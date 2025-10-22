from dataclasses import dataclass, field
from typing import Any

from taew.domain.configuration import (
    InterfaceMapping,
    PortConfigurationDict,
    PortConfiguration,
    PortsMapping,
)
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports import for_streaming_objects as for_streaming_objects_port


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for named tuple streaming adapter."""

    _args: tuple[Any, ...] = ()
    _type: type[Any] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

        if len(self._args) != 1:
            raise ValueError(
                "Named tuple configurator requires exactly one type argument"
            )

        named_tuple_type = self._args[0]
        if not hasattr(named_tuple_type, "_fields"):
            raise TypeError(
                f"Expected named tuple type with _fields attribute, got {named_tuple_type.__name__}"
            )

        object.__setattr__(self, "_type", named_tuple_type)

    def _collect_kwargs(self) -> dict[str, object]:
        base_kwargs = super()._collect_kwargs()
        base_kwargs["_type"] = self._type
        return base_kwargs

    def _nested_ports(self) -> PortsMapping:
        fields = getattr(self._type, "_fields")
        annotations = getattr(self._type, "__annotations__", {})

        adapter_map: InterfaceMapping = {
            field_name: self._configure_field(annotations.get(field_name, Any))
            for field_name in fields
        }
        return {for_streaming_objects_port: PortConfigurationDict(adapter=adapter_map)}

    def _configure_field(self, arg: Any) -> PortConfiguration:
        _, config = self._configure_item(arg, for_streaming_objects_port)
        return config
