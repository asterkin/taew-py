import unittest
from typing import cast
from io import BytesIO
from pathlib import Path

from taew.domain.configuration import PortConfigurationDict
from taew.ports import (
    for_streaming_objects as for_streaming_port,
    for_serializing_objects as for_serializing_port,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.adapters.launch_time.for_binding_interfaces.bind import bind
from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)


class TestIntStreamConfigureVariable(unittest.TestCase):
    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.int.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        # Use _width=0 to indicate variable-length integer streaming
        return Configure(_width=0, _byte_order="big", _signed=True)

    def test_builds_variable_length_ports_mapping(self) -> None:
        configure = self._get_configure()
        mapping = configure()

        # Top-level is the bytes streamer
        self.assertIn(for_streaming_port, mapping)
        pc = mapping[for_streaming_port]
        self.assertIsInstance(pc, PortConfigurationDict)
        pc_dict = cast(PortConfigurationDict, pc)

        self.assertEqual(pc_dict.adapter, "taew.adapters.python.bytes")
        # Bytes streamer has no direct kwargs in our configuration
        self.assertEqual(pc_dict.kwargs, {})

        # Nested ports should include length (streaming) and int serializer
        nested = pc_dict.ports
        self.assertIn(for_streaming_port, nested)
        self.assertIn(for_serializing_port, nested)

        # Validate length nested config: fixed-width int of 1 byte, big-endian, unsigned
        len_pc = nested[for_streaming_port]
        self.assertIsInstance(len_pc, PortConfigurationDict)
        len_pc_dict = cast(PortConfigurationDict, len_pc)
        self.assertEqual(len_pc_dict.adapter, "taew.adapters.python.int")
        self.assertEqual(
            len_pc_dict.kwargs, {"_width": 1, "_byte_order": "big", "_signed": False}
        )

        # Validate serializer nested config: minimal-width int serializer
        ser_pc = nested[for_serializing_port]
        self.assertIsInstance(ser_pc, PortConfigurationDict)
        ser_pc_dict = cast(PortConfigurationDict, ser_pc)
        self.assertEqual(ser_pc_dict.adapter, "taew.adapters.python.int")
        self.assertEqual(ser_pc_dict.kwargs, {"_byte_order": "big", "_signed": True})

    def _bind(self, cfg: ConfigureProtocol) -> tuple[WriteProtocol, ReadProtocol]:
        ports = cfg()
        # Configure for_browsing_code_tree
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        write: WriteProtocol = bind(WriteProtocol, ports)
        read: ReadProtocol = bind(ReadProtocol, ports)
        return write, read

    def test_round_trip_variable_length(self) -> None:
        cfg = self._get_configure()
        write, read = self._bind(cfg)

        values = [
            0,
            1,
            127,
            128,
            255,
            256,
            -1,
            -128,
            -129,
            2**31 - 1,
            -(2**31),
        ]

        for value in values:
            with self.subTest(value=value):
                stream = BytesIO()
                write(value, stream)
                stream.seek(0)
                out = read(stream)
                self.assertEqual(out, value)


if __name__ == "__main__":
    unittest.main()
