"""Port interfaces for binding and instantiation."""

from typing import Protocol, TypeVar, Type
from taew.ports.for_browsing_code_tree import Class
from taew.domain.configuration import PortsMapping

T = TypeVar("T")


class Bind(Protocol):
    """Bind an interface to its implementation using adapter configuration."""

    def __call__(self, interface: Type[T], adapters: PortsMapping) -> T:
        """Bind an interface to its implementation.

        Args:
            interface: The interface type (Protocol or ABC) to bind
            adapters: Configuration mapping for adapter bindings

        Returns:
            An instance implementing the interface
        """
        ...


class CreateInstance(Protocol):
    """Create an instance from a Class object."""

    def __call__(
        self,
        adapter: Class,
        adapters: PortsMapping,
    ) -> object:
        """Create an instance from a Class.

        Args:
            adapter: The Class object to instantiate
            adapters: Configuration mapping for adapter bindings

        Returns:
            An instance of the class
        """
        ...
