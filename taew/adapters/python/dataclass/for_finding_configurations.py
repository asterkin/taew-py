from typing import Any
from types import ModuleType
from dataclasses import dataclass

from taew.domain.configuration import PortConfiguration
from taew.ports.for_binding_interfaces import Bind as BindProtocol
from taew.ports.for_building_config_ports_mapping import Build as BuildPortsMapping
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


@dataclass(eq=False, frozen=True)
class Find:
    """Locate configurators for annotated types using dedicated builders."""

    _bind: BindProtocol
    _build_ports_mapping: BuildPortsMapping

    def __call__(
        self,
        arg: Any,
        port: ModuleType,
    ) -> tuple[type[object], PortConfiguration]:
        base, ports_map = self._build_ports_mapping(arg, port)
        configurator = self._bind(ConfigureProtocol, ports_map)
        ports = configurator()
        return base, ports[port]
