# pylint: disable=no-name-in-module
from dataclasses import dataclass
from typing import Optional, Callable, Type as TypeOf, List, Union, Any

from graphene import ObjectType
from mypy.plugin import Plugin, ClassDefContext
from mypy.types import AnyType, CallableType, UnboundType, Instance, TypeOfAny, Type, NoneType, UnionType
from mypy.nodes import AssignmentStmt, Decorator, CallExpr, Argument, TypeInfo, FuncDef, EllipsisExpr, StrExpr, \
    Statement, ClassDef, SymbolNode, TupleExpr

RESOLVER_PREFIX = 'resolve_'
GRAPHENE_ARGUMENT_NAME = 'graphene.types.argument.Argument'
GRAPHENE_ENUM_META_NAME = 'graphene.types.enum.EnumMeta'
GRAPHENE_ENUM_NAME = 'graphene.types.enum.Enum'
GRAPHENE_LIST_NAME = 'graphene.types.structures.List'
GRAPHENE_NONNULL_NAME = 'graphene.types.structures.NonNull'
GRAPHENE_OBJECTTYPE_NAME = 'graphene.types.objecttype.ObjectType'


@dataclass
class ArgumentNode:
    name: str
    type: Type
    context: Argument

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ArgumentNode):
            return False
        return self.name == other.name

    def __ne__(self, other: object) -> bool:
        return not (self == other)


@dataclass
class TypeNodeInfo:
    name: str
    return_type: Type
    arguments: List[ArgumentNode]
    context: Union[FuncDef, AssignmentStmt, Optional[SymbolNode]]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeNodeInfo):
            return False
        return self.name == other.name

    def __ne__(self, other: object) -> bool:
        return not (self == other)


def create_resolver_type(ctx: ClassDefContext, resolver_node: Union[Decorator, FuncDef]) -> 'TypeNodeInfo':
    name = resolver_node.name[len(RESOLVER_PREFIX):]  # Chop off the beginning of the name for easier matching later
    if isinstance(resolver_node, FuncDef):
        func_def = resolver_node
    if isinstance(resolver_node, Decorator):
        func_def = resolver_node.func
    return_type = (
        ctx.api.anal_type(func_def.type.ret_type)  # type: ignore[attr-defined, union-attr]
        if func_def.type.ret_type  # type: ignore[attr-defined, union-attr]
        else None
    )
    return_type = return_type or AnyType(TypeOfAny.unannotated)
    argument_list: List['ArgumentNode'] = []
    for argument_node in func_def.arguments:
        argument_type = ctx.api.anal_type(argument_node.type_annotation) if argument_node.type_annotation else None
        argument_type = argument_type or AnyType(TypeOfAny.unannotated)
        arg_name = argument_node.variable.name
        argument_list.append(ArgumentNode(name=arg_name, type=argument_type, context=argument_node))
    return TypeNodeInfo(name=name, return_type=return_type, arguments=argument_list, context=func_def)


def wrap_in_nonnull(python_type: Optional[Type], non_null: bool) -> Optional[Type]:
    if not python_type or isinstance(python_type, AnyType) or non_null:
        return python_type

    return UnionType((python_type, NoneType()))


def wrap_in_list(ctx: ClassDefContext, python_type: Optional[Type]) -> Optional[Type]:
    if not python_type or isinstance(python_type, AnyType):
        return python_type
    return ctx.api.named_type('list', args=[python_type])


