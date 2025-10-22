import unittest
from typing import cast

from taew.domain.configuration import PortConfigurationDict
from taew.ports import for_serializing_objects as for_serializing_port
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestStrSerializeConfigure(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.str.for_serializing_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_encoding="utf-16", _errors="ignore")

    def test_builds_ports_mapping_with_kwargs(self) -> None:
        configure = self._get_configure()
        mapping = configure()

        self.assertIn(for_serializing_port, mapping)

        pc = mapping[for_serializing_port]
        self.assertIsInstance(pc, PortConfigurationDict)
        pc_dict = cast(PortConfigurationDict, pc)

        self.assertEqual(pc_dict.adapter, "taew.adapters.python.str")
        self.assertEqual(pc_dict.kwargs, {"_encoding": "utf-16", "_errors": "ignore"})


if __name__ == "__main__":
    unittest.main()
