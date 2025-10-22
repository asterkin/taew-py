from dataclasses import dataclass
from typing import Optional

from ._common import DateIsoformatBase
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(DateIsoformatBase, ConfigureBase):
    """Dataclass-based configurator for date isoformat marshalling adapters.

    Inherits _format from DateIsoformatBase to allow custom date formats.
    Default (None) uses ISO format (YYYY-MM-DD).

    Args:
        _format: Optional strftime/strptime format string. None means ISO format.

    Example:
        Configure()  # Uses ISO format (YYYY-MM-DD)
        Configure(_format="%Y/%m/%d")  # Uses custom format (YYYY/MM/DD)
    """

    _format: Optional[str] = None

    def __post_init__(self) -> None:
        # Point to this package for adapter resolution and root detection
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
