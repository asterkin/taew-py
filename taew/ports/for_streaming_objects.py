from io import BytesIO
from types import TracebackType
from typing import Protocol, Self
from builtins import BaseException


class Write(Protocol):
    """Protocol for writing a single object to a byte stream.

    Implementations frame and encode one value into the provided BytesIO
    stream according to their wire format (e.g., fixed width, length prefix).
    """

    def __call__(self, obj: object, stream: BytesIO) -> None: ...


class Read(Protocol):
    """Protocol for reading a single object from a byte stream.

    Implementations parse one value from the provided BytesIO stream
    according to their wire format and return the reconstructed object.
    """

    def __call__(self, stream: BytesIO) -> object: ...


class SequenceContext(Protocol):
    """Context for incrementally building a streamed sequence value.

    Implementations accumulate elements via append() inside a context manager
    and produce the final value with value().
    """

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    def append(self, item: object) -> None: ...

    def value(self) -> object: ...
