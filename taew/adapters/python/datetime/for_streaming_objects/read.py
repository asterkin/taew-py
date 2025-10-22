from dataclasses import dataclass
from io import BytesIO
import datetime as dt

from taew.ports.for_streaming_objects import Read as ReadProtocol


@dataclass(eq=False, frozen=True)
class Read:
    _read_float: ReadProtocol

    def __call__(self, stream: BytesIO) -> object:
        ts = self._read_float(stream)
        if not isinstance(ts, float):  # type: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Datetime reader expects float seconds, got {type(ts)}")
        # Build timezone-aware UTC, then return naive UTC
        aware = dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc)
        return aware.replace(tzinfo=None)
