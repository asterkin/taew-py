from dataclasses import dataclass, field as dataclass_field
from typing import Any

from taew.domain.marshalling import Marshallable
from taew.ports.for_marshalling_objects import (
    FromMarshallable as FromMarshallableProtocol,
)


def _identity(data: Marshallable) -> object:
    """Identity function for primitive types that are already marshallable."""
    return data


@dataclass(frozen=True, eq=False)
class FromMarshallable:
    """Parse marshallable dicts back to named tuples using field-specific converters.

    Takes a dict and converts it to a named tuple where each field value is converted
    using the corresponding field-specific FromMarshallable converter. Fields without
    converters are passed through as-is (identity conversion for primitives).

    Args:
        _type: The named tuple type to construct
        _converters: Dict mapping field names to FromMarshallable converters
    """

    _type: type[Any]
    _converters: dict[str, FromMarshallableProtocol]
    _fields: tuple[str, ...] = dataclass_field(init=False)

    def __post_init__(self) -> None:
        if not hasattr(self._type, "_fields"):
            raise TypeError(
                f"Expected named tuple type with _fields attribute, got {self._type.__name__}"
            )

        fields = getattr(self._type, "_fields")
        object.__setattr__(self, "_fields", fields)

    def __call__(self, data: Marshallable) -> object:
        if not isinstance(data, dict):
            raise TypeError(
                f"Expected dict for named tuple unmarshalling, got {type(data)}"
            )

        # Verify all required fields are present
        if set(data.keys()) != set(self._fields):
            raise ValueError(
                f"Field mismatch in dict: expected {set(self._fields)}, "
                f"got {set(data.keys())}"
            )

        # Convert each field value using dict comprehension
        field_values = {
            field_name: self._converters.get(field_name, _identity)(data[field_name])
            for field_name in self._fields
        }

        return self._type(**field_values)
