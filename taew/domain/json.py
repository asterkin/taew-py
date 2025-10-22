"""JSON domain types and utilities."""

from typing import Union


# JSONable type alias for JSON-compatible types
JSONable = Union[str, int, float, bool, None, list["JSONable"], dict[str, "JSONable"]]


def is_jsonable(type_: type) -> bool:
    """Check if a type is JSON-compatible (basic JSON types only).

    Args:
        type_: The type to check for JSON compatibility

    Returns:
        True if the type is one of the basic JSON types:
        str, int, float, bool, NoneType, list, dict
    """
    # Handle NoneType specifically
    if type_ is type(None):
        return True

    # Check basic JSON types
    return type_ in {str, int, float, bool, list, dict}
