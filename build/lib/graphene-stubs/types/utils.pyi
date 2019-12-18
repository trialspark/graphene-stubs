from ..utils.module_loading import import_string as import_string
from .mountedtype import MountedType as MountedType
from .unmountedtype import UnmountedType as UnmountedType
from typing import Any, Optional


def get_field_as(value: Any, _as: Optional[Any] = ...) -> Any:
    ...


def yank_fields_from_attrs(attrs: Any, _as: Optional[Any] = ..., sort: bool = ...) -> Any:
    ...


def get_type(_type: Any) -> Any:
    ...
