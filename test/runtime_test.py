from unittest import TestCase

from graphene import ObjectType, Field, String, ResolveInfo, Schema
from graphene_plugin import patch_object_type

patch_object_type()


class RuntimeTest(TestCase):
    def test_object_type_is_indexable_at_runtime(self) -> None:
        class Query(ObjectType[None]):  # pylint: disable=unsubscriptable-object
            string = Field(String)

            @staticmethod
            def resolve_string(_: None, __: ResolveInfo) -> str:
                return 'foo'

        Schema(query=Query)
