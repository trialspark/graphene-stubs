from typing import Any, Optional


class OrderedType:
    creation_counter: int = ...

    def __init__(self, _creation_counter: Optional[Any] = ...) -> None:
        ...

    @staticmethod
    def gen_counter() -> Any:
        ...

    def reset_counter(self) -> None:
        ...

    def __eq__(self, other: Any) -> Any:
        ...

    def __lt__(self, other: Any) -> Any:
        ...

    def __gt__(self, other: Any) -> Any:
        ...

    def __hash__(self) -> Any:
        ...
