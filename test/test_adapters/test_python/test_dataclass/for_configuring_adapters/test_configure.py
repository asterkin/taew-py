import unittest
from typing import cast
from importlib import import_module

from taew.domain.configuration import PortConfigurationDict
from taew.ports import for_configuring_adapters as for_configuring_port
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestDataclassConfigure(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        # Use the base module's __file__ to ensure '/taew' exists in path
        base_mod = import_module(
            "taew.adapters.python.dataclass.for_configuring_adapters"
        )
        base_file_opt = getattr(base_mod, "__file__", None)
        if base_file_opt is None:
            self.fail("Base module has no __file__")
        fake_file: str = cast(str, base_file_opt)

        from .for_configuring_adapters import Configure

        cfg = Configure(_alpha=7, _name="hello")
        object.__setattr__(
            cfg, "_package", "taew.adapters.python.test.for_configuring_adapters"
        )
        object.__setattr__(cfg, "_file", fake_file)
        return cfg

    def test_builds_expected_ports_mapping(self) -> None:
        configure = self._get_configure()
        mapping = configure()

        # Validate top-level mapping key (port module)
        self.assertIn(for_configuring_port, mapping)

        pc = mapping[for_configuring_port]
        self.assertIsInstance(pc, PortConfigurationDict)
        pc_dict = cast(PortConfigurationDict, pc)
        self.assertEqual(pc_dict.adapter, "taew.adapters.python.test")

        # Root should be prefix up to '/taew'
        base_mod = import_module(
            "taew.adapters.python.dataclass.for_configuring_adapters"
        )
        base_file_opt = getattr(base_mod, "__file__", None)
        if base_file_opt is None:
            self.fail("Base module has no __file__")
        base_file = cast(str, base_file_opt)
        idx = base_file.rfind("/taew")
        self.assertGreater(idx, -1)
        root_expected = base_file[:idx]
        self.assertEqual(pc_dict.root, root_expected)

        # Kwargs should include only declared custom fields
        self.assertEqual(pc_dict.kwargs, {"_alpha": 7, "_name": "hello"})

        # No nested ports by default
        self.assertEqual(pc_dict.ports, {})


if __name__ == "__main__":
    unittest.main()
