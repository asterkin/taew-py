from dataclasses import dataclass
from typing import Any, cast

from taew.domain.marshalling import Marshallable
from taew.ports.for_marshalling_objects import ToMarshallable as ToMarshallableProtocol


def _identity(value: object) -> Marshallable:
    """Identity function for primitive types that are already marshallable."""
    return value  # type: ignore[return-value]


@dataclass(frozen=True, eq=False)
class ToMarshallable:
    """Convert named tuples to marshallable dict structures using field-specific converters.

    Takes a named tuple and converts it to a dict where each field value is converted
    using the corresponding field-specific ToMarshallable converter. Fields without
    converters are passed through as-is (identity conversion for primitives).

    Args:
        _converters: Dict mapping field names to ToMarshallable converters
    """

    _converters: dict[str, ToMarshallableProtocol]

    def __call__(self, value: object) -> Marshallable:
        if not hasattr(value, "_fields"):
            raise TypeError(
                f"Expected named tuple with _fields attribute, got {type(value).__name__}"
            )

        named_tuple = cast(Any, value)
        fields = getattr(named_tuple, "_fields")

        return {
            field_name: self._converters.get(field_name, _identity)(
                getattr(named_tuple, field_name)
            )
            for field_name in fields
        }
