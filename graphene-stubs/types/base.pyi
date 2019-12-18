from ..utils.subclass_with_meta import SubclassWithMeta as SubclassWithMeta
from ..utils.trim_docstring import trim_docstring as trim_docstring
from typing import Any, Optional


class BaseOptions:
    name: str = ...
    description: str = ...
    class_type: Any = ...

    def __init__(self, class_type: Any) -> None:
        ...

    def freeze(self) -> None:
        ...

    def __setattr__(self, name: Any, value: Any) -> None:
        ...


class BaseType(SubclassWithMeta):
    @classmethod
    def create_type(cls, class_name: Any, **options: Any) -> Any:
        ...

    @classmethod
    def __init_subclass_with_meta__(
        cls, name: Optional[Any] = ..., description: Optional[Any] = ..., _meta: Optional[Any] = ..., **_kwargs: Any
    ) -> None:
        ...
