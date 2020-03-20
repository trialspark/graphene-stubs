# pylint: disable=no-name-in-module
from dataclasses import dataclass
from itertools import chain
import re
from typing import Optional, Callable, Type as TypeOf, List, Any, Dict, cast, Union, Tuple

from mypy.checker import TypeChecker
from mypy.checkmember import analyze_member_access
from mypy.nodes import AssignmentStmt, Decorator, CallExpr, Argument, TypeInfo, FuncDef, Statement, ClassDef, \
    TupleExpr, Expression, MypyFile, ExpressionStmt, MemberExpr, Var, SymbolTableNode, MDEF, CastExpr, \
    RefExpr, NameExpr
from mypy.options import Options
from mypy.plugin import Plugin, AttributeContext, ClassDefContext, SemanticAnalyzerPluginInterface
from mypy.state import strict_optional_set
from mypy.subtypes import is_subtype, is_equivalent
from mypy.types import AnyType, CallableType, Instance, TypeOfAny, Type, NoneType, UnionType, UnboundType

RESOLVER_PREFIX = 'resolve_'

GRAPHENE_ARGUMENT_NAME = 'graphene.types.argument.Argument'
GRAPHENE_ENUM_META_NAME = 'graphene.types.enum.EnumMeta'
GRAPHENE_ENUM_NAME = 'graphene.types.enum.Enum'
GRAPHENE_LIST_NAME = 'graphene.types.structures.List'
GRAPHENE_NONNULL_NAME = 'graphene.types.structures.NonNull'
GRAPHENE_OBJECTTYPE_NAME = 'graphene.types.objecttype.ObjectType'
GRAPHENE_SCHEMA_NAME = 'graphene.types.schema.Schema'
GRAPHENE_FIELD_NAME = 'graphene.types.field.Field'
GRAPHENE_SCALAR_NAME = 'graphene.types.scalars.Scalar'
GRAPHENE_UNMOUNTED_TYPE_NAME = 'graphene.types.unmountedtype.UnmountedType'
GRAPHENE_STRUCTURE_NAME = 'graphene.types.structures.Structure'
GRAPHENE_INTERFACE_NAME = 'graphene.types.interface.Interface'

NOOP_ATTR_NAME = '__graphene_plugin_noop__'


def _type_is_a(type_info: TypeInfo, other_fullname: Union[str, Tuple[str, ...]]) -> bool:
    """
    Checks if the given type (`type_info`) is some other type (`other_fullname`) or if the other type
    exists somewhere in its ancestry.
    """
    all_fullnames = {other_fullname} if isinstance(other_fullname, str) else set(other_fullname)
    if type_info.fullname in all_fullnames:
        return True

    return any(_type_is_a(base_type_info.type, other_fullname) for base_type_info in type_info.bases)


def _add_var_to_class(name: str, typ: Type, info: TypeInfo) -> None:
    """
    Add a variable with given name and type to the symbol table of a class.
    This also takes care about setting necessary attributes on the variable node.
    """

    var = Var(name)
    var.info = info
    var._fullname = f'{info.fullname}.{name}'  # pylint: disable=protected-access
    var.type = typ
    info.names[name] = SymbolTableNode(MDEF, var)


def _add_attr_access_to_module(module: MypyFile, class_info: TypeInfo, attr_name: str) -> None:
    """
    Adds a statement that accesses a given `attr_name` of a type (specified via `class_info`) as the last
    statement in a `module`.
    """

    module.defs.append(
        ExpressionStmt(
            MemberExpr(
                CastExpr(NameExpr('None'), Instance(class_info, [])),
                attr_name,
            )
        )
    )


def _get_type_mismatch_error_message(arg_name: str, *, graphene_type: Type, resolver_type: Type) -> str:
    return f'Parameter "{arg_name}" has type {resolver_type}, expected type {graphene_type}'


