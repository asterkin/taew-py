from dataclasses import dataclass

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Dataclass-based configurator for datetime timestamp marshalling adapters.

    This configurator sets up adapters for converting datetime objects to/from
    Unix timestamps (float values). No configuration parameters or nested ports required.

    Timezone handling:
    - Timezone-aware datetimes are converted to UTC timestamp
    - Timezone information is NOT preserved during marshalling
    - Unmarshalling always returns naive datetime in local time
    """

    def __post_init__(self) -> None:
        # Point to this package for adapter resolution and root detection
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
