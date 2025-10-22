"""Configurator for directory-based storage adapters.

Provides configuration support for both DataRepository and DataSequence
implementations, supporting both binary (streaming) and text (stringizing)
serialization formats.
"""

from pathlib import Path
from typing import Any, Callable
from dataclasses import dataclass, field

from taew.domain.configuration import PortsMapping
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for directory-based storage adapters.

    Accepts a serialization configurator instance and provides nested ports
    configuration. Defers _package and _file to application-level derived classes.

    Attributes:
        _folder: Directory path for storing data files
        _extension: File extension for data files
        _serialization: Configurator instance for serialization (streaming or stringizing)
        _key_type: Callable to convert string keys to the appropriate type (for repositories)
        _marker: Path marker for root detection (set to "/adapters" for application-level use)
    """

    _folder: Path = field(kw_only=True)
    _extension: str = field(kw_only=True)
    _serialization: ConfigureProtocol = field(kw_only=True)
    _key_type: Callable[[str], Any] = field(kw_only=True, default=str)
    _ports: str = field(kw_only=True, default="ports")
    _root_marker: str = field(kw_only=True, default="/adapters")

    def _collect_kwargs(self) -> dict[str, object]:
        """Collect kwargs for adapter instantiation.

        Returns:
            Dictionary of kwargs for dir adapters
        """
        return {
            "_folder": self._folder,
            "_extension": self._extension,
            "_key_type": self._key_type,
        }

    def _nested_ports(self) -> PortsMapping:
        """Get nested ports from serialization configurator.

        Returns:
            PortsMapping containing serialization port configuration
        """
        return self._serialization()
