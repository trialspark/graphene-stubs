from ..types import Field as Field, InputObjectType as InputObjectType, String as String
from ..types.mutation import Mutation as Mutation
from ..utils.thenables import maybe_thenable as maybe_thenable
from typing import Any, Optional


class ClientIDMutation(Mutation):
    class Meta:
        abstract: bool = ...

    @classmethod
    def __init_subclass_with_meta__(  # type: ignore[override]
        cls,
        output: Optional[Any] = ...,
        input_fields: Optional[Any] = ...,
        arguments: Optional[Any] = ...,
        name: Optional[Any] = ...,
        **options: Any
    ) -> None:
        ...

    @classmethod
    def mutate(cls, root: Any, info: Any, input: Any) -> Any:
        ...
