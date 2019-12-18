from .signature import signature as signature
from graphql.pyutils.compat import Enum as Enum
from typing import Callable


def func_name(func: Callable) -> str:
    ...
