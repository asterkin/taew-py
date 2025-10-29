import unittest
from io import BytesIO
from pathlib import Path

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.adapters.launch_time.for_binding_interfaces.bind import bind


class TestBoolChoicesConfigureIntegration(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.bool.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure()

    def test_bind_and_round_trip_bool(self) -> None:
        configure: ConfigureProtocol = self._get_configure()
        ports = configure()

        # Configure for_browsing_code_tree

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)

        for original in (False, True):
            with self.subTest(value=original):
                stream = BytesIO()
                write(original, stream)
                stream.seek(0)
                restored = read(stream)
                self.assertEqual(restored, original)


if __name__ == "__main__":
    unittest.main()
