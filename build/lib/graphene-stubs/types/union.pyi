from .base import BaseOptions as BaseOptions, BaseType as BaseType
from .objecttype import ObjectType as ObjectType
from .unmountedtype import UnmountedType as UnmountedType
from typing import Any, Iterable, Optional, Type

MYPY: bool


class UnionOptions(BaseOptions):
    types: Iterable[Type[ObjectType]] = ...


class Union(UnmountedType, BaseType):
    @classmethod
    def __init_subclass_with_meta__(cls, types: Optional[Any] = ..., **options: Any) -> None:  # type: ignore[override]
        ...

    @classmethod
    def get_type(cls) -> Any:
        ...

    @classmethod
    def resolve_type(cls, instance: Any, info: Any) -> Any:
        ...
