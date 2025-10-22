import unittest
from typing import cast

from taew.domain.configuration import PortConfigurationDict
from taew.ports import for_streaming_objects as for_streaming_port
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestIntStreamConfigureFixed(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.int.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_width=2, _byte_order="little", _signed=True)

    def test_builds_ports_mapping_with_kwargs(self) -> None:
        configure = self._get_configure()
        mapping = configure()

        self.assertIn(for_streaming_port, mapping)

        pc = mapping[for_streaming_port]
        self.assertIsInstance(pc, PortConfigurationDict)
        pc_dict = cast(PortConfigurationDict, pc)

        self.assertEqual(pc_dict.adapter, "taew.adapters.python.int")
        self.assertEqual(
            pc_dict.kwargs, {"_width": 2, "_byte_order": "little", "_signed": True}
        )


if __name__ == "__main__":
    unittest.main()
