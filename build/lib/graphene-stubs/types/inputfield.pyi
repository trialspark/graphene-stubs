from .mountedtype import MountedType as MountedType
from .structures import NonNull as NonNull
from .utils import get_type as get_type
from typing import Any, Optional


class InputField(MountedType):
    name: Any = ...
    deprecation_reason: Any = ...
    default_value: Any = ...
    description: Any = ...

    def __init__(
        self,
        type: Any,
        name: Optional[Any] = ...,
        default_value: Optional[Any] = ...,
        deprecation_reason: Optional[Any] = ...,
        description: Optional[Any] = ...,
        required: bool = ...,
        _creation_counter: Optional[Any] = ...,
        **extra_args: Any
    ) -> None:
        ...

    @property
    def type(self) -> Any:
        ...
