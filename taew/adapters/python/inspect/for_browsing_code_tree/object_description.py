import inspect
from typing import Any
from docstring_parser import parse


def extract_object_description(obj: Any) -> str:
    """Extract short description from object's docstring."""
    try:
        docstring = inspect.getdoc(obj)
    except Exception:
        # inspect.getdoc() can fail with some object types
        return ""

    if docstring:
        try:
            parsed = parse(docstring)
        except Exception:
            # docstring_parser.parse() can fail with malformed docstrings
            return ""

        if parsed and parsed.short_description:
            try:
                # Strip whitespace and check if result is non-empty
                cleaned = parsed.short_description.strip()
                if cleaned:
                    return cleaned
            except (AttributeError, TypeError):
                # Handle case where short_description is not a string
                return ""

    return ""
