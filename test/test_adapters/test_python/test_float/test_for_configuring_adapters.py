import unittest
from io import BytesIO
from pathlib import Path

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestFloatConfigureIntegration(unittest.TestCase):
    def _get_configure(
        self, width: int = 8, byte_order: str = "big"
    ) -> ConfigureProtocol:
        from taew.adapters.python.float.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_width=width, _byte_order=byte_order)  # type: ignore[arg-type]

    def test_bind_and_round_trip_float64_big(self) -> None:
        configure: ConfigureProtocol = self._get_configure(8, "big")
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces.bind import Bind

        root = InspectRoot(Path("."))
        bind = Bind(root)

        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)

        for value in (0.0, 1.25, -3.5, 1e308):
            with self.subTest(value=value):
                stream = BytesIO()
                write(value, stream)
                stream.seek(0)
                restored = read(stream)
                self.assertIsInstance(restored, float)
                self.assertEqual(restored, value)


if __name__ == "__main__":
    unittest.main()
