from .thenables_asyncio import await_and_execute as await_and_execute
from typing import Any


class Promise:
    ...


def maybe_thenable(obj: Any, on_resolve: Any) -> Any:
    ...
