from .scalars import Scalar as Scalar
from typing import Any


class UUID(Scalar):
    @staticmethod
    def serialize(uuid: Any) -> Any:
        ...

    @staticmethod
    def parse_literal(node: Any) -> Any:
        ...

    @staticmethod
    def parse_value(value: Any) -> Any:
        ...
