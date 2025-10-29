"""Common internal functions for bind and create_instance.

This module contains shared helper functions used by both bind and create_instance.
It provides caching, adapter resolution, and instance creation utilities.
"""

import sys
from functools import lru_cache
from typing import Any, Type, cast

from taew.utils.strings import pascal_to_snake
from taew.domain.argument import (
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_POSITIONAL,
    KEYWORD_ONLY,
    VAR_KEYWORD,
)
from taew.domain.configuration import (
    PortConfiguration,
    PortConfigurationDict,
    PortsMapping,
)
from taew.ports.for_browsing_code_tree import (
    Root,
    Package,
    Module,
    Class,
    Argument,
    is_interface_type,
    is_class,
    is_function,
    is_package,
    is_module,
    is_interface,
    is_interface_mapping,
)


# Cache for Root instances keyed by browsing_code_tree port configuration
_root_cache: dict[int, Root] = {}


def clear_root_cache() -> None:
    """Clear the root cache. Primarily for testing purposes."""
    _root_cache.clear()


def get_root(adapters: PortsMapping) -> Root:
    """Get or create Root instance from adapters configuration.

    Looks for for_browsing_code_tree port configuration and creates/caches
    a Root instance. Uses caching for efficiency.

    Args:
        adapters: Configuration mapping containing browsing_code_tree config

    Returns:
        Root instance for code tree navigation

    Raises:
        KeyError: If for_browsing_code_tree is not configured
        ValueError: If Root cannot be created from configuration
    """
    # Find the for_browsing_code_tree port
    browsing_port = None
    for port_module in sys.modules.values():
        if hasattr(port_module, '__name__') and port_module.__name__.endswith('for_browsing_code_tree'):
            browsing_port = port_module
            break

    if browsing_port is None or browsing_port not in adapters:
        raise KeyError(
            "for_browsing_code_tree port must be configured in adapters mapping"
        )

    # Use configuration as cache key (id of the config dict)
    config = adapters[browsing_port]
    cache_key = id(config)

    if cache_key not in _root_cache:
        # Create Root instance from configuration
        # The configuration should specify the adapter (e.g., "adapters.python.inspect")
        # and we'll instantiate it
        if isinstance(config, str):
            # Simple string path - need to instantiate the Root adapter
            raise ValueError(
                "for_browsing_code_tree configuration must include instantiation parameters"
            )
        elif isinstance(config, PortConfigurationDict):
            # Should have Root class or factory in the configuration
            # For now, we'll use a simple approach - the Root should be pre-instantiated
            # and passed in the kwargs
            if '_root' in config.kwargs:
                _root_cache[cache_key] = config.kwargs['_root']
            else:
                raise ValueError(
                    "for_browsing_code_tree configuration must include '_root' in kwargs"
                )
        else:
            raise ValueError(f"Invalid for_browsing_code_tree configuration type: {type(config)}")

    return _root_cache[cache_key]


def get_port_by_interface(interface: type) -> Any:
    """Get the port module for a given interface type.

    Args:
        interface: The interface type

    Returns:
        The port module containing the interface
    """
    return _get_cached_port_module(interface.__module__)


@lru_cache(maxsize=512)
def _get_cached_port_module(module_name: str) -> Any:
    """Cache port module lookups by module name string."""
    return sys.modules[module_name]


