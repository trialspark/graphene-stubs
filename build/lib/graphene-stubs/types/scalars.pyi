from .base import BaseOptions as BaseOptions, BaseType as BaseType
from .unmountedtype import UnmountedType as UnmountedType
from typing import Any, Optional, Callable


class ScalarOptions(BaseOptions):
    ...


class Scalar(UnmountedType, BaseType):
    @classmethod
    def __init_subclass_with_meta__(cls, **options: Any) -> None:  # type: ignore[override]
        ...

    serialize: Any = ...
    parse_value: Any = ...
    parse_literal: Any = ...

    @classmethod
    def get_type(cls) -> Any:
        ...


MAX_INT: int
MIN_INT: int


class Int(Scalar):
    @staticmethod
    def coerce_int(value: Any) -> int:
        ...

    serialize = coerce_int
    parse_value = coerce_int

    @staticmethod
    def parse_literal(ast: Any) -> Any:
        ...


class Float(Scalar):
    @staticmethod
    def coerce_float(value: Any) -> float:
        ...

    serialize = coerce_float
    parse_value = coerce_float

    @staticmethod
    def parse_literal(ast: Any) -> Any:
        ...


class String(Scalar):
    @staticmethod
    def coerce_string(value: Any) -> str:
        ...

    serialize = coerce_string
    parse_value = coerce_string

    @staticmethod
    def parse_literal(ast: Any) -> Any:
        ...


class Boolean(Scalar):
    serialize = bool
    parse_value = bool

    @staticmethod
    def parse_literal(ast: Any) -> Any:
        ...


class ID(Scalar):
    serialize = str
    parse_value = str

    @staticmethod
    def parse_literal(ast: Any) -> Any:
        ...
