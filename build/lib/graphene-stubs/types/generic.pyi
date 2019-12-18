from .scalars import Scalar as Scalar
from graphene.types.scalars import MAX_INT as MAX_INT, MIN_INT as MIN_INT
from typing import Any


class GenericScalar(Scalar):
    @staticmethod
    def identity(value: Any) -> Any:
        ...

    serialize: Any = ...
    parse_value: Any = ...

    @staticmethod
    def parse_literal(ast: Any) -> Any:
        ...