def _is_field_declaration(statement: Statement) -> bool:
    """
    Given some `ClassDef` statement, figure out if it is a `Field()` declaration
    """

    if not isinstance(statement, AssignmentStmt):
        return False

    call_expr = statement.rvalue
    if not isinstance(call_expr, CallExpr):
        return False

    callee = call_expr.callee
    if not isinstance(callee, RefExpr):
        return False

    callee_node = callee.node
    if not isinstance(callee_node, TypeInfo):
        return False

    return _type_is_a(callee_node, GRAPHENE_FIELD_NAME)


def _get_func_def(expression: Statement) -> Optional[FuncDef]:
    """
    Given some `Statement`, return a `FuncDef` if it is a `FuncDef`, the `FuncDef` it wraps if it is a `Decorator`,
    or `None` if it is neither.
    """

    if isinstance(expression, FuncDef):
        return expression

    if isinstance(expression, Decorator):
        return expression.func

    return None


def _get_func_def_ret_type(semanal: SemanticAnalyzerPluginInterface, funcdef: FuncDef) -> Type:
    """
    Given a `FuncDef`, return its return-type (or `Any`)
    """

    ret_type = None
    type_ = funcdef.type

    if isinstance(type_, CallableType):
        ret_type = type_.ret_type

    if isinstance(ret_type, UnboundType):
        ret_type = semanal.anal_type(ret_type)

    return ret_type or AnyType(TypeOfAny.unannotated)


def _get_python_type_from_graphene_field_first_argument(
    semanal: SemanticAnalyzerPluginInterface, argument: Expression, *, covariant: bool, nullable: bool
) -> Type:
    """
    Given the first argument to a `Field()`/`Argument()`, return the corresponding runtime (python) type. E.g.:

    * `String` => `Union[builtins.str, None]`
    * `NonNull(String)` => `builtins.str`
    * `NonNull(List(Integer))` => `builtins.list[Union[builtins.int, None]]`
    """

    type_: Optional[Type] = None

    if isinstance(argument, RefExpr) and isinstance(argument.node, TypeInfo):
        # This is just a plain graphene type that doesn't wrap anything (i.e `String`, `MyObjectType`,
        # **not** `List(String)`, `NonNull(MyObjectType), etc.)``
        is_scalar = _type_is_a(argument.node, GRAPHENE_SCALAR_NAME)
        is_object = _type_is_a(argument.node, (GRAPHENE_OBJECTTYPE_NAME, GRAPHENE_INTERFACE_NAME))
        is_enum = _type_is_a(argument.node, GRAPHENE_ENUM_NAME)

        if is_scalar:
            # This is some scalar (either a builtin one like `String` or a user-defined one)
            parse_value_type = argument.node.names.get('parse_value')
            ret_type: Optional[Type] = None
            # Figure out the runtime type of the scalar by looking at the return value of its `parse_value` method
            if parse_value_type and isinstance(parse_value_type.type, CallableType):
                ret_type = parse_value_type.type.ret_type
            elif (
                parse_value_type
                and isinstance(parse_value_type.node, Decorator)
                and isinstance(parse_value_type.node.func.type, CallableType)
            ):
                ret_type = parse_value_type.node.func.type.ret_type

            if ret_type:
                type_ = ret_type

        elif is_object:
            # This is an `ObjectType`/`Interface` child-class, so get the runtime type by looking at the type arg passed
            # to `ObjectType[]`/`Interface[]`
            type_ = _get_graphene_subclass_runtime_type(argument.node)

        elif is_enum:
            # This is an `Enum` child-class, which means its value will just be a `str` at runtime
            symbol_table_node = semanal.lookup_fully_qualified('builtins.str')
            assert isinstance(symbol_table_node.node, TypeInfo)
            type_ = Instance(symbol_table_node.node, [])

    elif isinstance(argument, CallExpr) and isinstance(argument.callee, RefExpr) and argument.args:
        # This is something being called (e.g. `List()`/`NonNull()`)

        if argument.callee.fullname == GRAPHENE_LIST_NAME:
            # This is a `List()`

            # Use a `Sequence` if we want type-checking to be covariant
            iterable_type_name = 'typing.Sequence' if covariant else 'builtins.list'

            # Recursively call to figure out the runtime type of the first arg to `List()` and wrap the result
            # in a `builtins.list`/`typing.Sequence`.
            symbol_table_node = semanal.lookup_fully_qualified(iterable_type_name)
            assert isinstance(symbol_table_node.node, TypeInfo)
            type_ = Instance(
                symbol_table_node.node,
                [_get_python_type_from_graphene_field_first_argument(
                    semanal, argument.args[0], covariant=covariant, nullable=True
                )],
            )

        elif argument.callee.fullname == GRAPHENE_NONNULL_NAME:
            # This is a `NonNull()`

            # Recursively call to figure out the runtime type of the first arg to `NonNull()` but set the
            # `nullable` flag to `False` so that the resulting type will **not** be wrapped in a
            # `Union[X, None]`
            return _get_python_type_from_graphene_field_first_argument(
                semanal, argument.args[0], covariant=covariant, nullable=False
            )

    if isinstance(type_, UnboundType):
        type_ = semanal.anal_type(type_)

    if not type_:
        return AnyType(TypeOfAny.unannotated)

    if nullable:
        return UnionType((type_, NoneType()))

    return type_


