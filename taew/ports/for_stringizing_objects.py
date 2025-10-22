from typing import Protocol


class Dumps(Protocol):
    """Protocol for converting Python objects to strings.

    Implementations take an arbitrary Python object and return its string
    representation (e.g., JSON, YAML, TOML, etc.).
    """

    def __call__(self, value: object) -> str: ...


class Loads(Protocol):
    """Protocol for converting strings into Python objects.

    Implementations take a string buffer and reconstruct a Python object
    from it.
    """

    def __call__(self, buf: str) -> object: ...
