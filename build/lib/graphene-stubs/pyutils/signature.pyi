from typing import Any, Optional, TypeVar, Type


def signature(obj: Any):
    ...


class _void:
    ...


class _empty:
    ...


class _ParameterKind(int):
    def __new__(self, *args: Any, **kwargs: Any):
        ...


_T: TypeVar('_T', bound=object)


class Parameter:
    POSITIONAL_ONLY: Any = ...
    POSITIONAL_OR_KEYWORD: Any = ...
    VAR_POSITIONAL: Any = ...
    KEYWORD_ONLY: Any = ...
    VAR_KEYWORD: Any = ...
    empty: Any = ...

    def __init__(
        self, name: Any, kind: Any, default: Any = ..., annotation: Any = ..., _partial_kwarg: bool = ...
    ) -> None:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def default(self) -> Any:
        ...

    @property
    def annotation(self) -> Any:
        ...

    @property
    def kind(self) -> Any:
        ...

    def replace(
        self: _T,
        name: Any = ...,
        kind: Any = ...,
        annotation: Any = ...,
        default: Any = ...,
        _partial_kwarg: Any = ...
    ) -> _T:
        ...

    def __hash__(self) -> Any:
        ...

    def __eq__(self, other: Any) -> Any:
        ...

    def __ne__(self, other: Any) -> Any:
        ...


class BoundArguments:
    arguments: Any = ...

    def __init__(self, signature: Any, arguments: Any) -> None:
        ...

    @property
    def signature(self) -> Any:
        ...

    @property
    def args(self) -> tuple:
        ...

    @property
    def kwargs(self) -> dict:
        ...

    def __hash__(self) -> Any:
        ...

    def __eq__(self, other: Any) -> bool:
        ...

    def __ne__(self, other: Any) -> bool:
        ...


class Signature:
    empty: Any = ...

    def __init__(
        self, parameters: Optional[Any] = ..., return_annotation: Any = ..., __validate_parameters__: bool = ...
    ) -> None:
        ...

    @classmethod
    def from_function(cls: Type[_T], func: Any) -> _T:
        ...

    @property
    def parameters(self) -> Any:
        ...

    @property
    def return_annotation(self) -> Any:
        ...

    def replace(self: _T, parameters: Any = ..., return_annotation: Any = ...) -> _T:
        ...

    def __hash__(self) -> Any:
        ...

    def __eq__(self, other: Any) -> Any:
        ...

    def __ne__(self, other: Any) -> Any:
        ...

    def bind(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def bind_partial(self, *args: Any, **kwargs: Any) -> Any:
        ...