def _get_argument_value_expression(call: CallExpr, arg_name: str) -> Optional[Expression]:
    """
    Given some call, return the expression of one of its arguments' values, or `None` if no
    argument with that name exists in the call. E.g.:

    `foo(hello='world', iam='joe dart')`, `'iam'` => `'joe dart'`
    """
    arg_index = call.arg_names.index(arg_name) if arg_name in call.arg_names else None
    if arg_index is not None:
        return call.args[arg_index]

    return None


def _is_default_value_kwarg_not_none(expression: CallExpr) -> bool:
    """
    Given an `Argument()` expression, return a bool indicating if a `default_value` kwarg was passed, and if
    it was passed some non-`None` literal. E.g.:

    * `Argument(String)` => `False`
    * `Argument(String, default_value=None)` => `False`
    * `Argument(String, default_value='foo')` => `True`
    """

    default_value_expression = _get_argument_value_expression(expression, 'default_value')
    if not default_value_expression:
        return False

    if isinstance(default_value_expression, NameExpr) and default_value_expression.fullname == 'builtins.None':
        return False

    return True


def _is_required_kwarg_true(expression: CallExpr) -> bool:
    """
    Given a `Field()`/`Argument()` expression, return a bool indicating if a `required` kwarg was passed, and if
    it was passed the literal `True`. E.g.:

    * `Field(String)` => `False`
    * `Field(String, required=False)` => `False`
    * `Field(String, required=True)` => `True`
    * `Field(String, required=some_computation())` => `False`
    """

    required_expression = _get_argument_value_expression(expression, 'required')
    return isinstance(required_expression, NameExpr) and required_expression.fullname == 'builtins.True'

def _get_python_type_from_graphene_field_instantiation(
    semanal: SemanticAnalyzerPluginInterface, expression: Expression, *, covariant: bool
) -> Type:
    """
    Given an `Field()` definition, return the python type that the resolver should return at runtime.

    E.g. `Field(List(NonNull(String)), required=True) -> builtins.list[builtins.str]`
    """

    if not isinstance(expression, CallExpr):
        return AnyType(TypeOfAny.unannotated)

    if not isinstance(expression.callee, RefExpr) or expression.callee.fullname != GRAPHENE_FIELD_NAME:
        return AnyType(TypeOfAny.unannotated)

    if not expression.args:
        return AnyType(TypeOfAny.unannotated)

    return _get_python_type_from_graphene_field_first_argument(
        semanal, expression.args[0], covariant=covariant, nullable=not _is_required_kwarg_true(expression)
    )


