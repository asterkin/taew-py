import unittest
from io import BytesIO
from pathlib import Path

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.adapters.launch_time.for_binding_interfaces.bind import bind


class TestBytesConfigureIntegration(unittest.TestCase):
    def setUp(self) -> None:
        """Clear Root cache before each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

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

        # Dynamically bind Write/Read adapters
        # Configure for_browsing_code_tree

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

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
