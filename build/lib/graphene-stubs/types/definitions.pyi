from graphql import GraphQLEnumType, GraphQLInputObjectType, GraphQLInterfaceType, GraphQLObjectType, GraphQLScalarType, GraphQLUnionType
from typing import Any


class GrapheneGraphQLType:
    graphene_type: Any = ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class GrapheneInterfaceType(GrapheneGraphQLType, GraphQLInterfaceType):
    ...


class GrapheneUnionType(GrapheneGraphQLType, GraphQLUnionType):
    ...


class GrapheneObjectType(GrapheneGraphQLType, GraphQLObjectType):
    ...


class GrapheneScalarType(GrapheneGraphQLType, GraphQLScalarType):
    ...


class GrapheneEnumType(GrapheneGraphQLType, GraphQLEnumType):
    ...


class GrapheneInputObjectType(GrapheneGraphQLType, GraphQLInputObjectType):
    ...
