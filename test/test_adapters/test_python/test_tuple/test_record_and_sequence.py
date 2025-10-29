import unittest
from io import BytesIO
from pathlib import Path
from typing import cast

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.adapters.launch_time.for_binding_interfaces.bind import bind


class TestTupleRecordAndSequenceStreaming(unittest.TestCase):
    """Test hybrid tuple streaming - tuple[T1, T2, T3, ...]"""

    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.tuple.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_args=(int, str, float, ...))

    def test_round_trip_hybrid_tuple(self) -> None:
        configure = self._get_configure()
        ports = configure()


        # Configure for_browsing_code_tree



        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree



        browsing_config = BrowseCodeTree(_root_path=Path("./"))()



        ports.update(browsing_config)



        



        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)

        cases = [
            (42, "hello", 3.14),  # No tail
            (42, "hello", 3.14, 1.1),  # One tail element
            (42, "hello", 3.14, 1.1, 2.2, 3.3),  # Multiple tail elements
        ]
        for value in cases:
            with self.subTest(value=value):
                stream = BytesIO()
                write(value, stream)
                stream.seek(0)
                restored = read(stream)
                self.assertIsInstance(restored, tuple)
                typed_restored = cast(
                    tuple[int, str, float, ...],  # type: ignore
                    restored,
                )
                self.assertEqual(typed_restored, value)


if __name__ == "__main__":
    unittest.main()
