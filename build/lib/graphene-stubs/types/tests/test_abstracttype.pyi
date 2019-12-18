from .. import abstracttype as abstracttype
from ..abstracttype import AbstractType as AbstractType
from ..field import Field as Field
from ..objecttype import ObjectType as ObjectType
from ..unmountedtype import UnmountedType as UnmountedType
from typing import Any

class MyType(ObjectType): ...

class MyScalar(UnmountedType):
    def get_type(self) -> Any: ...

def test_abstract_objecttype_warn_deprecation(mocker: Any) -> None: ...
def test_generate_objecttype_inherit_abstracttype() -> None: ...
