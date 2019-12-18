from datetime import datetime, date, time
from .scalars import Scalar as Scalar
from typing import Any


class Date(Scalar):
    @staticmethod
    def serialize(date: Any) -> Any:
        ...

    @classmethod
    def parse_literal(cls, node: Any) -> Any:
        ...

    @staticmethod
    def parse_value(value: Any) -> date:
        ...


class DateTime(Scalar):
    @staticmethod
    def serialize(dt: Any) -> Any:
        ...

    @classmethod
    def parse_literal(cls, node: Any) -> Any:
        ...

    @staticmethod
    def parse_value(value: Any) -> datetime:
        ...


class Time(Scalar):
    @staticmethod
    def serialize(time: Any) -> Any:
        ...

    @classmethod
    def parse_literal(cls, node: Any) -> Any:
        ...

    @classmethod
    def parse_value(cls, value: Any) -> time:
        ...
