"""Directory-based DataSequence implementation.

Provides read-only sequence storage backed by directory structure.
"""

from pathlib import Path
from dataclasses import dataclass, field
from collections.abc import Iterator, Sequence
from typing import TypeVar, cast, overload

from taew.ports.for_storing_data import DataSequence as DataSequenceProtocol
from ._common import (
    Mode,
    Unmarshal,
    detect_mode,
    make_path,
    read_value,
    validate_extension,
)

V = TypeVar("V")


@dataclass(eq=False)
class DataSequence(DataSequenceProtocol[V]):
    """Directory-based read-only data sequence.

    Implements DataSequence protocol using directory structure where sequence
    items are stored in numbered files. Supports both binary (streaming) and
    text (stringizing) serialization formats.

    Attributes:
        _folder: Directory path for storing sequence files
        _extension: File extension for sequence files
        _mode: File mode - 'b' for binary, 't' for text
        _deserialize: Tuple of (type, unmarshaler) for deserialization
        _size: Total number of items in underlying sequence
        _start: Starting index for this view
        _stop: Stopping index for this view
        _step: Step size for this view
    """

    _folder: Path
    _extension: str
    _deserialize: tuple[Unmarshal, type]
    _size: int = -1
    _start: int = 0
    _stop: int = -1
    _step: int = 1
    _unmarshal: Unmarshal = field(init=False)
    _mode: Mode = field(init=False)

    def __post_init__(self) -> None:
        """Initialize and validate configuration."""
        validate_extension(self._extension)

        unmarshal, type_ = self._deserialize
        self._unmarshal = unmarshal
        self._mode = detect_mode(type_)

        if self._size < 0:
            self._size = sum(1 for _ in self._folder.glob(f"*.{self._extension}"))

        if self._stop < 0:
            # default view spans the entire underlying sequence
            self._stop = self._size

    def _path(self, index: int) -> Path:
        """Construct file path for given index.

        Args:
            index: Sequence index

        Returns:
            Path to file for this index
        """
        return make_path(self._folder, str(index), self._extension)

    def _view_range(self) -> range:
        """Get range object for current view.

        Returns:
            Range representing the view indices
        """
        return range(self._start, self._stop, self._step)

    def __len__(self) -> int:
        """Return number of items in sequence.

        Returns:
            Count of stored items in current view
        """
        return len(self._view_range())

    def __iter__(self) -> Iterator[V]:
        """Iterate over all items in order.

        Returns:
            Iterator over sequence items
        """
        for base_index in self._view_range():
            yield cast(
                V, read_value(self._path(base_index), self._mode, self._unmarshal)
            )

    @overload
    def __getitem__(self, index: int) -> V: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[V]: ...

    def __getitem__(self, index: int | slice) -> V | Sequence[V]:
        """Retrieve item(s) by index.

        Args:
            index: Integer index or slice

        Returns:
            Single item for int index, sequence view for slice

        Raises:
            IndexError: If index is out of range
        """
        if isinstance(index, slice):
            # slice applies to the current view; compute new view relative to base indices
            view_len = len(self)
            i_start, i_stop, i_step = index.indices(view_len)
            base_start = self._start + self._step * i_start
            base_stop = self._start + self._step * i_stop
            base_step = self._step * i_step
            return DataSequence(
                _folder=self._folder,
                _extension=self._extension,
                _deserialize=self._deserialize,
                _size=self._size,
                _start=base_start,
                _stop=base_stop,
                _step=base_step,
            )

        # normalize negative index within current view
        view_len = len(self)
        i = index
        if i < 0:
            i += view_len
        if i < 0 or i >= view_len:
            raise IndexError("sequence index out of range")

        base_index = self._start + self._step * i
        return cast(V, read_value(self._path(base_index), self._mode, self._unmarshal))