def find_adapter_instance(
    interface: Type[Any],
    adapters: PortsMapping,
    root: Root,
) -> Any:
    """Find and instantiate an adapter for the given interface.

    This is the core adapter resolution logic extracted from the old Bind class.

    Args:
        interface: The interface type to find an adapter for
        adapters: Configuration mapping
        root: Root for code tree navigation

    Returns:
        An instance of the adapter

    Raises:
        KeyError: If port configuration is missing
        ValueError: If adapter cannot be found
    """
    port = get_port_by_interface(interface)
    port_configuration = adapters[port]
    interface_name = interface.__name__

    # Handle iterable port configuration (multiple configurations)
    if hasattr(port_configuration, "__iter__") and not isinstance(
        port_configuration, (str, PortConfigurationDict)
    ):
        return tuple(
            find_adapter_instance(interface, {port: pc}, root)
            for pc in port_configuration
        )

    # Parse configuration to get adapter path and starting point
    adapter_path, current = _parse_port_configuration_for_adapter_resolution(
        port_configuration, port, adapters, root
    )

    # Navigate to the adapter module
    adapter_module_name = interface.__module__.split(".")[-1]
    adapter_path_parts = adapter_path.split(".") + [adapter_module_name]

    for part in adapter_path_parts:
        try:
            next_item = current[part]
        except KeyError:
            raise ValueError(
                f"Invalid adapter path {adapter_path}, {part} not found"
            )
        if not (is_module(next_item) or is_package(next_item)):
            raise ValueError(
                f"Invalid adapter path: '{part}' is not a module or package"
            )
        current = next_item

    # Try different adapter resolution strategies
    snake_name = pascal_to_snake(interface_name)

    # Strategy 1: Direct class match
    adapter = _try_direct_class_adapter(
        current, interface_name, port_configuration, adapters, root
    )
    if adapter is not None:
        return adapter

    # Strategy 2: Function or nested adapters
    adapter = _try_function_or_nested_adapters(
        current, interface_name, snake_name, port_configuration, adapters, root
    )
    if adapter is not None:
        return adapter

    raise ValueError(
        f"Adapter for interface '{interface_name}' not found in '{'.'.join(adapter_path_parts)}'. "
        f"Expected class named '{interface_name}' or function/module/package named '{snake_name}'."
    )


def _parse_port_configuration_for_adapter_resolution(
    port_configuration: PortConfiguration,
    port: Any,
    adapters: PortsMapping,
    root: Root,
) -> tuple[str, Root | Package | Module]:
    """Parse port configuration for adapter resolution."""
    current: Root | Package | Module = root

    match port_configuration:
        case str():
            adapter_path = port_configuration
        case PortConfigurationDict():
            if (ap := port_configuration.adapter) is None:
                raise ValueError(
                    f"Adapter path is missing in port configuration for {port}"
                )
            match ap:
                case str():
                    adapter_path = ap
                case _:
                    raise ValueError(
                        f"Interface mapping in adapter field not yet supported for port {port}"
                    )
            # Handle alternative root if specified
            if (new_root := port_configuration.root) is not None:
                current = root.change_root(new_root)
        case _:
            raise ValueError(
                f"Invalid port configuration: {port_configuration}"
            )

    return adapter_path, current


def _try_direct_class_adapter(
    current: Root | Package | Module,
    interface_name: str,
    port_configuration: PortConfiguration,
    adapters: PortsMapping,
    root: Root,
) -> Any:
    """Try to find adapter as direct class match."""
    try:
        adapter = current[interface_name]
        if is_class(adapter):
            return create_class_instance(adapter, port_configuration, adapters, root)
    except KeyError:
        pass
    return None


def _try_function_or_nested_adapters(
    current: Root | Package | Module,
    interface_name: str,
    snake_name: str,
    port_configuration: PortConfiguration,
    adapters: PortsMapping,
    root: Root,
) -> Any:
    """Try to find adapter as function or nested class/function."""
    try:
        adapter = current[snake_name]

        # Direct function match
        if is_function(adapter):
            return adapter

        # Package or module - look for nested adapters
        if is_package(adapter) or is_module(adapter):
            # Try nested class
            nested_class = _try_nested_class_adapter(
                adapter, interface_name, port_configuration, adapters, root
            )
            if nested_class is not None:
                return nested_class

            # Try nested function
            nested_function = _try_nested_function_adapter(adapter, snake_name)
            if nested_function is not None:
                return nested_function

    except KeyError:
        pass

    return None


def _try_nested_class_adapter(
    adapter: Package | Module,
    interface_name: str,
    port_configuration: PortConfiguration,
    adapters: PortsMapping,
    root: Root,
) -> Any:
    """Try to find nested class adapter."""
    try:
        nested = adapter[interface_name]
        if is_class(nested):
            try:
                return create_class_instance(nested, port_configuration, adapters, root)
            except (ValueError, KeyError) as e:
                print(f"Error creating class instance for {nested}: {e}")
    except KeyError:
        pass
    return None


def _try_nested_function_adapter(adapter: Package | Module, snake_name: str) -> Any:
    """Try to find nested function adapter."""
    try:
        nested = adapter[snake_name]
        if is_function(nested):
            return nested
    except KeyError:
        pass
    return None


