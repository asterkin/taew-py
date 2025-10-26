import unittest
from io import BytesIO
from pathlib import Path
from typing import cast

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestSetStreaming(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.set.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_args=(int,))

    def test_round_trip_int_set(self) -> None:
        configure = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces.bind import Bind

        root = InspectRoot(Path("."))
        bind = Bind(root)

        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)

        cases: list[set[int]] = [
            set(),
            {0},
            {1, 2, 3, 4},
        ]
        for value in cases:
            with self.subTest(value=value):
                stream = BytesIO()
                write(value, stream)
                stream.seek(0)
                restored = read(stream)
                self.assertIsInstance(restored, set)
                typed_restored = cast(set[int], restored)
                self.assertEqual(typed_restored, value)

    def test_duplicate_detection(self) -> None:
        configure = self._get_configure()
        ports = configure()

        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces.bind import Bind

        root = InspectRoot(Path("."))
        bind = Bind(root)

        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)

        # Build a forged payload with duplicates using the underlying writers
        forged = BytesIO()
        length_writer = getattr(write, "_write_len")
        item_writer = getattr(write, "_write_item")
        length_writer(3, forged)
        for item in (1, 2, 1):
            item_writer(item, forged)
        forged.seek(0)

        with self.assertRaises(ValueError):
            read(forged)


if __name__ == "__main__":
    unittest.main()
