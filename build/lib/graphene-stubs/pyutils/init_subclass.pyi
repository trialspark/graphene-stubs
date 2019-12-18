from typing import Any, TypeVar, Type

_T = TypeVar('_T', bound=object)


class InitSubclassMeta(type):
    def __new__(cls: Type[_T], name: Any, bases: Any, ns: Any, **kwargs: Any) -> _T:
        ...

    def __init__(cls, name: Any, bases: Any, ns: Any, **kwargs: Any) -> None:
        ...
