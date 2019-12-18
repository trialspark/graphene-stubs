from typing import Any


def attr_resolver(attname: Any, default_value: Any, root: Any, info: Any, **args: Any) -> Any:
    ...


def dict_resolver(attname: Any, default_value: Any, root: Any, info: Any, **args: Any) -> Any:
    ...


def dict_or_attr_resolver(attname: Any, default_value: Any, root: Any, info: Any, **args: Any) -> Any:
    ...


default_resolver = dict_or_attr_resolver


def set_default_resolver(resolver: Any) -> None:
    ...


def get_default_resolver() -> Any:
    ...
