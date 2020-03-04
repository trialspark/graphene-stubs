<img src="http://mypy-lang.org/static/mypy_light.svg" alt="mypy logo" width="300px"/>

Mypy plugin and stubs for Graphene
====================================

This is basically an attempt to copy the pattern for publishing stubs + a plugin established by the sqlalchemy-stubs repo.

## Installation
`pip install graphene-stubs`

Include the plugin in your mypy.ini file:
```
[mypy]
plugins = graphene_plugin
```

If you want to use the generic version of `ObjectType` then you have to call `patch_object_type()` at the entry point of your application, **before defining any `ObjectType` sub-classes**:
```python
from graphene_plugin import patch_object_type
# Have to patch before defining an `ObjectType` sub-classes, OR importing any modules that define
# `ObjectType` sub-classes.
patch_object_type()


from graphene import ObjectType, Field, String, ResolveInfo


class PersonModel:
    first_name: str
    last_name: str


class AnimalModel:
    species: str


class Person(ObjectType[PersonModel]):
    first_name = Field(String, required=True)
    last_name = Field(String, required=True)

    @staticmethod
    def resolve_first_name(person: PersonModel, _: ResolveInfo) -> str:
        return person.first_name

    @staticmethod
    def resolve_last_name(person: AnimalModel, _: ResolveInfo) -> str:  # Fails, the type of `person` doesn't match the generic argument
        return person.species
```

## Plugin Details
Because of the implementation and patterns used by Graphene, there are many cases where types are being declared and correspond to arguments used in resolvers, but it's hard for mypy to understand the correlation between them. Because of this, a plugin has been added that does nothing but throw additional errors when types don't seem to match up.

For details on exactly what the plugin supports, you can view the test data in `test/test-data/unit/graphene_plugin.test`, but here's a list of things currently supported:

For classes with the base class `ObjectType`:
- Erroring when arguments are included in a field attribute definition, but are missing in the resolver method's signature.
- Erroring when resolvers are defined that don't have corresponding field attributes.
- Erroring when the types defined in field attribute `Argument`s don't match up with type annotations in resolvers *perfectly*.
- Erroring when a resolver's return type does not match the corresponding field attribute definition
- Some amount of robustness for all of the above features, including type checking custom scalar types out of the box, following `Interface`s defined in a `Meta` class on the `ObjectType` to see additional fields, typing `graphene.Enum` types correctly as strings, supporting both static and non-static resolver methods.


Currently not supported:
- Anything to do with `Mutation` classes.
- Anything to do with parsing graphql query strings passed to `execute_query`.

## Development Setup

First, clone the repo and cd into it. Then _install_ the repo (`pip install -e .`).

Then:
```
export MYPY_TEST_PREFIX=./test
```

To run the tests:
```
pytest -n 0 -p no:flaky
```

Note that `"-n 0 -p no:flaky"` are related to pytest plugins you may not have installed, so you may only have to run `pytest`.
