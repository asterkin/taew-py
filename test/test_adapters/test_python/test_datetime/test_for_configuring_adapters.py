import unittest
import datetime as dt
from io import BytesIO
from typing import cast
from pathlib import Path

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestDatetimeConfigureIntegration(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.datetime.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure()

    def _bind(self, cfg: ConfigureProtocol) -> tuple[WriteProtocol, ReadProtocol]:
        write: WriteProtocol = bind(WriteProtocol, ports)
        read: ReadProtocol = bind(ReadProtocol, ports)
        return write, read

    def _to_naive_utc(self, value: dt.datetime) -> dt.datetime:
        if value.tzinfo is None:
            # Treat naive as UTC
            return value
        return value.astimezone(dt.timezone.utc).replace(tzinfo=None)

    def test_round_trip_various_datetimes(self) -> None:
        cfg = self._get_configure()
        write, read = self._bind(cfg)

        tzp3 = dt.timezone(dt.timedelta(hours=3))
        cases = (
            dt.datetime(1970, 1, 1, 0, 0, 0),
            dt.datetime(2021, 5, 1, 12, 34, 56, 789012),
            dt.datetime(1999, 12, 31, 23, 59, 59, 123456, tzinfo=tzp3),
        )

        for original in cases:
            with self.subTest(value=original.isoformat()):
                stream = BytesIO()
                write(original, stream)
                stream.seek(0)
                restored = cast(dt.datetime, read(stream))
                self.assertIsInstance(restored, dt.datetime)
                expected = self._to_naive_utc(original)
                # Allow tiny rounding error due to IEEE-754
                delta = abs((restored - expected).total_seconds())
                self.assertLess(delta, 1e-6)


if __name__ == "__main__":
    unittest.main()
