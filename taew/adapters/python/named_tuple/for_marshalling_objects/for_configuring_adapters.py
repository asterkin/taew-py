from dataclasses import dataclass, field
from typing import Any

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.domain.configuration import (
    InterfaceMapping,
    PortConfigurationDict,
    PortsMapping,
)
from taew.ports import for_marshalling_objects as for_marshalling_objects_port


# Primitive types that are already marshallable and don't need adapters
MARSHALLABLE_PRIMITIVES = {int, str, float}


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for named tuple marshalling adapter.

    Supports optional adapter variant selection via _variants parameter.

    Args:
        _args: Tuple containing the named tuple type
        _variants: Optional dict mapping types to adapter strategy names
            Example: {datetime: 'timestamp', date: 'isoformat'}

    Example:
        from datetime import datetime, date

        # Use default adapters for all types
        Configure(_args=(MyTuple,))

        # Explicitly select adapter strategies
        Configure(
            _args=(MyTuple,),
            _variants={datetime: 'timestamp', date: 'isoformat'}
        )
    """

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

        adapter_map: InterfaceMapping = {}
        for field_name in fields:
            field_type = annotations.get(field_name, Any)
            # Skip primitive types - they'll use identity conversion
            if field_type not in MARSHALLABLE_PRIMITIVES:
                _, config = self._configure_item(
                    field_type, for_marshalling_objects_port
                )
                adapter_map[field_name] = config

        return {
            for_marshalling_objects_port: PortConfigurationDict(adapter=adapter_map)
        }