def get_python_type_from_graphene_type( # pylint: disable=too-many-branches,too-many-return-statements
    ctx: ClassDefContext,
    graphene_types: List[TypeInfo],
    arg_names: Optional[List[str]] = None,
    non_null: bool = False,
) -> Type:
    if arg_names is None:
        arg_names = []

    if not non_null and len(graphene_types) == len(arg_names):
        # Check extra conditions that could make this attribute non-nullable.

        if 'default_value' in arg_names:
            # If default_value isn't None, then this type isn't nullable.
            default_value_arg_value = list(zip(graphene_types, arg_names))[arg_names.index('default_value')][0]
            if not (
                hasattr(default_value_arg_value, 'fullname') and default_value_arg_value.fullname == 'builtins.None'
            ):
                non_null = True

        if 'required' in arg_names:
            # If required is True, then this type isn't nullable.
            required_arg_value = list(zip(graphene_types, arg_names))[arg_names.index('required')][0]
            if (hasattr(required_arg_value, 'fullname') and required_arg_value.fullname == 'builtins.True'):
                non_null = True

    graphene_type = graphene_types[0]
    if isinstance(graphene_type, StrExpr):
        return AnyType(TypeOfAny.explicit)  # TODO: Look up the name of graphene_type.value with the api?
    # if isinstance(graphene_type, NameExpr):
    #     graphene_type = graphene_type.node

    if isinstance(graphene_type, CallExpr):
        # This appears to be a graphene type instatiation.
        if not hasattr(graphene_type, 'callee'):
            # TODO: Figure out the None case (starargs?) AND check this is still happening
            return AnyType(TypeOfAny.explicit)  # TODO: Improve this by using actual types
        if graphene_type.callee.fullname == GRAPHENE_ARGUMENT_NAME:
            return get_python_type_from_graphene_type(ctx, graphene_type.args, graphene_type.arg_names)
        if graphene_type.callee.fullname == GRAPHENE_NONNULL_NAME:
            return get_python_type_from_graphene_type(ctx, graphene_type.args, non_null=True)
        if graphene_type.callee.fullname == GRAPHENE_LIST_NAME:
            return wrap_in_nonnull(
                wrap_in_list(ctx, get_python_type_from_graphene_type(ctx, graphene_type.args)),
                non_null,
            )
        return graphene_type.callee.name

    if (
        hasattr(graphene_type, 'node')  \
        and hasattr(graphene_type.node, 'names')  # type: ignore[attr-defined]
        and 'parse_value' in graphene_type.node.names  # type: ignore[attr-defined]
    ):
        # This is a scalar type.
        # Look at the parse_value method on a Scalar class and figure out its
        # return type, or default to Any.
        current_type = graphene_type.node['parse_value'].type  # type: ignore[attr-defined]
        if current_type is None:
            current_node = graphene_type.node['parse_value'].node  # type: ignore[attr-defined]
            if isinstance(current_node, Decorator):
                # This is likely a static method.
                current_type = current_node.func.type
                # if isinstance(current_type.ret_type, AnyType):
                #     return 'Any'
                # return_type_name = current_type.ret_type.name
            else:
                # I don't know what this is, let's just return Any.
                return AnyType(TypeOfAny.explicit)

        return_type: Optional[Type] = None
        if isinstance(current_type, CallableType):
            if isinstance(current_type.ret_type, AnyType):
                return AnyType(TypeOfAny.explicit)
            if isinstance(current_type.ret_type, Instance):
                return_type = current_type.ret_type
            elif isinstance(current_type.ret_type, UnboundType):
                return_type = ctx.api.anal_type(current_type.ret_type)  # type: ignore[attr-defined]
        elif current_type.is_type_obj():
            return_type = Instance(current_type.type_object(), args=[])

    elif hasattr(graphene_type, 'node') and graphene_type.node is not None:  # type: ignore[attr-defined]
        # Check for Enum types.
        graphene_type_node = graphene_type.node  # type: ignore[attr-defined]
        if hasattr(graphene_type_node, 'bases') and \
        GRAPHENE_ENUM_NAME in [base.type.fullname for base in graphene_type_node.bases]:
            return_type = ctx.api.named_type('str')
        else:
            return AnyType(TypeOfAny.explicit)
    else:
        # TODO: Come up with better fallback behavior.
        return AnyType(TypeOfAny.explicit)
    return wrap_in_nonnull(return_type, non_null) or AnyType(TypeOfAny.unannotated)


def create_attribute_type(ctx: ClassDefContext, attribute_node: AssignmentStmt) -> Optional['TypeNodeInfo']:
    # Collect type info about an  attribute on graphene ObjectType classes,
    # e.g. `attribute = Field(String, match_cookie=Argument(List(NonNull(Float))))`
    if isinstance(attribute_node.rvalue, EllipsisExpr):
        # This is inside a stub, there's nothing to do.
        return None
    if not hasattr(attribute_node.rvalue, 'args'):
        # This is not a Field or Argument instantiation.
        return None

    # `<attribute> = Field(String, match_cookie=Argument(List(NonNull(Float))))`
    name = attribute_node.lvalues[0].name  # type: ignore[attr-defined]
    # `attribute = Field(<String>, <match_cookie=Argument(List(NonNull(Float)))>)`
    argument_nodes = attribute_node.rvalue.args  # type: ignore[attr-defined]
    if not argument_nodes:
        return None

    argument_node_names = attribute_node.rvalue.arg_names  # type: ignore[attr-defined]
    return_type = get_python_type_from_graphene_type(ctx, argument_nodes)

    argument_list: List['ArgumentNode'] = []
    names_to_nodes = zip(argument_node_names[1:], argument_nodes[1:])

    for argument_name, argument_node in names_to_nodes:
        if argument_name in ['description', 'required', 'default_value', 'deprecation_reason']:
            continue
        python_type = get_python_type_from_graphene_type(ctx, [argument_node], argument_node_names)
        argument_list.append(ArgumentNode(name=argument_name, type=python_type, context=argument_node))

    return TypeNodeInfo(
        name=name,
        return_type=return_type,
        arguments=argument_list,
        context=attribute_node,
    )

def are_types_equal(left: Type, right: Type) -> bool:
    if isinstance(left, AnyType) or isinstance(right, AnyType):
        return True
    return left == right


