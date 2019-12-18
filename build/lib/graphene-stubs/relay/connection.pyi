from ..types import Boolean as Boolean, Enum as Enum, Int as Int, Interface as Interface, List as List, NonNull as NonNull, Scalar as Scalar, String as String, Union as Union
from ..types.field import Field as Field
from ..types.objecttype import ObjectType as ObjectType, ObjectTypeOptions as ObjectTypeOptions
from ..utils.thenables import maybe_thenable as maybe_thenable
from .node import is_node as is_node
from typing import Any, Optional


class PageInfo(ObjectType):
    class Meta:
        description: str = ...

    has_next_page: Any = ...
    has_previous_page: Any = ...
    start_cursor: Any = ...
    end_cursor: Any = ...


class ConnectionOptions(ObjectTypeOptions):
    node: Any = ...


class Connection(ObjectType):
    class Meta:
        abstract: bool = ...

    @classmethod
    def __init_subclass_with_meta__(  # type: ignore[override]
        cls,
        node: Optional[Any] = ...,
        name: Optional[Any] = ...,
        **options: Any
    ) -> Any:
        ...


class IterableConnectionField(Field):
    def __init__(self, type: Any, *args: Any, **kwargs: Any) -> None:
        ...

    @property
    def type(self) -> Any:
        ...

    @classmethod
    def resolve_connection(cls, connection_type: Any, args: Any, resolved: Any) -> Any:
        ...

    @classmethod
    def connection_resolver(cls, resolver: Any, connection_type: Any, root: Any, info: Any, **args: Any) -> Any:
        ...

    def get_resolver(self, parent_resolver: Any) -> Any:
        ...


ConnectionField = IterableConnectionField
