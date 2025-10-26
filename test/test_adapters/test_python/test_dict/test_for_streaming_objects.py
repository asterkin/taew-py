import unittest
from io import BytesIO
from pathlib import Path
from typing import cast

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestDictStreaming(unittest.TestCase):
    """Test dict streaming - dict[K, V]"""

    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.dict.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_args=(str, int))

    def test_round_trip_str_int_dict(self) -> None:
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

        cases = [
            {},
            {"a": 1},
            {"foo": 42, "bar": 99, "baz": 0},
        ]
        for value in cases:
            with self.subTest(value=value):
                stream = BytesIO()
                write(value, stream)
                stream.seek(0)
                restored = read(stream)
                self.assertIsInstance(restored, dict)
                typed_restored = cast(dict[str, int], restored)
                self.assertEqual(typed_restored, value)


if __name__ == "__main__":
    unittest.main()
