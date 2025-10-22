from dataclasses import dataclass
from io import BytesIO
import datetime as dt

from taew.ports.for_streaming_objects import Write as WriteProtocol


@dataclass(eq=False, frozen=True)
class Write:
    _write_float: WriteProtocol

    def __call__(self, obj: object, stream: BytesIO) -> None:
        if not isinstance(obj, dt.datetime):  # type: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Unsupported type for datetime write: {type(obj)}")
        # Treat naive datetimes as UTC; convert aware to UTC
        if obj.tzinfo is None:
            aware = obj.replace(tzinfo=dt.timezone.utc)
        else:
            aware = obj.astimezone(dt.timezone.utc)
        ts = aware.timestamp()
        self._write_float(ts, stream)
