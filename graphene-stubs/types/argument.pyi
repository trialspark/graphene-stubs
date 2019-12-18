from .dynamic import Dynamic as Dynamic
from .mountedtype import MountedType as MountedType
from .structures import NonNull as NonNull
from .utils import get_type as get_type
from typing import Any, Optional


class Argument(MountedType):
    name: Any = ...
    default_value: Any = ...
    description: Any = ...

    def __init__(
        self,
        type: Any,
        default_value: Optional[Any] = ...,
        description: Optional[Any] = ...,
        name: Optional[Any] = ...,
        required: bool = ...,
        _creation_counter: Optional[Any] = ...
    ) -> None:
        ...

    @property
    def type(self) -> Any:
        ...

    def __eq__(self, other: Any) -> Any:
        ...


def to_arguments(args: Any, extra_args: Optional[Any] = ...) -> Any:
    ...
