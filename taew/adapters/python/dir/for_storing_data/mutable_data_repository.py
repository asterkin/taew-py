"""Directory-based MutableDataRepository implementation.

Provides read-write key-value storage backed by directory structure.
"""

from typing import TypeVar
from dataclasses import dataclass, field

from taew.ports.for_storing_data import (
    MutableDataRepository as MutableDataRepositoryProtocol,
)
from .data_repository import DataRepository
from ._common import Marshal, write_value, detect_mode

K = TypeVar("K")
V = TypeVar("V")


@dataclass(eq=False, frozen=True)
class MutableDataRepository(DataRepository[K, V], MutableDataRepositoryProtocol[K, V]):
    """Directory-based mutable data repository.

    Extends DataRepository with write operations. Supports both binary
    (streaming) and text (stringizing) serialization formats.

    Attributes:
        _serialize: Tuple of (type, marshaler) for serialization
    """

    _serialize: tuple[Marshal, type] = None  # type: ignore[assignment]
    _marshal: Marshal = field(init=False)

    def __post_init__(self) -> None:
        """Initialize and validate configuration."""
        super().__post_init__()
        marshal, type_ = self._serialize
        object.__setattr__(self, "_marshal", marshal)
        # Verify that serialize and deserialize modes match
        if detect_mode(type_) != self._mode:
            raise ValueError("Serialize and deserialize protocol types must match")

    def __setitem__(self, key: K, value: V) -> None:
        """Store value under key.

        Args:
            key: The key to store under
            value: The value to store
        """
        # Ensure the folder exists
        self._folder.mkdir(parents=True, exist_ok=True)

        file_path = self._make_path(key)
        write_value(file_path, value, self._mode, self._marshal)

    def __delitem__(self, key: K) -> None:
        """Delete item by key.

        Args:
            key: The key to delete

        Raises:
            KeyError: If key does not exist
        """
        file_path = self._make_path(key)
        try:
            file_path.unlink()
        except FileNotFoundError:
            raise KeyError(f"Key '{key}' not found")