def _get_python_type_from_graphene_argument_instantiation(
    semanal: SemanticAnalyzerPluginInterface, expression: CallExpr
) -> Type:
    """
    Given an `Argument()` defintion, return the python type that will be passed to the resolver at runtime.

    E.g. `Argument(List(NonNull(String)), required=True) -> builtins.list[builtins.str]`
    """

    assert isinstance(expression.callee, RefExpr) and isinstance(expression.callee.node, TypeInfo)

    graphene_type: Optional[Expression] = None
    if _type_is_a(expression.callee.node, GRAPHENE_UNMOUNTED_TYPE_NAME):
        # What we actually have here is some graphene type being instantiated directly
        # (e.g. `foo = String(required=True)` instead of `foo = Argument(String, required=True)`)
        # In this case, the type of the arg is actually the thing being instantiated, not the first arg
        if _type_is_a(expression.callee.node, GRAPHENE_STRUCTURE_NAME):
            # This is a Graphene `Structure` (`List()`/`NonNull()`). Graphene `Structure`s wrap another
            # type, so we actually want to treat the entire `CallExpr` as the thing to look at
            # (e.g. `List(String)`) and not just the callee (e.g. `List`).
            graphene_type = expression
        else:
            # This is just a regular `UnmountedType`
            graphene_type = expression.callee
    elif expression.args:
        # We have an `Argument()` instantation. Get the type from the first argument
        graphene_type = expression.args[0]

    if not graphene_type:
        return AnyType(TypeOfAny.unannotated)

    is_required = _is_required_kwarg_true(expression)
    has_non_null_default_value = _is_default_value_kwarg_not_none(expression)

    return _get_python_type_from_graphene_field_first_argument(
        semanal, graphene_type, covariant=False, nullable=not is_required and not has_non_null_default_value
    )


def _get_graphene_subclass_runtime_type(type_info: TypeInfo) -> Type:
    """
    Get the type that an `ObjectType`/`Interface` child class should serialize at runtime (via the type argument passed
    to `ObjectType`/`Interface`) (e.g. `ObjectType[Foo] -> Foo`)
    """

    graphene_base = next(
        base for base in type_info.bases if base.type.fullname in (GRAPHENE_OBJECTTYPE_NAME, GRAPHENE_INTERFACE_NAME)
    )
    # Note: even if no type argument was passed to `ObjectType`/`Interface` when it was sub-classed, there will still be
    # an item in the `args` list below. It will just be `Any`.
    return graphene_base.args[0]


@dataclass
class FieldArgumentInfo:
    """
    Contains information about one of a field declarations' arguments, including:

    * name: the name of the argument
    * type: the type that will be passed to the field's resolver at runtime for this argument
    """

    name: str
    type: Type

    @classmethod
    def for_expression(
        cls, semanal: SemanticAnalyzerPluginInterface, name: str, expression: CallExpr
    ) -> 'FieldArgumentInfo':
        type_ = _get_python_type_from_graphene_argument_instantiation(semanal, expression)
        return cls(
            name=name,
            type=type_,
        )


