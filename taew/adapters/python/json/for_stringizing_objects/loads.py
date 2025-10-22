import json
from typing import Any
from dataclasses import dataclass

from taew.ports.for_marshalling_objects import (
    FromMarshallable as FromMarshallableProtocol,
)


def _identity(data: object) -> object:
    """Identity function for data that is already in final form."""
    return data


@dataclass(frozen=True, eq=False)
class LoadsBase:
    """Base class containing json.loads configuration parameters."""

    _cls: type | None = None
    _object_hook: Any = None
    _parse_float: Any = None
    _parse_int: Any = None
    _parse_constant: Any = None
    _object_pairs_hook: Any = None
    _strict: bool = True


@dataclass(frozen=True, eq=False)
class Loads(LoadsBase):
    """Converts JSON strings back to Python objects with configurable options.

    Supports optional unmarshalling converter to transform JSON-compatible
    structures to final objects after parsing.

    Args:
        from_marshallable: Optional converter to transform marshallable form to objects.
                          Defaults to identity (no conversion).
    """

    from_marshallable: FromMarshallableProtocol = _identity

    def __call__(self, buf: str) -> object:
        parsed = json.loads(
            buf,
            cls=self._cls,
            object_hook=self._object_hook,
            parse_float=self._parse_float,
            parse_int=self._parse_int,
            parse_constant=self._parse_constant,
            object_pairs_hook=self._object_pairs_hook,
            strict=self._strict,
        )
        return self.from_marshallable(parsed)