def create_class_instance(
    adapter: Class,
    port_configuration: PortConfiguration,
    adapters: PortsMapping,
    root: Root,
) -> object:
    """Create an instance of a class with dependency injection.

    Args:
        adapter: The Class to instantiate
        port_configuration: Configuration for this adapter
        adapters: Full adapters mapping
        root: Root for code tree navigation

    Returns:
        An instance of the class
    """
    args: list[Any] = []
    kwargs: dict[str, Any] = {}

    config_kwargs, adapter_ports = _parse_port_configuration_for_class_creation(
        port_configuration, adapter
    )

    constructor = adapter["__init__"]
    new_adapters = adapters | adapter_ports if adapter_ports else adapters

    # Process arguments in order to maintain positional argument order
    for arg_name, arg in constructor.items():
        if arg_name in {"self", "cls"}:
            continue
        _add_argument(arg_name, arg, config_kwargs, args, kwargs, new_adapters, root)

    return adapter(*args, **kwargs)


def _parse_port_configuration_for_class_creation(
    port_configuration: PortConfiguration,
    adapter: Class,
) -> tuple[dict[str, Any], PortsMapping]:
    """Parse port configuration for class creation, returning kwargs and adapter_ports."""
    match port_configuration:
        case str():
            return {}, {}
        case PortConfigurationDict():
            return port_configuration.kwargs, port_configuration.ports
        case _:
            raise ValueError(
                f"Unsupported port configuration type: {type(port_configuration)} "
                f"in create_class_instance for {adapter=}"
            )


def _add_argument(
    arg_name: str,
    arg: Argument,
    config_kwargs: dict[str, Any],
    args: list[Any],
    kwargs: dict[str, Any],
    adapters: PortsMapping,
    root: Root,
) -> None:
    """Add argument value to args or kwargs based on configuration and argument kind."""
    # First check if argument value is present in configuration kwargs
    if arg_name in config_kwargs:
        _add_config_value(arg_name, arg, config_kwargs[arg_name], args, kwargs)
    # If no configured value, check if it's an interface mapping
    elif interface_type := is_interface_mapping(arg):
        _add_interface_mapping(arg_name, arg, interface_type, args, kwargs, adapters, root)
    # If union of interfaces, resolve first available
    elif (union_interfaces := _extract_interface_union(arg)) is not None:
        # Check if any interface in the union has a configured port
        has_configured_port = False
        for interface in union_interfaces:
            try:
                port = get_port_by_interface(interface)
                if port is not None and port in adapters:
                    has_configured_port = True
                    break
            except Exception:
                continue

        # If no port is configured and argument has default, skip allocation
        if not has_configured_port and not arg.default.is_empty():
            # Leave unset to use default
            pass
        else:
            _add_interface_argument(arg_name, arg, args, kwargs, adapters, root)
    # If no configured value, check if it's an interface or has default
    elif is_interface(arg):
        # Try to allocate interface, but if it fails and there's a default, use the default
        if not arg.default.is_empty():
            # Try allocation, but allow fallback to default
            try:
                _add_interface_argument(arg_name, arg, args, kwargs, adapters, root)
            except Exception:
                # Allocation failed but default is available, use default
                pass
        else:
            # No default, allocation must succeed
            _add_interface_argument(arg_name, arg, args, kwargs, adapters, root)
    # If no configured value and not an interface, check if required
    elif arg.default.is_empty() and arg.kind in [
        POSITIONAL_ONLY,
        POSITIONAL_OR_KEYWORD,
        KEYWORD_ONLY,
    ]:
        raise ValueError(
            f"Configuration error: required parameter '{arg_name}' "
            f"is missing from configuration and has no default value"
        )


def _place_argument_value(
    arg_name: str,
    arg: Argument,
    value: Any,
    args: list[Any],
    kwargs: dict[str, Any],
) -> None:
    """Place argument value in args or kwargs based on argument kind."""
    if arg.kind in [POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD]:
        args.append(value)
    elif arg.kind == VAR_POSITIONAL:
        if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
            args.extend(value)
        else:
            args.append(value)
    elif arg.kind == KEYWORD_ONLY:
        kwargs[arg_name] = value
    elif arg.kind == VAR_KEYWORD:
        if isinstance(value, dict):
            kwargs.update(cast(dict[str, Any], value))
        else:
            kwargs[arg_name] = value