@dataclass
class FieldInfo:
    """
    Contains information about a field declaration on a graphene `ObjectType` child class, including:

    * name: the name of the field
    * type: the type the field's resolver must return at runtime
    * arguments: a Dict of argument name to `FieldArgumentInfo` for each of the field's arguments
    * context: the field's defintion's AST
    """

    name: str
    type: Type
    arguments: Dict[str, FieldArgumentInfo]
    context: AssignmentStmt

    @staticmethod
    def _arguments_for_expression(
        semanal: SemanticAnalyzerPluginInterface, expression: Expression
    ) -> List[FieldArgumentInfo]:
        arguments: List[FieldArgumentInfo] = []

        if (
            not isinstance(expression, CallExpr)
            or not isinstance(expression.callee, RefExpr)
            or not expression.callee.fullname == GRAPHENE_FIELD_NAME
        ):
            return []

        for arg_name, arg in list(zip(expression.arg_names, expression.args))[1:]:
            if (
                arg_name
                and isinstance(arg, CallExpr)
                and isinstance(arg.callee, RefExpr)
                and isinstance(arg.callee.node, TypeInfo)
            ):
                if (
                    arg.callee.fullname == GRAPHENE_ARGUMENT_NAME
                    or _type_is_a(arg.callee.node, GRAPHENE_UNMOUNTED_TYPE_NAME)
                ):
                    arguments.append(FieldArgumentInfo.for_expression(semanal, arg_name, arg))

        return arguments

    @classmethod
    def for_statement(cls, semanal: SemanticAnalyzerPluginInterface, statement: AssignmentStmt) -> 'FieldInfo':
        name_expr = statement.lvalues[0]
        arguments = cls._arguments_for_expression(semanal, statement.rvalue)

        assert isinstance(name_expr, NameExpr)
        return cls(
            name=name_expr.name,
            type=_get_python_type_from_graphene_field_instantiation(semanal, statement.rvalue, covariant=True),
            arguments={argument.name: argument for argument in arguments},
            context=statement,
        )


@dataclass
class ResolverArgumentInfo:
    """
    Contains information about one of a resolver method's keyword arguments, including:

    * name: the name of the field the resolver resolves
    * type: the type of the argument (via a type annotation)
    * context: the argument's defintion's AST
    """

    name: str
    type: Type
    context: Argument

    @classmethod
    def for_argument(cls, semanal: SemanticAnalyzerPluginInterface, argument: Argument) -> 'ResolverArgumentInfo':
        type_annotation = semanal.anal_type(argument.type_annotation) if argument.type_annotation else None
        return cls(
            name=argument.variable.name,
            type=type_annotation or AnyType(TypeOfAny.unannotated),
            context=argument,
        )


@dataclass
class ResolverInfo:
    """
    Contains information about the defintion of a resolver method on a Graphene `ObjectType` child class, including:

    * field_name: The name of the field the resolver resolves
    * return_type: The return type of the resolver method
    * previous_argument: Information about the "previous" argument of a resolver (a.k.a the first positional argument
      of a resolver)
    * arguments: Dict of argument name to `ResolverArgumentInfo` for each of the resolver's keyword arguments
    * context: The resolver's defintion's AST
    """

    field_name: str
    return_type: Type
    previous_argument: ResolverArgumentInfo
    arguments: Dict[str, ResolverArgumentInfo]
    context: FuncDef

    @classmethod
    def for_funcdef(cls, semanal: SemanticAnalyzerPluginInterface, funcdef: FuncDef) -> 'ResolverInfo':
        field_name = re.sub(r'^resolve_', '', funcdef.name)
        arguments = (ResolverArgumentInfo.for_argument(semanal, argument) for argument in funcdef.arguments[2:])

        return cls(
            field_name=field_name,
            arguments={argument.name: argument for argument in arguments},
            return_type=_get_func_def_ret_type(semanal, funcdef),
            context=funcdef,
            previous_argument=ResolverArgumentInfo.for_argument(semanal, funcdef.arguments[0]),
        )


