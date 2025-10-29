from dataclasses import dataclass, field
from typing import Any

from taew.domain.configuration import PortsMapping
from taew.ports.for_browsing_code_tree import Root, Package, is_package


@dataclass(eq=False, frozen=True, kw_only=True)
class MainBase:
    _ports_mapping: PortsMapping
    _root: Root
    _cli_package: str = "adapters.cli"
    _cli_root: Package = field(init=False)

    def __post_init__(self) -> None:
        """Initialize _cli_root from _root and _cli_package."""
        # Navigate through dot-separated package path
        parts = self._cli_package.split(".")
        current: Any = self._root
        for part in parts:
            current = current[part]

        if not is_package(current):
            raise ValueError(
                f"Expected '{self._cli_package}' to be a Package, got {type(current).__name__}"
            )
        object.__setattr__(self, "_cli_root", current)
