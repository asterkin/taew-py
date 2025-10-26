import unittest
from io import BytesIO
from pathlib import Path

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestOptionalUnionStreaming(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.union.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_args=(type(None), str))

    def test_round_trip_optional_str(self) -> None:
        configure = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces.main import Bind

        root = InspectRoot(Path("."))
        bind = Bind(root)

        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)

        for value in (None, "", "hello"):
            with self.subTest(value=value):
                stream = BytesIO()
                write(value, stream)
                stream.seek(0)
                restored = read(stream)
                self.assertEqual(restored, value)


if __name__ == "__main__":
    unittest.main()
