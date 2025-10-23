"""Configurator for RAM-based storage adapters.

Provides configuration support for both DataRepository and MutableDataRepository
implementations using in-memory dictionaries.
"""

from dataclasses import dataclass, field

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for RAM-based storage adapters.

    Provides simple configuration for in-memory storage. Unlike dir adapters,
    RAM adapters don't require serialization or other complex configuration.
    """

    _ports: str = field(kw_only=True, default="ports")
    _root_marker: str = field(kw_only=True, default="/adapters")
    _values: dict[str, object] = field(
        kw_only=True, default_factory=lambda: dict[str, object]()
    )

    def _collect_kwargs(self) -> dict[str, object]:
        """Collects keyword arguments for configuring the adapter.

        Returns:
            dict[str, object]: A dictionary of keyword arguments.
        """
        return self._values
