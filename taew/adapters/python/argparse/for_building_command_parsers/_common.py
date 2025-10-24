from dataclasses import dataclass

from taew.ports.for_binding_interfaces import Bind as BindProtocol
from taew.ports.for_finding_configurations import Find as FindProtocol


@dataclass(eq=False, frozen=True)
class BuildBase:
    """Base configuration for command parser builders.

    Encapsulates the dependencies required by Builder:
    - _find: Locates configuration for custom types
    - _bind: Binds protocols to implementations

    This is frozen and immutable. Builder uses composition with this class.
    Build and Configure inherit from this directly.

    Properties provide access to the protected fields for use by Builder.
    """

    _find: FindProtocol
    _bind: BindProtocol

    @property
    def find(self) -> FindProtocol:
        """Expose _find for use by Builder."""
        return self._find

    @property
    def bind(self) -> BindProtocol:
        """Expose _bind for use by Builder."""
        return self._bind
