import unittest
from typing import cast, Any
from types import ModuleType

from taew.domain.configuration import PortConfigurationDict
from taew.ports import for_building_command_parsers as for_building_command_parsers_port
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class StubFind:
    def __call__(self, arg: Any, port: ModuleType) -> tuple[type[Any], Any]:
        return object, {}


class StubBind:
    def __call__(self, interface: type[Any], ports: Any) -> Any:
        return lambda: None


class TestArgparseBuildCommandParsersConfigure(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.argparse.for_building_command_parsers.for_configuring_adapters import (
            Configure,
        )

        find_stub = StubFind()
        bind_stub = StubBind()
        return Configure(_find=find_stub, _bind=bind_stub)  # type: ignore

    def test_builds_ports_mapping(self) -> None:
        configure = self._get_configure()
        mapping = configure()

        self.assertIn(for_building_command_parsers_port, mapping)

        pc = mapping[for_building_command_parsers_port]
        self.assertIsInstance(pc, PortConfigurationDict)
        pc_dict = cast(PortConfigurationDict, pc)

        self.assertEqual(pc_dict.adapter, "taew.adapters.python.argparse")
        # BuildBase provides _find and _bind
        self.assertIn("_find", pc_dict.kwargs)
        self.assertIn("_bind", pc_dict.kwargs)


if __name__ == "__main__":
    unittest.main()
