from enum import Enum as PyEnum
from typing import Any, Optional, Union, Dict, Callable, Type
from .argument import Argument as Argument, to_arguments as to_arguments
from .mountedtype import MountedType as MountedType
from .structures import NonNull as NonNull
from .unmountedtype import UnmountedType as UnmountedType
from .utils import get_type as get_type
from .objecttype import ObjectType
from .structures import Structure
from .base import BaseType
from .enum import Enum

base_type = type

def source_resolver(source: Any, root: Any, info: Any, **args: Any) -> Any:
    ...

TypeType: Union[Type[Union[ObjectType, UnmountedType, BaseType, Enum, PyEnum]], Structure, Enum, str]
class Field(MountedType):
    name: Optional[str] = ...
    args: Optional[Dict[str, Argument]] = ...
    resolver: Optional[Callable[[], Any]] = ...
    deprecation_reason: Optional[str] = ...
    description: Optional[str] = ...
    default_value: Optional[Any] = ...

    def __init__(
        self,
        type: Union[TypeType, Callable[[], TypeType]],
        args: Optional[Dict[str, Argument]] = None,
        resolver: Optional[Callable[[], Any]] = None,
        source: Optional[str] = None,
        deprecation_reason: Optional[str] = None,
        name: Optional[Union[str, Argument]] = None,
        description: Optional[str] = None,
        required: bool = False,
        _creation_counter: Optional[Any] = None,
        default_value: Optional[Any] = ...,
        **extra_args: Any
    ) -> None:
        ...

    @property
    def type(self) -> Any:
        ...

    def get_resolver(self, parent_resolver: Any) -> Any:
        ...
