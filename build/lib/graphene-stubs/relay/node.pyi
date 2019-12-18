from ..types import Field as Field, ID as ID, Interface as Interface, ObjectType as ObjectType
from ..types.interface import InterfaceOptions as InterfaceOptions
from ..types.utils import get_type as get_type
from typing import Any, Optional


def is_node(objecttype: Any) -> Any:
    ...


class GlobalID(Field):
    node: Any = ...
    parent_type_name: Any = ...

    def __init__(
        self,
        node: Optional[Any] = ...,
        parent_type: Optional[Any] = ...,
        required: bool = ...,
        *args: Any,
        **kwargs: Any
    ) -> None:
        ...

    @staticmethod
    def id_resolver(
        parent_resolver: Any, node: Any, root: Any, info: Any, parent_type_name: Optional[Any] = ..., **args: Any
    ) -> Any:
        ...

    def get_resolver(self, parent_resolver: Any) -> Any:
        ...


class NodeField(Field):
    node_type: Any = ...
    field_type: Any = ...

    def __init__(
        self,
        node: Any,
        type: bool = ...,
        deprecation_reason: Optional[Any] = ...,
        name: Optional[Any] = ...,
        **kwargs: Any
    ) -> None:
        ...

    def get_resolver(self, parent_resolver: Any) -> Any:
        ...


class AbstractNode(Interface):
    class Meta:
        abstract: bool = ...

    @classmethod
    def __init_subclass_with_meta__(cls, **options: Any) -> None:  # type: ignore[override]
        ...


class Node(AbstractNode):
    @classmethod
    def Field(cls, *args: Any, **kwargs: Any) -> Any:
        ...

    @classmethod
    def node_resolver(cls, only_type: Any, root: Any, info: Any, id: Any) -> Any:
        ...

    @classmethod
    def get_node_from_global_id(cls, info: Any, global_id: Any, only_type: Optional[Any] = ...) -> Any:
        ...

    @classmethod
    def from_global_id(cls, global_id: Any) -> Any:
        ...

    @classmethod
    def to_global_id(cls, type: Any, id: Any) -> Any:
        ...
