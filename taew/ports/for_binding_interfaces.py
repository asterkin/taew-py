from typing import Protocol, TypeVar, Type
from taew.ports.for_browsing_code_tree import Class
from taew.domain.configuration import PortsMapping

T = TypeVar("T")


class Bind(Protocol):
    def __call__(self, interface: Type[T], ports: PortsMapping) -> T:
        """Bind an interface to its implementation using the provided ports configuration.

        Args:
            interface: The interface type (Protocol or ABC) to bind
            ports: Configuration mapping for port bindings

        Returns:
            An instance implementing the interface
        """
        ...

    def create_instance(
        self,
        adapter: Class,
        ports: PortsMapping,
    ) -> object:
        """Create an instance from a Class.

        If the Class represents an interface (Protocol or ABC), finds and creates
        an adapter implementation. If it's a concrete class, creates a direct instance.

        Args:
            adapter: The Class object to instantiate
            ports: Configuration mapping for port bindings

        Returns:
            Either a concrete class instance or an interface adapter
        """
        ...
