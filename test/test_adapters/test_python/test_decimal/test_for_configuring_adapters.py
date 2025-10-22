import unittest
from io import BytesIO
from pathlib import Path
from decimal import Decimal

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestDecimalStreamingConfigureIntegration(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.decimal.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure()

    def _bind(self, cfg: ConfigureProtocol) -> tuple[WriteProtocol, ReadProtocol]:
        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces import Bind

        ports = cfg()
        root = InspectRoot(Path("."))
        bind = Bind(root)
        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)
        return write, read

    def test_round_trip_decimals(self) -> None:
        cfg = self._get_configure()
        write, read = self._bind(cfg)

        cases = (
            Decimal("0"),
            Decimal("123.456"),
            Decimal("-1.23e-8"),
            Decimal("999999999999999999999.000000000000000001"),
        )

        for original in cases:
            with self.subTest(value=str(original)):
                stream = BytesIO()
                write(original, stream)
                stream.seek(0)
                restored = read(stream)
                self.assertIsInstance(restored, Decimal)
                self.assertEqual(restored, original)


if __name__ == "__main__":
    unittest.main()
