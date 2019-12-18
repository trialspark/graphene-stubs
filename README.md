<img src="http://mypy-lang.org/static/mypy_light.svg" alt="mypy logo" width="300px"/>

Mypy plugin and stubs for Graphene
====================================

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
