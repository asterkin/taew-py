from __future__ import annotations
from types import ModuleType
from typing import Any, TypeAlias
from collections.abc import Iterable
from dataclasses import dataclass, field

PortsMapping: TypeAlias = dict[ModuleType, "PortConfiguration"]
InterfaceMapping: TypeAlias = dict[str | type, "PortConfiguration"]


@dataclass(eq=False, frozen=True)
class PortConfigurationDict:
    """Configuration dictionary for port adapters."""

    # Package path to port adapter technology or mapping of types to configurations
    adapter: str | InterfaceMapping | None = None

    # Optional keyword arguments for adapter construction
    kwargs: dict[str, Any] = field(default_factory=dict[str, Any])

    # Optional recursive configuration of internal ports (used by workflows or composite adapters)
    ports: PortsMapping = field(default_factory=PortsMapping)

    # Optional root path for the port adapter
    root: str | None = None


PortConfigurationList: TypeAlias = Iterable["PortConfiguration"]
PortConfiguration: TypeAlias = str | PortConfigurationDict | PortConfigurationList
