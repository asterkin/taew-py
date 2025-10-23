from dataclasses import dataclass

from taew.domain.logging import LogLevel, INFO
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configurator for Python logging adapter.

    Simplifies configuration of the logging adapter by accepting a logger name
    and log level, then providing sensible defaults for the config dictionary.

    Args:
        _name: Logger name (typically module name or component identifier)
        _level: Logging level (defaults to INFO). Use taew.domain.logging constants.

    The config dict is automatically constructed with default format and style.

    Example:
        from taew.domain.logging import INFO, DEBUG
        from taew.adapters.python.logging.for_configuring_adapters import Configure

        # Minimal usage - only name required, level defaults to INFO
        ports = Configure(_name="MyApp")()

        # With explicit level
        ports = Configure(_name="MyApp.Component", _level=DEBUG)()
    """

    _level: LogLevel = INFO
    _name: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

    def _collect_kwargs(self) -> dict[str, object]:
        """Collect kwargs for adapter instantiation.

        Renames _name to name for the Logger adapter.
        """
        return dict(
            name=self._name,
            config=dict(
                level=self._level,
                format="{levelname}:{message}",
                style="{",
            ),
        )
