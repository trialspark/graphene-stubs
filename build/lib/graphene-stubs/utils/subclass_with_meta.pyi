from ..pyutils.init_subclass import InitSubclassMeta as InitSubclassMeta
from .props import props as props
from typing import Any

class SubclassWithMeta_Meta(InitSubclassMeta): ...

class SubclassWithMeta(metaclass=SubclassWithMeta_Meta):
    def __init_subclass__(cls, **meta_options: Any) -> None: ...
    @classmethod
    def __init_subclass_with_meta__(cls, **meta_options: Any) -> None: ...