def _add_config_value(
    arg_name: str,
    arg: Argument,
    value: Any,
    args: list[Any],
    kwargs: dict[str, Any],
) -> None:
    """Add configured value to args or kwargs with type validation."""
    if not arg.has_valid_type(value):
        raise TypeError(
            f"Configuration error: parameter '{arg_name}' expects "
            f"{arg.annotation} but got {type(value).__name__} "
            f"(value: {repr(value)})"
        )
    _place_argument_value(arg_name, arg, value, args, kwargs)


def _add_interface_argument(
    arg_name: str,
    arg: Argument,
    args: list[Any],
    kwargs: dict[str, Any],
    adapters: PortsMapping,
    root: Root,
) -> None:
    """Allocate interface and add to args or kwargs based on argument kind."""
    allocated_interface = _allocate_interface_argument(arg, adapters, arg_name, root)
    _place_argument_value(arg_name, arg, allocated_interface, args, kwargs)


def _add_interface_mapping(
    arg_name: str,
    arg: Argument,
    interface: type,
    args: list[Any],
    kwargs: dict[str, Any],
    adapters: PortsMapping,
    root: Root,
) -> None:
    """Build interface mapping and add to args or kwargs based on argument kind."""
    port = get_port_by_interface(interface)
    port_config = adapters[port]

    # Interface mapping requires type-based adapter configuration
    if not isinstance(port_config, PortConfigurationDict):
        raise ValueError(
            f"Interface mapping parameter '{arg_name}' requires PortConfigurationDict "
            f"for port {port.__name__}, got {type(port_config)}"
        )

    if not isinstance(port_config.adapter, dict):
        raise ValueError(
            f"Interface mapping parameter '{arg_name}' requires adapter mapping "
            f"for port {port.__name__}, got adapter: {port_config.adapter}"
        )

    # Build the interface mapping
    adapters_mapping: dict[Any, Any] = {
        key: find_adapter_instance(interface, adapters | {port: config}, root)
        for key, config in port_config.adapter.items()
    }
    _place_argument_value(arg_name, arg, adapters_mapping, args, kwargs)


def _extract_interface_union(arg: Argument) -> tuple[type, ...] | None:
    """Detect tuple[Union[InterfaceA|InterfaceB|...], type] in arg.spec."""
    from typing import get_args

    origin, args_spec = arg.spec
    if origin is not tuple:
        return None
    if len(args_spec) != 2:
        return None
    union_type, target_type = args_spec
    # Second entry must be a type
    if not isinstance(target_type, type):
        return None
    # Extract Union items robustly
    union_members = get_args(union_type)
    if not union_members:
        return None
    # Validate all are interface types
    if not all(isinstance(t, type) and is_interface_type(t) for t in union_members):
        raise ValueError(
            "All union members must be interface types (Protocol or ABC)"
        )
    return cast(tuple[type, ...], union_members)


def _resolve_union_interfaces(
    interfaces: tuple[type, ...],
    adapters: PortsMapping,
    arg_name: str,
    root: Root,
) -> Any:
    """Resolve the first available adapter for a union of interfaces."""
    for iface in interfaces:
        port = get_port_by_interface(iface)
        if port in adapters:
            try:
                adapter = find_adapter_instance(iface, adapters, root)
                return (adapter, iface)
            except Exception:
                # Try next interface if resolution fails
                continue
    raise ValueError(
        f"No adapter found for any interface in union for argument '{arg_name}'"
    )


def _allocate_interface_argument(
    arg: Any,
    adapters: PortsMapping,
    arg_name: str,
    root: Root,
) -> Any:
    """Dynamically allocate an interface argument."""
    try:
        # Handle interface union pattern first
        if (interfaces := _extract_interface_union(arg)) is not None:
            return _resolve_union_interfaces(interfaces, adapters, arg_name, root)

        # Fallback: single interface
        arg_interface = arg.annotation
        return find_adapter_instance(arg_interface, adapters, root)
    except Exception:
        raise
