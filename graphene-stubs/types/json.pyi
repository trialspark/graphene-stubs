from .scalars import Scalar as Scalar
from typing import Any, Dict


class JSONString(Scalar):
    @staticmethod
    def serialize(dt: Any) -> Any:
        ...

    @staticmethod
    def parse_literal(node: Any) -> Any:
        ...

    @staticmethod
    def parse_value(value: Any) -> dict:
        ...
