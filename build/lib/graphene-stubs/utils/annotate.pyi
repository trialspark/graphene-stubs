from ..pyutils.compat import func_name as func_name, signature as signature
from .deprecated import warn_deprecation as warn_deprecation
from typing import Any, Optional


def annotate(_func: Optional[Any] = ..., _trigger_warning: bool = ..., **annotations: Any) -> Any:
    ...