@dataclass
class BaseObjectInfo:
    """
    Defines common attributes that both `ObjectType`s and `Interface`s share.
    """

    name: str
    fields: Dict[str, FieldInfo]
    resolvers: Dict[str, ResolverInfo]
    runtime_type: Type

    @classmethod
    def _resolvers_for_classdef(
        cls, semanal: SemanticAnalyzerPluginInterface, classdef: ClassDef
    ) -> List[ResolverInfo]:
        resolvers: List[ResolverInfo] = []

        for statement in classdef.defs.body:
            funcdef = _get_func_def(statement)
            if funcdef and funcdef.name.startswith(RESOLVER_PREFIX):
                resolvers.append(ResolverInfo.for_funcdef(semanal, funcdef))

        return resolvers

    @staticmethod
    def _fields_for_statements(
        semanal: SemanticAnalyzerPluginInterface, statements: List[Statement]
    ) -> List[FieldInfo]:
        fields: List[FieldInfo] = []

        for statement in statements:
            if _is_field_declaration(statement):
                assert isinstance(statement, AssignmentStmt)
                if isinstance(statement.lvalues[0], NameExpr):
                    fields.append(FieldInfo.for_statement(semanal, statement))

        return fields

    @classmethod
    def for_classdef(cls, semanal: SemanticAnalyzerPluginInterface, classdef: ClassDef) -> 'BaseObjectInfo':
        resolvers = {resolver.field_name: resolver for resolver in cls._resolvers_for_classdef(semanal, classdef)}
        fields = {field.name: field for field in cls._fields_for_statements(semanal, classdef.defs.body)}
        runtime_type = _get_graphene_subclass_runtime_type(classdef.info)

        return cls(
            name=classdef.name,
            fields=fields,
            resolvers=resolvers,
            runtime_type=runtime_type,
        )


@dataclass
class ObjectTypeInfo(BaseObjectInfo):
    """
    Contains information about the defintion of a Graphene `ObjectType` child class, including:

    * name: the name of the `ObjectType`
    * fields: A `dict` of field name to `FieldInfo` for each field defintion in the `ObjectType`
      (e.g. `some_field = Field(String, required=True, description='this is a thing')`)
    * resolvers: A `dict` of field name to `ResolverInfo` for each resolver method in the `ObjectType`
      (e.g. `def resolve_some_field(_: None, __: ResolveInfo) -> str: 'hello'`)
    * runtime_type: The type that this `ObjectType` serializes at runtime, specified via the passing an
      argument to `ObjectType` (e.g. `class MyObjectType(ObjectType[MyRuntimeType]): ...`)
    """

    @staticmethod
    def _interface_classdefs_for_meta_classdef(
        semanal: SemanticAnalyzerPluginInterface, classdef: ClassDef
    ) -> List[ClassDef]:
        for statement in classdef.defs.body:
            if (
                isinstance(statement, AssignmentStmt)
                and any(isinstance(lval, NameExpr) and lval.name == 'interfaces' for lval in statement.lvalues)
            ):
                if not isinstance(statement.rvalue, TupleExpr):
                    semanal.fail('"interfaces" attribute in Meta class must be a tuple type', statement)
                    return []

                # Loop through tuple and add defintions of graphene `Interface`s to the final list.
                interface_defs: List[ClassDef] = []
                for item in statement.rvalue.items:
                    if (
                        isinstance(item, RefExpr)
                        and isinstance(item.node, TypeInfo)
                        and isinstance(item.node.defn, ClassDef)
                    ):
                        interface_defs.append(item.node.defn)

                return interface_defs

        return []

    @classmethod
    def _interfaces_for_classdef(cls, semanal: SemanticAnalyzerPluginInterface, classdef: ClassDef) -> List[ClassDef]:
        for statement in classdef.defs.body:
            if isinstance(statement, ClassDef) and statement.name == 'Meta':
                return cls._interface_classdefs_for_meta_classdef(semanal, statement)

        return []

    @classmethod
    def _get_interface_fields(
        cls, semanal: SemanticAnalyzerPluginInterface, classdef: ClassDef
    ) -> Dict[str, FieldInfo]:
        interface_def_statements = list(
            chain(*(interface.defs.body for interface in cls._interfaces_for_classdef(semanal, classdef)))
        )

        return {field.name: field for field in cls._fields_for_statements(semanal, interface_def_statements)}

    @classmethod
    def for_classdef(cls, semanal: SemanticAnalyzerPluginInterface, classdef: ClassDef) -> 'ObjectTypeInfo':
        base_info = super().for_classdef(semanal, classdef)

        return cls(
            name=base_info.name,
            fields={**cls._get_interface_fields(semanal, classdef), **base_info.fields},
            resolvers=base_info.resolvers,
            runtime_type=base_info.runtime_type,
        )


