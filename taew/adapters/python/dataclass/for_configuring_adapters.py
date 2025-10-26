import importlib
from types import ModuleType
from dataclasses import dataclass, field, fields
from typing import Any, cast, get_args, get_origin

from taew.domain.configuration import (
    PortConfiguration,
    PortConfigurationDict,
    PortsMapping,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


@dataclass(eq=False, frozen=True, kw_only=True)
class Configure:
    """Dataclass-based configurator that auto-builds PortsMapping.

    - Adapter path: uses __package__ provided via _package
    - Root path:    uses __file__ prefix up to _marker (Linux-oriented)
    - Ports package: ports package name (default: 'taew.ports')
    - Root Marker:  path marker for root detection (default: '/taew')
    - Variants:     optional type-to-strategy mapping for adapter variants
    """

    _package: str = field(default="", init=False)
    _file: str = field(default="", init=False)
    _ports: str = "taew.ports"
    _root_marker: str = "/taew"
    _variants: dict[type, str | dict[str, object]] = field(default_factory=lambda: {})

    def _detect_port_module(self, package: str) -> ModuleType:
        """Return the taew.ports module for the given adapter package.

        Assumes the last package segment is the port name (e.g. 'for_streaming_objects').
        """

        segments = package.split(".")
        if not segments:
            raise ValueError("Invalid package name for configurator")
        port_name = segments[-1]
        port_module = f"{self._ports}.{port_name}"
        return importlib.import_module(port_module)

    def _detect_root(self) -> str:
        """Detect project root using the configured marker.

        Returns:
            Path to project root

        Raises:
            ValueError: If marker not found in file path
        """
        idx = self._file.rfind(self._root_marker)
        if idx == -1:
            raise ValueError(
                f"Cannot detect project root: '{self._root_marker}' not found in path"
            )
        return self._file[:idx]

    def _collect_kwargs(self) -> dict[str, object]:
        """Collect kwargs for adapter instantiation.

        Excludes internal configuration fields.

        Returns:
            Dictionary of kwargs for adapter
        """
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.init
            and f.name
            not in {"_package", "_file", "_ports", "_root_marker", "_variants"}
        }

    def _nested_ports(self) -> PortsMapping:
        return {}

    def _get_configurator(
        self, arg: Any, port: ModuleType
    ) -> tuple[type[object], ConfigureProtocol]:
        """Get configurator for a given type argument and port.

        Returns a tuple of (type, configurator) where type is the base type
        to be used as a key in interface mappings.
        """
        origin = get_origin(arg)

        # Determine adapter name and kwargs based on whether type is generic
        if origin is None:
            # Non-generic type
            base = arg
            # Check if this is a named tuple
            if hasattr(base, "_fields"):
                adapter = "named_tuple"
                kwargs: dict[str, object] = {"_args": (arg,)}
            else:
                name_source = getattr(base, "__name__", str(base))
                adapter = name_source.lower()
                kwargs = {}
        else:
            # Generic type like list[int], tuple[str, int], etc.
            base = origin
            name_source = getattr(base, "__name__", str(base))
            adapter = name_source.lower()
            kwargs = {"_args": get_args(arg)}

        # Apply variant strategy if specified for this type
        if base in self._variants:
            variant_spec = self._variants[base]
            if isinstance(variant_spec, str):
                # Simple string variant: just the adapter name
                adapter = f"{adapter}.{variant_spec}"
            else:
                # Dict variant: extract _variant and pass other keys as kwargs
                variant_name = variant_spec.get("_variant")
                if variant_name:
                    adapter = f"{adapter}.{variant_name}"
                # Add all keys except _variant to kwargs
                for key, value in variant_spec.items():
                    if key != "_variant":
                        kwargs[key] = value

        # Propagate variants to nested configurators
        if self._variants:
            kwargs["_variants"] = self._variants

        port_name = port.__name__.split(".")[-1]
        module_path = (
            f"taew.adapters.python.{adapter}.{port_name}.for_configuring_adapters"
        )
        module = importlib.import_module(module_path)

        configure_cls = getattr(module, "Configure")
        configurator = cast(ConfigureProtocol, configure_cls(**kwargs))
        return base, configurator

    def _configure_item(
        self, arg: Any, port: ModuleType
    ) -> tuple[type[object], PortConfiguration]:
        """Configure a single item type for the given port.

        Returns a tuple of (type, port_configuration) where type is the base type
        to be used as a key in interface mappings.
        """
        type_, configurator = self._get_configurator(arg, port)
        ports = configurator()
        return type_, ports[port]

    def __call__(self) -> PortsMapping:
        port = self._detect_port_module(self._package)
        adapter, _, _ = self._package.rpartition(".")
        return {
            port: PortConfigurationDict(
                adapter=adapter,
                kwargs=self._collect_kwargs(),
                ports=self._nested_ports(),
                root=self._detect_root(),
            )
        }
