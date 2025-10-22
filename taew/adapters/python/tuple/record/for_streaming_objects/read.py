from io import BytesIO
from taew.ports.for_streaming_objects import Read as ReadProtocol


class Read:
    """Reads fixed-arity heterogeneous tuples by delegating per position."""

    def __init__(self, *_readers: ReadProtocol) -> None:
        if not _readers:
            raise ValueError("Tuple reader requires at least one positional reader")
        self._readers = tuple(_readers)

    def __call__(self, stream: BytesIO) -> object:
        return tuple(reader(stream) for reader in self._readers)