def get_metaclass_attribute_types(class_body: List[Statement],
                                  ctx: ClassDefContext) -> Optional[List[Optional[TypeNodeInfo]]]:
    # Weakly support interfaces.
    interface_attributes: List[Optional[TypeNodeInfo]] = []

    meta_classes = [
        attribute for attribute in class_body if isinstance(attribute, ClassDef) and attribute.name == 'Meta'
    ]
    interfaces: List[AssignmentStmt] = []
    if meta_classes:
        meta_class_body = meta_classes[0].defs.body
        interfaces = [
            attribute for attribute in meta_class_body
            if isinstance(attribute, AssignmentStmt) \
            and attribute.lvalues[0].name == 'interfaces' # type: ignore[attr-defined]
        ]

    if not interfaces:
        return interface_attributes

    tuple_expr = interfaces[0].rvalue
    if not isinstance(tuple_expr, TupleExpr):
        not_a_tuple_error_message = '"interfaces" attribute in Meta class must be a tuple type'
        if hasattr(tuple_expr, 'line'):  # This unknown node type can be used as context for an error
            ctx.api.fail(not_a_tuple_error_message, tuple_expr)
        else:
            ctx.api.fail(not_a_tuple_error_message, tuple_expr)
        return interface_attributes

    for tuple_item in tuple_expr.items:
        tuple_item_node = tuple_item.node  # type: ignore[attr-defined]
        if not tuple_item_node:
            return None
        interface_class_body = tuple_item_node.defn.defs.body  # TODO: Maybe make this safer
        interface_attributes.extend([
            create_attribute_type(ctx, interface_attribute)
            for interface_attribute in interface_class_body
            if isinstance(interface_attribute, AssignmentStmt)
        ])

    return interface_attributes


def get_type_mismatch_error_message(arg_name: str, *, graphene_type: Type, resolver_type: Type) -> str:
    return f'Parameter "{arg_name}" has type {resolver_type}, expected type {graphene_type}'


class GraphenePlugin(Plugin):
    @staticmethod
    def get_base_class_hook(fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        def resolver_and_attribute_type_check(ctx: ClassDefContext) -> None:
            class_body = ctx.cls.defs.body
            class_bases = ctx.cls.info.bases
            objecttype_base = next(
                (base for base in class_bases if base.type.fullname == GRAPHENE_OBJECTTYPE_NAME),
                None,
            )

            if not objecttype_base:
                return

            interface_attributes = get_metaclass_attribute_types(class_body, ctx)
            if interface_attributes is None:
                ctx.api.defer()
                return

            # TODO: Improve performance by only getting type info for attributes that have
            # names matching resolvers.
            runtime_type = objecttype_base.args[0]
            attributes_or_none = [
                create_attribute_type(ctx, attribute_node)
                for attribute_node in class_body
                if isinstance(attribute_node, AssignmentStmt)
            ] + interface_attributes
            attributes = [
                attribute_or_none for attribute_or_none in attributes_or_none if attribute_or_none is not None
            ]

            resolvers = [ # TODO: Maybe use dicts to increase comparison speed
                create_resolver_type(ctx, resolver_node)
                for resolver_node in class_body
                # The check for Decorator assumes we're using `staticmethod`s.
                if isinstance(resolver_node, (Decorator, FuncDef)) and resolver_node.name.startswith(RESOLVER_PREFIX)
            ]

            for resolver in resolvers:
                matching_attributes = [attribute for attribute in attributes if attribute == resolver]
                assert resolver.context is not None
                if not matching_attributes:
                    ctx.api.fail(f'No field with name "{resolver.name}" defined', resolver.context)
                    continue

                previous_object_argument = resolver.arguments[0]
                if not are_types_equal(previous_object_argument.type, runtime_type):
                    ctx.api.fail(
                            get_type_mismatch_error_message(
                                previous_object_argument.name,
                                graphene_type=runtime_type,
                                resolver_type=previous_object_argument.type,
                            ),
                        previous_object_argument.context
                    )
                    continue

                # Assume there's only one match, but if there is more than one, compare against the last one defined.
                matching_attribute = matching_attributes[-1]
                for arg in matching_attribute.arguments:
                    matching_resolver_arguments = [argument for argument in resolver.arguments if argument == arg]
                    if not matching_resolver_arguments:
                        ctx.api.fail(
                            f'Parameter "{arg.name}" of type {arg.type} is missing,'
                            ' but required in resolver definition', resolver.context
                        )
                        continue

                    matching_resolver_argument = matching_resolver_arguments[0]
                    if not are_types_equal(matching_resolver_argument.type, arg.type):
                        ctx.api.fail(
                            get_type_mismatch_error_message(
                                matching_resolver_argument.name,
                                graphene_type=arg.type,
                                resolver_type=matching_resolver_argument.type,
                            ),
                            matching_resolver_argument.context,
                        )

        if GRAPHENE_OBJECTTYPE_NAME in fullname:  # TODO: Use ==
            return resolver_and_attribute_type_check

        return None


def plugin(_: str) -> TypeOf[GraphenePlugin]:
    return GraphenePlugin

def patch_object_type() -> None:
    """
    Patches `graphene.ObjectType` to make it indexable at runttime. This is necessary for it be
    generic at typechecking time.
    """
    ObjectTypeMetaclass = type(ObjectType)

    def __getitem__(cls: TypeOf[TypeOf[ObjectType]], _: Any) -> TypeOf[TypeOf[ObjectType]]:
        return cls

    ObjectTypeMetaclass.__getitem__ = __getitem__  # type: ignore
