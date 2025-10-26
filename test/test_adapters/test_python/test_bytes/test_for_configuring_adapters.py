import unittest
from io import BytesIO
from pathlib import Path

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestBytesConfigureIntegration(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.bytes.for_streaming_objects.for_configuring_adapters import (
            Configure as BytesConfigure,
        )

        # Use default 2-byte length configuration
        return BytesConfigure()

    def test_bind_and_round_trip_bytes(self) -> None:
        # Build composed PortsMapping via configurator
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        # Build a code tree root and binder
        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces.bind import Bind

        root = InspectRoot(Path("."))
        bind = Bind(root)

        # Dynamically bind Write/Read adapters
        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)

        # Round-trip raw bytes
        original = b"Hello bytes streamer!"
        stream = BytesIO()
        write(original, stream)
        stream.seek(0)
        restored = read(stream)
        self.assertEqual(restored, original)


if __name__ == "__main__":
    unittest.main()
