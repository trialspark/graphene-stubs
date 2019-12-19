<img src="http://mypy-lang.org/static/mypy_light.svg" alt="mypy logo" width="300px"/>

Mypy plugin and stubs for Graphene
====================================

This is basically an attempt to copy the sqlalchemy-stubs repo. This is meant as a sandbox to play around with plugins and stubs until it gets used in the main Spark repo.

## Installation
`pip install graphene-stubs`

Include the plugin in your mypy.ini file:
```
[mypy]
plugins = sqlmypy
```

## Development Setup

First, clone the repo and cd into it, then:
```
git submodule update --init --recursive
pip install -r dev-requirements.txt
export MYPY_TEST_PREFIX=./test
```

Then, to run the tests:
```
pytest -n 0 -p no:flaky # "-p no:flaky" not required if you don't have the pytest flaky plugin installed
```

## Plugin Details
Because of the implementation and patterns used by Graphene, there are many cases where types are being declared and correspond to arguments used in resolvers, but it's hard for mypy to understand the correlation between them. Because of this, a plugin has been added that does nothing but throw additional errors when types don't seem to match up.

For details on exactly what the plugin supports, you can view the test data in `test/test-data/unit/graphene_plugin.test`, but here's a list of things currently supported:

For classes with the base class `ObjectType`:
- Erroring when arguments are included in a field attribute definition, but are missing in the resolver method's signature.
- Erroring when resolvers are defined that don't have corresponding field attributes.
- Erroring when the types defined in field attribute `Argument`s don't match up with type annotations in resolvers *perfectly*.
- Some amount of robustness for all of the above features, including type checking custom scalar types out of the box, following `Interface`s defined in a `Meta` class on the `ObjectType` to see additional fields, typing `graphene.Enum` types correctly as strings, supporting both static and non-static resolver methods.


Currently not supported:
- Checking return types of resolvers. This will require some careful definition and potentially the addition of a type generator.
- Anything to do with `Mutation` classes.
- Anything to do with parsing graphql query strings passed to `execute_query`.
