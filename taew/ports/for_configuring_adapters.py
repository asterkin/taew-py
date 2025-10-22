from typing import Protocol

from taew.domain.configuration import PortsMapping


class Configure(Protocol):
    """Protocol for building adapter configuration mappings.

    Implementations encapsulate configuration in their own state and,
    when called with no arguments, return a composed PortsMapping that
    wires concrete adapter paths and nested port configurations.
    """

    def __call__(self) -> PortsMapping: ...
