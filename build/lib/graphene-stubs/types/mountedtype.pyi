from ..utils.orderedtype import OrderedType as OrderedType
from .unmountedtype import UnmountedType as UnmountedType
from typing import Any


class MountedType(OrderedType):
    @classmethod
    def mounted(cls, unmounted: Any) -> Any:
        ...