@dataclass
class InterfaceInfo(BaseObjectInfo):
    """
    Contains information about the definition of a Graphene `Interface` child class, including:

    * name: the name of the `Interface`
    * fields: A `dict` of field name to `FieldInfo` for each field defintion in the `Interface`
      (e.g. `some_field = Field(String, required=True, description='this is a thing')`)
    * resolvers: A `dict` of field name to `ResolverInfo` for each resolver method in the `Interface`
      (e.g. `def resolve_some_field(_: None, __: ResolveInfo) -> str: 'hello'`)
    * runtime_type: The type that this `Interface` serializes at runtime, specified via the passing an
      argument to `Interface` (e.g. `class MyInterface(Interface[MyRuntimeType]): ...`)
    """

    @classmethod
    def for_classdef(cls, semanal: SemanticAnalyzerPluginInterface, classdef: ClassDef) -> 'InterfaceInfo':
        base_info = super().for_classdef(semanal, classdef)

        return cls(
            name=base_info.name,
            fields=base_info.fields,
            resolvers=base_info.resolvers,
            runtime_type=base_info.runtime_type,
        )


class GraphenePlugin(Plugin):
    def __init__(self, options: Options) -> None:
        super().__init__(options)

        self._graphene_objects: Dict[str, Union[ObjectTypeInfo, InterfaceInfo]] = {}

    def get_base_class_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        def collect_graphene_subclass(ctx: ClassDefContext) -> None:
            """
            Collect type information about graphene `ObjectType` child classes. This plugin is invoked
            during semantic analysis.
            """

            if not ctx.api.final_iteration:
                ctx.api.defer()
                return

            module = ctx.api.modules[ctx.cls.info.module_name]

            if _type_is_a(ctx.cls.info, GRAPHENE_OBJECTTYPE_NAME):
                self._graphene_objects[ctx.cls.info.fullname] = ObjectTypeInfo.for_classdef(ctx.api, ctx.cls)
            elif _type_is_a(ctx.cls.info, GRAPHENE_INTERFACE_NAME):
                self._graphene_objects[ctx.cls.info.fullname] = InterfaceInfo.for_classdef(ctx.api, ctx.cls)

            # Here is the fun hack. We want to type-check our `ObjectType`s at type-checking time, but
            # the `get_base_class_hook` only runs at semantic analysis time and as of now there is no
            # classdef hook that runs at type-checking time. To work around this, we do two things:
            #
            # * First, we add a dummy attribute to the `ObjectType` child class (__graphene_plugin_noop__)
            # * Then, we add some statements to the module's AST that effectively do this:
            #   `cast(MyObjectType, None).__graphene_plugin_noop__`
            #
            # Because mypy has a `get_attribute_hook` plugin hook that is invoked during type-checking time
            # we now can rely on that hook to perform our type-checking of the `ObjectType`.
            _add_var_to_class(NOOP_ATTR_NAME, NoneType(), ctx.cls.info)
            _add_attr_access_to_module(module, ctx.cls.info, NOOP_ATTR_NAME)

        if fullname in (GRAPHENE_OBJECTTYPE_NAME, GRAPHENE_INTERFACE_NAME):
            return collect_graphene_subclass

        return None

    def get_attribute_hook(self, fullname: str) -> Optional[Callable[[AttributeContext], Type]]:
        @strict_optional_set(True)
        def process_gql_schema(ctx: AttributeContext) -> Type:
            """
            Actually perform the type-checking logic for each graphene `ObjectType` child class.
            The plugin is invoked at type-checking time.
            """

            assert isinstance(ctx.type, Instance)
            object_info = self._graphene_objects[ctx.type.type.fullname]

            for field in object_info.fields.values():
                resolver = object_info.resolvers.get(field.name)

                # If no resolver function is defined, type-check the behavior of the graphene default resolver
                if not resolver:
                    if isinstance(object_info, InterfaceInfo):
                        # The default resolver doesn't apply to `Interface`s because the `ObjectType`s that implement
                        # them could have resolvers for their fields.
                        # TODO: Detect if any of an `Interface`'s `ObjectType`s do _not_ define their own resolver for
                        # this field. In that case, we _do_ want to type-check the default resolver.
                        continue

                    # Note: `analyze_member_access` will call `ctx.api.fail()` if the provided type doesn't have
                    # a member with the given name at all. So our code only needs to do the subtype check.
                    default_resolver_return_type = analyze_member_access(
                        field.name,
                        object_info.runtime_type,
                        field.context,
                        False,  # is_lvalue
                        False,  # is_super
                        False,  # is_operator
                        ctx.api.msg,
                        original_type=object_info.runtime_type,
                        chk=cast(TypeChecker, ctx.api),
                    )
                    if not is_subtype(default_resolver_return_type, field.type):
                        ctx.api.fail(
                            f'Field expects type {field.type} but {object_info.runtime_type}.{field.name} has type '
                            f'{default_resolver_return_type}',
                            field.context,
                        )
                    continue

                # Check that the resolver's "previous" (first) argument has the correct type
                if not is_equivalent(resolver.previous_argument.type, object_info.runtime_type):
                    ctx.api.fail(
                        _get_type_mismatch_error_message(
                            resolver.previous_argument.name,
                            graphene_type=object_info.runtime_type,
                            resolver_type=resolver.previous_argument.type,
                        ),
                        resolver.previous_argument.context,
                    )
                    continue

                # Check that the resolver returns the correct type
                if not is_subtype(resolver.return_type, field.type):
                    ctx.api.fail(
                        f'Resolver returns type {resolver.return_type}, expected type {field.type}',
                        resolver.context,
                    )
                    continue

                for field_argument in field.arguments.values():
                    resolver_argument = resolver.arguments.get(field_argument.name)

                    # Check that the resolver has an argument for each argument the `Field()` defines
                    if not resolver_argument:
                        ctx.api.fail(
                            f'Parameter "{field_argument.name}" of type {field_argument.type} is missing,'
                            ' but required in resolver definition',
                            resolver.context,
                        )
                        continue

                    # Check that the resolver's argument has the correct type annotation
                    if not is_equivalent(field_argument.type, resolver_argument.type):
                        ctx.api.fail(
                            _get_type_mismatch_error_message(
                                field_argument.name,
                                graphene_type=field_argument.type,
                                resolver_type=resolver_argument.type,
                            ),
                            resolver_argument.context,
                        )
                        continue

            # Check the every resolver function has a corresponding `Field()` defintion
            missing_field_names = set(object_info.resolvers.keys()) - set(object_info.fields.keys())
            for name in missing_field_names:
                if isinstance(object_info, InterfaceInfo) and name == 'type':
                    # This is not a field resolver. It is the special `Interface` resolver that determines which
                    # `ObjectType` to use at runtime.
                    continue

                resolver = object_info.resolvers[name]

                ctx.api.fail(f'No field with name "{resolver.field_name}" defined', resolver.context)
                continue

            return ctx.default_attr_type

        if fullname.endswith(NOOP_ATTR_NAME):
            return process_gql_schema

        return None


def plugin(_: str) -> TypeOf[GraphenePlugin]:
    return GraphenePlugin

def patch_object_type() -> None:
    """
    Patches `graphene.ObjectType` to make it indexable at runttime. This is necessary for it be
    generic at typechecking time.
    """
    # Lazily import graphene as it is actually an expensive thing to do and we don't want to slow down things at
    # type-checking time.
    from graphene import ObjectType  # pylint: disable=import-outside-toplevel


    ObjectTypeMetaclass = type(ObjectType)

    def __getitem__(cls: TypeOf[TypeOf[ObjectType]], _: Any) -> TypeOf[TypeOf[ObjectType]]:
        return cls

    ObjectTypeMetaclass.__getitem__ = __getitem__  # type: ignore
