"""Directory-based MutableDataSequence implementation.

Provides read-write sequence storage backed by directory structure.
"""

from typing import Iterable, TypeVar, overload
from dataclasses import dataclass, field

from taew.ports.for_storing_data import (
    MutableDataSequence as MutableDataSequenceProtocol,
)
from .data_sequence import DataSequence
from ._common import Marshal, write_value

V = TypeVar("V")


@dataclass(eq=False, kw_only=True)
class MutableDataSequence(DataSequence[V], MutableDataSequenceProtocol[V]):
    """Directory-based mutable data sequence.

    Extends DataSequence with write operations. Supports both binary
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
        self._marshal = marshal
        # Verify that serialize and deserialize modes match
        from ._common import detect_mode

        if detect_mode(type_) != self._mode:
            raise ValueError("Serialize and deserialize protocol types must match")

    @overload
    def __getitem__(self, index: int) -> V: ...

    @overload
    def __getitem__(self, index: slice) -> MutableDataSequenceProtocol[V]: ...

    # Delegate to base implementation; overloads satisfy typing for MutableSequence
    def __getitem__(self, index: int | slice) -> MutableDataSequenceProtocol[V] | V:
        """Retrieve item(s) by index.

        Runtime returns a DataSequence for slices; typed as MutableDataSequenceProtocol
        for compatibility with MutableSequence protocol.
        """
        return super().__getitem__(index)  # type: ignore[return-value]

    @overload
    def __setitem__(self, index: int, value: V) -> None: ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[V]) -> None: ...

    def __setitem__(self, index: int | slice, value: V | Iterable[V]) -> None:
        """Set item(s) by index.

        Args:
            index: Integer index or slice
            value: Single value for int index, iterable of values for slice

        Raises:
            TypeError: If operation not supported on this view
            IndexError: If index is out of range
        """
        if self._step != 1:
            raise TypeError("assignment only supported on unit-step views")

        if isinstance(index, slice):
            raise TypeError("slice assignment is not supported")

        view_len = len(self)
        i = index
        if i < 0:
            i += view_len
        if i < 0 or i >= view_len:
            raise IndexError("sequence index out of range")

        base_index = self._start + i
        write_value(self._path(base_index), value, self._mode, self._marshal)

    @overload
    def __delitem__(self, index: int) -> None: ...

    @overload
    def __delitem__(self, index: slice) -> None: ...

    def __delitem__(self, index: int | slice) -> None:
        """Delete item(s) by index.

        Args:
            index: Integer index or slice

        Raises:
            TypeError: If operation not supported on this view
            IndexError: If index is out of range
        """
        if self._step != 1:
            raise TypeError("deletion only supported on unit-step views")

        if isinstance(index, slice):
            raise TypeError("slice deletion is not supported")

        view_len = len(self)
        i = index
        if i < 0:
            i += view_len
        if i < 0 or i >= view_len:
            raise IndexError("sequence index out of range")

        base_index = self._start + i

        # remove the target file and shift subsequent items left
        target = self._path(base_index)
        if not target.exists():
            raise IndexError("sequence index out of range")
        target.unlink()

        for j in range(base_index + 1, self._size):
            src = self._path(j)
            dst = self._path(j - 1)
            if src.exists():
                src.rename(dst)

        # update underlying size and default-view stop if applicable
        old_size = self._size
        self._size -= 1
        if self._start == 0 and self._step == 1 and self._stop == old_size:
            self._stop = self._size

    def insert(self, index: int, value: V) -> None:
        """Insert item at index.

        Args:
            index: Position to insert at
            value: Value to insert

        Raises:
            TypeError: If operation not supported on this view
        """
        if self._step != 1:
            raise TypeError("insert only supported on unit-step views")

        view_len = len(self)
        i = index
        if i < 0:
            i += view_len
        # clamp to [0, view_len]
        if i < 0:
            i = 0
        if i > view_len:
            i = view_len

        base_index = self._start + i

        # shift items right to make room
        for j in range(self._size - 1, base_index - 1, -1):
            src = self._path(j)
            dst = self._path(j + 1)
            if src.exists():
                src.rename(dst)

        # write the new item
        write_value(self._path(base_index), value, self._mode, self._marshal)

        # update size and default-view stop if applicable
        old_size = self._size
        self._size += 1
        if self._start == 0 and self._step == 1 and self._stop == old_size:
            self._stop = self._size
