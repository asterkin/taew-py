"""Stateless create_instance function for class instantiation.

This module provides a function-based implementation of class instantiation,
replacing the previous class-based approach.
"""

from taew.domain.configuration import PortsMapping, PortConfigurationDict
from taew.ports.for_browsing_code_tree import Class, is_interface

from ._imp import get_root, create_class_instance
from .bind import bind


def create_instance(adapter: Class, adapters: PortsMapping) -> object:
    """Create an instance from a Class object.

    If the Class represents an interface (Protocol or ABC), delegates to bind().
    If it's a concrete class, creates a direct instance with dependency injection.

    Args:
        adapter: The Class object to instantiate
        adapters: Configuration mapping for adapter bindings

    Returns:
        An instance of the class

    Raises:
        ValueError: If instance creation fails
        TypeError: If argument types don't match
    """
    try:
        if is_interface(adapter):
            # For interfaces, delegate to bind (no root needed)
            return bind(adapter.type_, adapters)  # type: ignore
        else:
            # For concrete classes, get root and instantiate directly
            root = get_root(adapters)
            port_configuration = adapters.get(adapter.py_module, PortConfigurationDict())
            return create_class_instance(adapter, port_configuration, adapters, root)

    except Exception as e:
        print(f"Error creating instance for adapter '{adapter}': {type(e)}({e})")
        raise
