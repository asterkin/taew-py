"""Stateless bind function for interface binding.

This module provides a function-based implementation of interface binding,
replacing the previous class-based approach.
"""

from typing import TypeVar, Type, cast, Any

from taew.domain.configuration import PortsMapping

from ._imp import (
    get_root,
    get_port_by_interface,
    find_adapter_instance,
)

T = TypeVar("T")


def bind(interface: Type[T], adapters: PortsMapping) -> T:
    """Bind an interface to its implementation using adapter configuration.

    This is a stateless function that resolves interface types to their
    configured adapter implementations.

    Args:
        interface: The interface type (Protocol or ABC) to bind
        adapters: Configuration mapping for adapter bindings

    Returns:
        An instance implementing the interface

    Raises:
        KeyError: If the interface's port is not configured in adapters
        ValueError: If the adapter cannot be found or instantiated
    """
    # Get the root from configuration (cached)
    root = get_root(adapters)

    # Get port module for this interface
    port = get_port_by_interface(interface)

    # Check if port is configured
    if port not in adapters:
        # Special case: if requesting Bind itself, return this function
        # (wrapped to match protocol signature)
        if port.__name__.endswith("for_binding_interfaces"):
            # Create a wrapper function with proper types
            def bind_wrapper(iface: Type[Any]) -> Any:
                return bind(iface, adapters)

            return cast(T, bind_wrapper)

        # Otherwise, port is required but missing
        raise KeyError(
            f"Port module '{port.__name__}' not found in adapters mapping. "
            f"Required for interface '{interface.__name__}'"
        )

    # Find and instantiate the adapter
    return cast(T, find_adapter_instance(interface, adapters, root))
