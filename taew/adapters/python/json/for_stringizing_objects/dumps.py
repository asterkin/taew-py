import json
from typing import Any
from dataclasses import dataclass

from taew.domain.marshalling import Marshallable
from taew.ports.for_marshalling_objects import ToMarshallable as ToMarshallableProtocol


def _identity(value: object) -> Marshallable:
    """Identity function for objects that are already marshallable."""
    return value  # type: ignore[return-value]


@dataclass(frozen=True, eq=False)
class DumpsBase:
    """Base class containing json.dumps configuration parameters."""

    _skipkeys: bool = False
    _ensure_ascii: bool = True
    _check_circular: bool = True
    _allow_nan: bool = True
    _cls: type | None = None
    _indent: None | int | str = None
    _separators: tuple[str, str] | None = None
    _default: Any = None
    _sort_keys: bool = False


@dataclass(frozen=True, eq=False)
class Dumps(DumpsBase):
    """Converts Python objects to JSON strings with configurable options.

    Supports optional marshalling converter to transform objects to JSON-compatible
    structures before stringification.

    Args:
        to_marshallable: Optional converter to transform objects to marshallable form.
                        Defaults to identity (no conversion).
    """

    to_marshallable: ToMarshallableProtocol = _identity

    def __call__(self, value: object) -> str:
        marshallable = self.to_marshallable(value)
        return json.dumps(
            marshallable,
            skipkeys=self._skipkeys,
            ensure_ascii=self._ensure_ascii,
            check_circular=self._check_circular,
            allow_nan=self._allow_nan,
            cls=self._cls,
            indent=self._indent,
            separators=self._separators,
            default=self._default,
            sort_keys=self._sort_keys,
        )
