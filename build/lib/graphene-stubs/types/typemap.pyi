from ..utils.get_unbound_function import get_unbound_function as get_unbound_function
from ..utils.str_converters import to_camel_case as to_camel_case
from .definitions import GrapheneEnumType as GrapheneEnumType, GrapheneGraphQLType as GrapheneGraphQLType, GrapheneInputObjectType as GrapheneInputObjectType, GrapheneInterfaceType as GrapheneInterfaceType, GrapheneObjectType as GrapheneObjectType, GrapheneScalarType as GrapheneScalarType, GrapheneUnionType as GrapheneUnionType
from .dynamic import Dynamic as Dynamic
from .enum import Enum as Enum
from .field import Field as Field
from .inputobjecttype import InputObjectType as InputObjectType
from .interface import Interface as Interface
from .objecttype import ObjectType as ObjectType
from .resolver import get_default_resolver as get_default_resolver
from .scalars import Boolean as Boolean, Float as Float, ID as ID, Int as Int, Scalar as Scalar, String as String
from .structures import List as List, NonNull as NonNull
from .union import Union as Union
from .utils import get_field_as as get_field_as
from graphql.type.typemap import GraphQLTypeMap
from typing import Any, Optional


def is_graphene_type(_type: Any) -> Any:
    ...


def resolve_type(resolve_type_func: Any, map: Any, type_name: Any, root: Any, info: Any) -> Any:
    ...


def is_type_of_from_possible_types(possible_types: Any, root: Any, info: Any) -> Any:
    ...


class TypeMap(GraphQLTypeMap):
    auto_camelcase: Any = ...
    schema: Any = ...

    def __init__(self, types: Any, auto_camelcase: bool = ..., schema: Optional[Any] = ...) -> None:
        ...

    def reducer(self, map: Any, type: Any) -> Any: # type: ignore[override]
        ...

    def graphene_reducer(self, map: Any, type: Any) -> Any:
        ...

    def construct_scalar(self, map: Any, type: Any) -> Any:
        ...

    def construct_enum(self, map: Any, type: Any) -> Any:
        ...

    def construct_objecttype(self, map: Any, type: Any) -> Any:
        ...

    def construct_interface(self, map: Any, type: Any) -> Any:
        ...

    def construct_inputobjecttype(self, map: Any, type: Any) -> Any:
        ...

    def construct_union(self, map: Any, type: Any) -> Any:
        ...

    def get_name(self, name: Any) -> Any:
        ...

    def construct_fields_for_type(self, map: Any, type: Any, is_input_type: bool = ...) -> Any:
        ...

    def get_resolver_for_type(self, type: Any, name: Any, default_value: Any) -> Any:
        ...

    def get_field_type(self, map: Any, type: Any) -> Any:
        ...
