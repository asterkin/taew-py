"""Configuration adapter for inspect-based code tree browsing."""

from dataclasses import dataclass
from pathlib import Path

from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)


@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    """Configure the inspect-based Root for code tree browsing.

    Args:
        _root_path: Path to the root directory for code tree navigation.
                   Defaults to current directory ('./').
    """

    _root_path: Path = Path("./")

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
