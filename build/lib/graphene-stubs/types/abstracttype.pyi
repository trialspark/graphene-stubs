from ..utils.deprecated import warn_deprecation as warn_deprecation
from ..utils.subclass_with_meta import SubclassWithMeta as SubclassWithMeta
from typing import Any


class AbstractType(SubclassWithMeta):
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        ...
