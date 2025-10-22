import sys
from dataclasses import dataclass
from collections.abc import Iterable

from taew.utils.strings import pascal_to_snake
from typing import TypeVar, Type, cast, Any, get_args
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

T = TypeVar("T")


@dataclass
class Bind:
    _root: Root

    def _get_port_by_interface(self, interface: type) -> Any:
        """Return the port module for a given interface type."""
        return sys.modules[interface.__module__]

    def _extract_interface_union(self, arg: Argument) -> tuple[type, ...] | None:
        """Detect tuple[Union[InterfaceA|InterfaceB|...], type] in arg.spec.

        Guard pattern:
        - spec origin must be tuple
        - spec args must be length 2
        - first arg must be a Union (PEP 604 UnionType) and second must be type
        - all Union members must be interface types (Protocol or ABC)
        Returns the tuple of interface types on success, otherwise None.
        """
        origin, args = arg.spec
        if origin is not tuple:
            return None
        if len(args) != 2:
            return None
        union_type, target_type = args
        # Second entry must be a type; union is validated by get_args below
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
        self, interfaces: tuple[type, ...], ports: PortsMapping, arg_name: str
    ) -> Any:
        """Resolve the first available adapter for a union of interfaces.

        Scans interfaces in order; for each interface whose port is present in
        the provided ports mapping, attempts to resolve an adapter. Returns the
        first successfully resolved adapter. Raises ValueError if none resolve.
        """
        for iface in interfaces:
            port = self._get_port_by_interface(iface)
            if port in ports:
                try:
                    adapter = cast(Any, self._find_adapter(iface, ports))
                    return (adapter, iface)
                except Exception:
                    # Try next interface if resolution fails
                    continue
        raise ValueError(
            f"No adapter found for any interface in union for argument '{arg_name}'"
        )

    def _allocate_interface_argument(
        self, arg: Any, ports: PortsMapping, arg_name: str
    ) -> Any:
        """Dynamically allocate an interface argument."""
        try:
            # Handle interface union pattern first
            if (interfaces := self._extract_interface_union(arg)) is not None:
                return self._resolve_union_interfaces(interfaces, ports, arg_name)

            # Fallback: single interface
            arg_interface = arg.annotation
            return cast(Any, self._find_adapter(arg_interface, ports))
        except Exception:
            raise

    def _parse_port_configuration_for_class_creation(
        self, port_configuration: PortConfiguration, adapter: Class
    ) -> tuple[dict[str, Any], PortsMapping]:
        """Parse port configuration for class creation, returning kwargs and adapter_ports."""
        match port_configuration:
            case str():
                return {}, {}
            case PortConfigurationDict():
                return port_configuration.kwargs, port_configuration.ports
            case _:
                raise ValueError(
                    f"Unsupported port configuration type: {type(port_configuration)} in create_class_instance for {adapter=}"
                )

    def _create_class_instance(
        self,
        adapter: Class,
        port_configuration: PortConfiguration,
        ports: PortsMapping,
    ) -> object:
        args = list[Any]()
        kwargs = dict[str, Any]()

        config_kwargs, adapter_ports = (
            self._parse_port_configuration_for_class_creation(
                port_configuration, adapter
            )
        )

        constructor = adapter["__init__"]
        new_ports = ports | adapter_ports if adapter_ports else ports

        # Process arguments in order to maintain positional argument order
        for arg_name, arg in constructor.items():
            if arg_name in {"self", "cls"}:
                continue
            self._add_argument(arg_name, arg, config_kwargs, args, kwargs, new_ports)
        return adapter(*args, **kwargs)

    def create_instance(
        self,
        adapter: Class,
        ports: PortsMapping,
    ) -> object:
        """Create an instance from a Class.

        If the Class represents an interface (Protocol or ABC), finds and creates
        an adapter implementation. If it's a concrete class, creates a direct instance.
        """
        try:
            if is_interface(adapter):
                return self._find_adapter(adapter.type_, ports)  # type: ignore[return-value]
            else:
                port_configuration = ports.get(
                    adapter.py_module, PortConfigurationDict()
                )
                return self._create_class_instance(adapter, port_configuration, ports)
        except Exception as e:
            print(f"Error creating instance for adapter '{adapter}': {type(e)}({e})")
            raise

    def _add_argument(
        self,
        arg_name: str,
        arg: Argument,
        config_kwargs: dict[str, Any],
        args: list[Any],
        kwargs: dict[str, Any],
        ports: PortsMapping,
    ) -> None:
        """Add argument value to args or kwargs based on configuration and argument kind.

        Notes on interface arguments and defaults:
        - If an argument is an interface (Protocol/ABC) and the corresponding
          port is configured under ``ports``, an adapter is resolved and injected.
        - If no configuration is provided for that interface's port and the
          argument declares a default value, allocation is skipped so the
          constructor's default may apply (useful for adapters with sensible
          in‑class defaults such as identity behavior).
        - If no configuration is provided and the argument has no default, a
          ValueError is raised (the parameter is required).
        """
        # First check if argument value is present in configuration kwargs
        if arg_name in config_kwargs:
            self._add_config_value(arg_name, arg, config_kwargs[arg_name], args, kwargs)
        # If no configured value, check if it's an interface mapping
        elif interface_type := is_interface_mapping(arg):
            self._add_interface_mapping(
                arg_name, arg, interface_type, args, kwargs, ports
            )
        # If union of interfaces, resolve first available
        elif (union_interfaces := self._extract_interface_union(arg)) is not None:
            # Check if any interface in the union has a configured port
            has_configured_port = False
            for interface in union_interfaces:
                try:
                    port = self._get_port_by_interface(interface)
                    if port is not None and port in ports:
                        has_configured_port = True
                        break
                except Exception:
                    continue

            # If no port is configured and argument has default, skip allocation
            if not has_configured_port and not arg.default.is_empty():
                # Leave unset to use default
                pass
            else:
                self._add_interface_argument(arg_name, arg, args, kwargs, ports)
        # If no configured value, check if it's an interface or has default
        elif is_interface(arg):
            # If port for this interface is not configured and a default exists,
            # skip allocation to let the constructor default apply.
            # Try to allocate interface, but if it fails and there's a default, use the default
            if not arg.default.is_empty():
                # Try allocation, but allow fallback to default
                try:
                    self._add_interface_argument(arg_name, arg, args, kwargs, ports)
                except Exception:
                    # Allocation failed but default is available, use default
                    pass
            else:
                # No default, allocation must succeed
                self._add_interface_argument(arg_name, arg, args, kwargs, ports)
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
        self,
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
        self,
        arg_name: str,
        arg: Argument,
        value: Any,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> None:
        """Add configured value to args or kwargs with type validation and placement logic."""
        if not arg.has_valid_type(value):
            raise TypeError(
                f"Configuration error: parameter '{arg_name}' expects "
                f"{arg.annotation} but got {type(value).__name__} "
                f"(value: {repr(value)})"
            )

        self._place_argument_value(arg_name, arg, value, args, kwargs)

    def _add_interface_argument(
        self,
        arg_name: str,
        arg: Argument,
        args: list[Any],
        kwargs: dict[str, Any],
        ports: PortsMapping,
    ) -> None:
        """Allocate interface and add to args or kwargs based on argument kind."""
        allocated_interface = self._allocate_interface_argument(arg, ports, arg_name)
        self._place_argument_value(arg_name, arg, allocated_interface, args, kwargs)

    def _add_interface_mapping(
        self,
        arg_name: str,
        arg: Argument,
        interface: type,
        args: list[Any],
        kwargs: dict[str, Any],
        ports: PortsMapping,
    ) -> None:
        """Build interface mapping and add to args or kwargs based on argument kind."""
        port = self._get_port_by_interface(interface)
        port_config = ports[port]

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
            key: self._find_adapter(interface, ports | {port: config})
            for key, config in port_config.adapter.items()
        }
        self._place_argument_value(arg_name, arg, adapters_mapping, args, kwargs)

    def _parse_port_configuration_for_adapter_resolution(
        self, port_configuration: PortConfiguration, port: Any, ports: PortsMapping
    ) -> tuple[str, Root | Package | Module]:
        """Parse port configuration for adapter resolution, returning adapter_path and current root."""
        current: Root | Package | Module = self._root

        match port_configuration:
            case str():
                adapter_path = port_configuration
            case PortConfigurationDict():
                if (ap := port_configuration.adapter) is None:
                    raise ValueError(
                        f"Adapter path is missing in port configuration for {port} in {ports}"
                    )
                match ap:
                    case str():
                        adapter_path = ap
                    case _:  # Mapping[Any, PortConfiguration]
                        # TODO: Handle interface mapping in adapter selection
                        # For now, we don't support this at the port level
                        raise ValueError(
                            f"Interface mapping in adapter field not yet supported for port {port}"
                        )
                # Handle alternative root if specified, then traverse adapter path
                if (new_root := port_configuration.root) is not None:
                    current = self._root.change_root(new_root)
            case _:
                raise ValueError(
                    f"Invalid port configuration: {port_configuration} in _find_adapter"
                )

        return adapter_path, current

    def _try_direct_class_adapter(
        self,
        current: Root | Package | Module,
        interface_name: str,
        port_configuration: PortConfiguration,
        ports: PortsMapping,
    ) -> Any:
        """Try to find adapter as direct class match."""
        try:
            adapter = current[interface_name]
            if is_class(adapter):
                return self._create_class_instance(adapter, port_configuration, ports)
        except KeyError:
            pass
        return None

    def _try_function_or_nested_adapters(
        self,
        current: Root | Package | Module,
        interface_name: str,
        snake_name: str,
        port_configuration: PortConfiguration,
        ports: PortsMapping,
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
                if (
                    nested_class := self._try_nested_class_adapter(
                        adapter, interface_name, port_configuration, ports
                    )
                ) is not None:
                    return nested_class

                # Try nested function
                if (
                    nested_function := self._try_nested_function_adapter(
                        adapter, snake_name
                    )
                ) is not None:
                    return nested_function

        except KeyError:
            pass

    def _try_nested_class_adapter(
        self,
        adapter: Package | Module,
        interface_name: str,
        port_configuration: PortConfiguration,
        ports: PortsMapping,
    ) -> Any:
        """Try to find nested class adapter."""
        try:
            nested = adapter[interface_name]
            if is_class(nested):
                try:
                    return self._create_class_instance(
                        nested, port_configuration, ports
                    )
                except (ValueError, KeyError) as e:
                    print(f"Error creating class instance for {nested}: {e}")
        except KeyError:
            pass
        return None

    def _try_nested_function_adapter(
        self, adapter: Package | Module, snake_name: str
    ) -> Any:
        """Try to find nested function adapter."""
        try:
            nested = adapter[snake_name]
            if is_function(nested):
                return nested
        except KeyError:
            pass
        return None

    def _find_adapter(self, interface: Type[T], ports: PortsMapping) -> T | Iterable[T]:
        port = self._get_port_by_interface(interface)
        port_configuration = ports[port]
        interface_name = interface.__name__
        # Handle iterable port configuration (multiple configurations)
        if hasattr(port_configuration, "__iter__") and not isinstance(
            port_configuration, (str, PortConfigurationDict)
        ):
            # TODO: type annotation error because of recursion
            return tuple(
                self._find_adapter(interface, {port: pc})  # type: ignore
                for pc in port_configuration
            )  # type: ignore[return-value]

        adapter_path, current = self._parse_port_configuration_for_adapter_resolution(
            port_configuration, port, ports
        )
        adapter_module_name = interface.__module__.split(".")[-1]
        adapter_path_parts = adapter_path.split(".") + [adapter_module_name]
        for part in adapter_path_parts:
            try:
                next = current[part]
            except KeyError:
                raise ValueError(
                    f"Invalid adapter path {adapter_path}, {part} not found"
                )
            if not (is_module(next) or is_package(next)):
                raise ValueError(
                    f"Invalid adapter path: '{part}' is not a module or package"
                )
            current = next

        # Try different adapter resolution strategies
        snake_name = pascal_to_snake(interface_name)

        # Strategy 1: Direct class match
        if (
            adapter := self._try_direct_class_adapter(
                current, interface_name, port_configuration, ports
            )
        ) is not None:
            return cast(T, adapter)

        # Strategy 2: Function or nested adapters
        if (
            adapter := self._try_function_or_nested_adapters(
                current, interface_name, snake_name, port_configuration, ports
            )
        ) is not None:
            return cast(T, adapter)

        raise ValueError(
            f"Adapter for interface '{interface_name}' not found in '{'.'.join(adapter_path_parts)}'. "
            "Expected class named '{0}' or function/module/package named '{1}'.".format(
                interface_name, snake_name
            )
        )

    def __call__(self, interface: Type[T], ports: PortsMapping) -> T:
        # TODO: type annotation error because of recursion
        return self._find_adapter(interface, ports)  # type: ignore
