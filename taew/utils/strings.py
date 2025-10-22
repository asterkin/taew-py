import re


def pascal_to_snake(pascal_str: str) -> str:
    """
    Converts a PascalCase string to snake_case.

    Args:
        pascal_str (str): The PascalCase string to convert.

    Returns:
        str: The converted snake_case string.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", pascal_str).lower()


def snake_to_pascal(snake_str: str) -> str:
    """
    Converts a snake_case string to PascalCase.

    Args:
        snake_str (str): The snake_case string to convert.

    Returns:
        str: The converted PascalCase string.
    """
    return "".join(word.capitalize() for word in snake_str.split("_"))
