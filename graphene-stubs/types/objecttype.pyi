from .base import BaseOptions as BaseOptions, BaseType as BaseType
from .field import Field as Field
from .interface import Interface as Interface
from .utils import yank_fields_from_attrs as yank_fields_from_attrs
from typing import Any, Dict, Iterable, Optional, Type, TypeVar, Generic


RT = TypeVar('RT')


class ObjectTypeOptions(BaseOptions):
    fields: Dict[str, Field] = ...
    interfaces: Iterable[Type[Interface]] = ...


class ObjectType(Generic[RT], BaseType):
    @classmethod
    def __init_subclass_with_meta__( # type: ignore[override]
        cls,
        interfaces: Any = ...,
        possible_types: Any = ...,
        default_resolver: Optional[Any] = ...,
        _meta: Optional[Any] = ...,
        **options: Any
    ) -> None:
        ...

    is_type_of: Any = ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...
