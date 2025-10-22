"""Directory-based DataRepository implementation.

Provides read-only key-value storage backed by directory structure.
"""

from pathlib import Path
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Callable, TypeVar, cast

from taew.ports.for_storing_data import DataRepository as DataRepositoryProtocol
from ._common import (
    Mode,
    Unmarshal,
    detect_mode,
    make_path,
    read_value,
    validate_extension,
    validate_key,
)

K = TypeVar("K")
V = TypeVar("V")


@dataclass(eq=False, frozen=True)
class DataRepository(DataRepositoryProtocol[K, V]):
    """Directory-based read-only data repository.

    Implements DataRepository protocol using directory structure where each
    key corresponds to a file. Supports both binary (streaming) and text
    (stringizing) serialization formats.

    Attributes:
        _folder: Directory path for storing data files
        _extension: File extension for data files
        _mode: File mode - 'b' for binary, 't' for text
        _deserialize: Tuple of (type, unmarshaler) for deserialization
        _key_type: Function to convert string to key type
    """

    _folder: Path
    _extension: str
    _deserialize: tuple[Unmarshal, type]
    _key_type: Callable[[str], K]
    _unmarshal: Unmarshal = field(init=False)
    _mode: Mode = field(init=False)

    def __post_init__(self) -> None:
        """Initialize and validate configuration."""
        validate_extension(self._extension)
        unmarshal, type_ = self._deserialize
        object.__setattr__(self, "_unmarshal", unmarshal)
        object.__setattr__(self, "_mode", detect_mode(type_))

    def _make_path(self, key: K) -> Path:
        """Construct the file path for a given key.

        Args:
            key: Key to construct path for

        Returns:
            Path to file corresponding to key
        """
        validate_key(str(key))
        return make_path(self._folder, str(key), self._extension)

    def __len__(self) -> int:
        """Return number of items in repository.

        Returns:
            Count of stored items
        """
        return sum(1 for _ in self._folder.glob(f"*.{self._extension}"))

    def __iter__(self) -> Iterator[K]:
        """Iterate over all keys.

        Returns:
            Iterator over keys in the repository
        """
        for file in self._folder.glob(f"*.{self._extension}"):
            yield (self._key_type(file.stem))  # type: ignore[misc]

    def __getitem__(self, key: K) -> V:
        """Retrieve value by key.

        Args:
            key: The key to look up

        Returns:
            The value associated with the key

        Raises:
            KeyError: If key does not exist
        """
        file_path = self._make_path(key)
        if not file_path.exists():
            raise KeyError(f"Item with key '{key}' not found")

        return cast(V, read_value(file_path, self._mode, self._unmarshal))
