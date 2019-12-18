from .base import BaseOptions as BaseOptions, BaseType as BaseType
from .inputfield import InputField as InputField
from .unmountedtype import UnmountedType as UnmountedType
from .utils import yank_fields_from_attrs as yank_fields_from_attrs
from typing import Any, Dict, Optional

MYPY: bool


class InputObjectTypeOptions(BaseOptions):
    fields: Dict[str, InputField] = ...
    container: InputObjectTypeContainer = ...


class InputObjectTypeContainer(dict, BaseType):
    class Meta:
        abstract: bool = ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        ...


class InputObjectType(UnmountedType, BaseType):
    @classmethod
    def __init_subclass_with_meta__(  # type: ignore[override]
        cls,
        container: Optional[Any] = ...,
        _meta: Optional[Any] = ...,
        **options: Any
    ) -> None:
        ...

    @classmethod
    def get_type(cls) -> Any:
        ...
