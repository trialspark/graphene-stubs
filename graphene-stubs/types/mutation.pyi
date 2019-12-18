from ..utils.deprecated import warn_deprecation as warn_deprecation
from ..utils.get_unbound_function import get_unbound_function as get_unbound_function
from ..utils.props import props as props
from .argument import Argument as Argument
from .field import Field as Field
from .objecttype import ObjectType as ObjectType, ObjectTypeOptions as ObjectTypeOptions
from .utils import yank_fields_from_attrs as yank_fields_from_attrs
from typing import Any, Callable, Dict, Optional, Type

MYPY: bool


class MutationOptions(ObjectTypeOptions):
    arguments: Dict[str, Argument] = ...
    output: Type[ObjectType] = ...
    resolver: Callable = ...


class Mutation(ObjectType):
    @classmethod
    def __init_subclass_with_meta__(  # type: ignore[override]
        cls,
        resolver: Optional[Any] = ...,
        output: Optional[Any] = ...,
        arguments: Optional[Any] = ...,
        _meta: Optional[Any] = ...,
        **options: Any
    ) -> None:
        ...

    @classmethod
    def Field(
        cls,
        name: Optional[Any] = ...,
        description: Optional[Any] = ...,
        deprecation_reason: Optional[Any] = ...,
        required: bool = ...
    ) -> Any:
        ...
