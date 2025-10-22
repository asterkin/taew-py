"""Marshalling domain types and utilities.

This module defines the concept of marshallable data structures - compositions
of primitive scalar types (str, int, float, bool, None), lists, and dictionaries
that can be marshalled (serialized) to various interchange formats such as JSON,
YAML, XML, and others.

Marshallable structures represent the intermediate form in the marshalling process:
1. Domain objects are converted TO marshallable primitives (ToMarshallable)
2. Marshallable primitives are encoded to strings/bytes by format-specific adapters
3. The reverse process unmarshalls: bytes/strings → primitives → domain objects
"""

# Marshallable type alias for data structures composed of primitives, lists, and dicts
Marshallable = (
    str | int | float | bool | None | list["Marshallable"] | dict[str, "Marshallable"]
)


def is_marshallable(type_: type) -> bool:
    """Check if a type is marshallable (basic primitive types only).

    Args:
        type_: The type to check for marshallability

    Returns:
        True if the type is one of the basic marshallable types:
        str, int, float, bool, NoneType, list, dict
    """
    # Handle NoneType specifically
    if type_ is type(None):
        return True

    # Check basic marshallable types
    return type_ in {str, int, float, bool, list, dict}
