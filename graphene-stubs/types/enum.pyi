from enum import Enum as PyEnum
from typing import Any, Optional, Type

from graphene.utils.subclass_with_meta import SubclassWithMeta_Meta as SubclassWithMeta_Meta

from .base import BaseOptions as BaseOptions, BaseType as BaseType
from .unmountedtype import UnmountedType as UnmountedType


def eq_enum(self: Any, other: Any) -> Any:
    ...


EnumType: Any


class EnumOptions(BaseOptions):
    enum: Enum = ...
    deprecation_reason: Any = ...


class EnumMeta(SubclassWithMeta_Meta):
    def __new__(cls, name: Any, bases: Any, classdict: Any, **options: Any) -> Any:
        ...

    def get(cls, value: Any) -> Any:
        ...

    def __getitem__(cls, value: Any) -> Any:
        ...

    def __prepare__(name: Any, bases: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        ...

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        ...

    def from_enum(
        cls,
        enum: Any,
        description: Optional[Any] = ...,
        deprecation_reason: Optional[Any] = ...,
    ) -> Any:
        ...


class Enum(UnmountedType, BaseType, metaclass=EnumMeta):
    @classmethod
    def __init_subclass_with_meta__(  # type: ignore[override]
            cls,
            enum: Optional[Any] = ...,
            _meta: Optional[Any] = ...,
            **options: Any) -> None:
        ...

    @classmethod
    def get_type(cls) -> Any:
        ...
