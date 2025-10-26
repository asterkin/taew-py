import unittest
from typing import Any
from collections.abc import Callable

from taew.domain.configuration import PortConfigurationDict, PortsMapping
from taew.adapters.python.dataclass.for_finding_configurations.find import Find
from taew.ports import (
    for_configuring_adapters as configure_port,
    for_stringizing_objects as stringizing_port,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class StubBuild:
    def __init__(self, ports: PortsMapping, base: type[Any]):
        self._ports = ports
        self._base = base
        self.calls: list[tuple[Any, Any]] = []

    def __call__(self, arg: Any, port: Any) -> tuple[type[Any], PortsMapping]:
        self.calls.append((arg, port))
        return self._base, self._ports


class StubConfigurator:
    def __init__(self, ports: PortsMapping):
        self._ports = ports

    def __call__(self) -> PortsMapping:
        return self._ports


class StubBind:
    def __init__(
        self, configurator_factory: Callable[[PortsMapping], StubConfigurator]
    ):
        self._configurator_factory = configurator_factory
        self.calls = list[tuple[type[Any], PortsMapping]]()

    def __call__(self, interface: type[Any], ports: PortsMapping) -> ConfigureProtocol:
        self.calls.append((interface, ports))
        return self._configurator_factory(ports)


class TestFindConfigurator(unittest.TestCase):
    def test_find_returns_configuration(self) -> None:
        configured_ports: PortsMapping = {
            stringizing_port: PortConfigurationDict(
                adapter="int.for_stringizing_objects"
            )
        }

        builder_ports: PortsMapping = {
            configure_port: PortConfigurationDict(adapter="int.for_stringizing_objects")
        }

        builder = StubBuild(builder_ports, int)
        bind = StubBind(lambda ports: StubConfigurator(configured_ports))  # type: ignore

        finder = Find(_bind=bind, _build_ports_mapping=builder)  # type: ignore

        base, configuration = finder(int, stringizing_port)

        self.assertIs(base, int)
        self.assertIs(configuration, configured_ports[stringizing_port])

        self.assertEqual(builder.calls, [(int, stringizing_port)])
        self.assertEqual(len(bind.calls), 1)
        interface, ports_passed = bind.calls[0]
        self.assertIs(interface, ConfigureProtocol)
        self.assertIs(ports_passed, builder_ports)

    def test_find_missing_port_raises(self) -> None:
        builder_ports: PortsMapping = {
            configure_port: PortConfigurationDict(adapter="int.for_streaming_objects")
        }

        builder = StubBuild(builder_ports, int)
        bind = StubBind(lambda ports: StubConfigurator({}))

        finder = Find(_bind=bind, _build_ports_mapping=builder)  # type: ignore

        with self.assertRaises(KeyError):
            finder(int, stringizing_port)


if __name__ == "__main__":
    unittest.main()
