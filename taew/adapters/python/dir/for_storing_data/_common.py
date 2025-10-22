"""Common utilities for directory-based data storage adapters.

This module provides shared functionality for reading and writing files
in both binary and text modes, supporting both streaming and stringizing
serialization strategies.
"""

import re
from pathlib import Path
from typing import Final, Literal, Pattern

from taew.ports.for_stringizing_objects import Loads as LoadsProtocol
from taew.ports.for_stringizing_objects import Dumps as DumpsProtocol
from taew.ports.for_serializing_objects import Serialize as SerializeProtocol
from taew.ports.for_serializing_objects import Deserialize as DeserializeProtocol

# Type aliases
Mode = Literal["b", "t"]
Marshal = SerializeProtocol | DumpsProtocol
Unmarshal = DeserializeProtocol | LoadsProtocol

_EXTENSION_PATTERN: Final[Pattern[str]] = re.compile(r"^[a-zA-Z0-9_]+$")
_KEY_PATTERN: Final[Pattern[str]] = re.compile(r"^[a-zA-Z0-9_\-]+$")


def detect_mode(type_: type) -> Mode:
    """Detect file mode based on protocol type.

    Args:
        type_: The protocol type (ReadProtocol, WriteProtocol, LoadsProtocol, or DumpsProtocol)

    Returns:
        'b' for streaming protocols (binary), 't' for stringizing protocols (text)

    Raises:
        ValueError: If type is not a recognized protocol
    """
    # Check if it's a streaming protocol (binary)
    if type_ in (DeserializeProtocol, SerializeProtocol):
        return "b"
    # Check if it's a stringizing protocol (text)
    if type_ in (LoadsProtocol, DumpsProtocol):
        return "t"
    raise ValueError(f"Unknown protocol type: {type_}")


def validate_extension(extension: str) -> None:
    """Validate file extension format.

    Args:
        extension: File extension to validate

    Raises:
        ValueError: If extension contains invalid characters
    """
    if not _EXTENSION_PATTERN.match(extension):
        raise ValueError(f"Invalid file extension: '{extension}'")


def validate_key(name: str) -> None:
    """Validate key format.

    Args:
        name: Key name to validate

    Raises:
        ValueError: If key contains invalid characters
    """
    if not _KEY_PATTERN.match(name):
        raise ValueError(f"Invalid key format: '{name}'")


def make_path(folder: Path, name: str, extension: str) -> Path:
    """Construct file path from folder, name, and extension.

    Args:
        folder: Directory containing the file
        name: File name (without extension)
        extension: File extension (without dot)

    Returns:
        Complete file path

    Raises:
        ValueError: If extension or name format is invalid
    """
    validate_extension(extension)
    validate_key(name)
    return folder / f"{name}.{extension}"


def read_value(path: Path, mode: Mode, unmarshal: Unmarshal) -> object:
    """Read and deserialize value from file.

    Args:
        path: Path to file to read
        mode: File mode - 'b' for binary, 't' for text
        unmarshal: Callable to deserialize data (Read or Loads protocol)

    Returns:
        Deserialized object
    """
    open_mode = f"r{mode}"
    with open(path, open_mode) as f:
        data = f.read()
        return unmarshal(data)  # type: ignore[operator]


def write_value(path: Path, value: object, mode: Mode, marshal: Marshal) -> None:
    """Serialize and write value to file.

    Args:
        path: Path to file to write
        value: Object to serialize and write
        mode: File mode - 'b' for binary, 't' for text
        marshal: Callable to serialize data (Write or Dumps protocol)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    open_mode = f"w{mode}"
    with open(path, open_mode) as f:
        data = marshal(value)  # type: ignore[operator]
        f.write(data)  # type: ignore[arg-type]
