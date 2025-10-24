from types import ModuleType
from dataclasses import dataclass, field
from typing import Any, get_args, get_origin

from taew.ports import for_configuring_adapters
from taew.domain.configuration import PortConfigurationDict, PortsMapping


@dataclass(eq=False, frozen=True)
class Build:
    """Build PortsMapping entries for configurator binding based on type annotations."""

    _variants: dict[type, str | dict[str, object]] = field(default_factory=lambda: {})

    def __call__(
        self,
        arg: Any,
        port: ModuleType,
    ) -> tuple[type[object], PortsMapping]:
        base, adapter_path, kwargs = self._analyse_type(arg, port)
        ports: PortsMapping = {
            for_configuring_adapters: PortConfigurationDict(
                adapter=adapter_path, kwargs=kwargs
            )
        }
        return base, ports

    def _analyse_type(
        self,
        arg: Any,
        port: ModuleType,
    ) -> tuple[type[object], str, dict[str, object]]:
        origin = get_origin(arg)

        if origin is None:
            base = arg
            if hasattr(base, "_fields"):
                adapter = "named_tuple"
                kwargs: dict[str, object] = {"_args": (arg,)}
            else:
                name_source = getattr(base, "__name__", str(base))
                adapter = name_source.lower()
                kwargs = {}
        else:
            base = origin
            name_source = getattr(base, "__name__", str(base))
            adapter = name_source.lower()
            kwargs = {"_args": get_args(arg)}

        variant_spec = self._variants.get(base)
        if variant_spec is not None:
            if isinstance(variant_spec, str):
                adapter = f"{adapter}.{variant_spec}"
            elif isinstance(variant_spec, dict):  # type: ignore
                variant_name = variant_spec.get("_variant")
                if variant_name:
                    adapter = f"{adapter}.{variant_name}"
                for key, value in variant_spec.items():
                    if key != "_variant":
                        kwargs[key] = value
            else:
                raise TypeError(
                    f"Unsupported variant specification for {base}: {variant_spec!r}"
                )

        if self._variants:
            kwargs["_variants"] = self._variants

        port_name = port.__name__.rsplit(".", 1)[-1]
        adapter_path = f"{adapter}.{port_name}"

        return base, adapter_path, kwargs
