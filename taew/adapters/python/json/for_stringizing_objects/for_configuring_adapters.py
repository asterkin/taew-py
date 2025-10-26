from dataclasses import dataclass
from typing import Any

from taew.domain.configuration import PortsMapping
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from taew.ports import for_marshalling_objects as for_marshalling_objects_port
from .dumps import DumpsBase
from .loads import LoadsBase


@dataclass(eq=False, frozen=True, kw_only=True)
class Configure(DumpsBase, LoadsBase, ConfigureBase):
    """Configurator for JSON stringizing adapter with marshalling support.

    Bridges for_stringizing_objects to for_marshalling_objects by using
    the base class _configure_item to resolve the appropriate marshalling adapter.

    Inherits all json.dumps and json.loads configuration parameters from
    DumpsBase and LoadsBase.

    Args:
        _type: The type to configure marshalling for
    """

    _type: Any = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

    def _nested_ports(self) -> PortsMapping:
        """Return nested ports from the for_marshalling_objects configurator.

        Uses base class _configure_item to resolve the marshalling adapter
        for the specified type. Only returns marshalling configuration if _type is set.
        """
        if self._type is None:
            return {}
        _, config = self._configure_item(self._type, for_marshalling_objects_port)
        return {for_marshalling_objects_port: config}
