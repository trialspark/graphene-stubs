from ...types import ID as ID, NonNull as NonNull, ObjectType as ObjectType, String as String
from ...types.definitions import GrapheneObjectType as GrapheneObjectType
from ..node import GlobalID as GlobalID, Node as Node
from typing import Any

class CustomNode(Node):
    class Meta:
        name: str = ...

class User(ObjectType):
    class Meta:
        interfaces: Any = ...
    name: Any = ...

class Info:
    parent_type: Any = ...
    def __init__(self, parent_type: Any) -> None: ...

def test_global_id_defaults_to_required_and_node() -> None: ...
def test_global_id_allows_overriding_of_node_and_required() -> None: ...
def test_global_id_defaults_to_info_parent_type() -> Any: ...
def test_global_id_allows_setting_customer_parent_type() -> Any: ...
