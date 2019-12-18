from .argument import Argument as Argument, to_arguments as to_arguments
from .mountedtype import MountedType as MountedType
from .structures import NonNull as NonNull
from .unmountedtype import UnmountedType as UnmountedType
from .utils import get_type as get_type
from typing import Any, Optional

base_type = type


def source_resolver(source: Any, root: Any, info: Any, **args: Any) -> Any:
    ...


class Field(MountedType):
    name: Any = ...
    args: Any = ...
    resolver: Any = ...
    deprecation_reason: Any = ...
    description: Any = ...
    default_value: Any = ...

    def __init__(
        self,
        type: Any,
        args: Optional[Any] = ...,
        resolver: Optional[Any] = ...,
        source: Optional[Any] = ...,
        deprecation_reason: Optional[Any] = ...,
        name: Optional[Any] = ...,
        description: Optional[Any] = ...,
        required: bool = ...,
        _creation_counter: Optional[Any] = ...,
        default_value: Optional[Any] = ...,
        **extra_args: Any
    ) -> None:
        ...

    @property
    def type(self) -> Any:
        ...

    def get_resolver(self, parent_resolver: Any) -> Any:
        ...
