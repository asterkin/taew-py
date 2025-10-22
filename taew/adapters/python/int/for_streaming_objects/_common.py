from typing import Final, Literal
from dataclasses import dataclass


_BYTE_ORDERS: Final[tuple[Literal["big", "little"], ...]] = ("big", "little")


@dataclass(eq=False, frozen=True)
class IntStreamBase:
    """Base config for fixed-width integer streaming.

    Holds common framing parameters and validates them. Concrete adapters
    implement Write/Read behaviors.
    """

    _width: int = 4
    _byte_order: Literal["big", "little"] = "big"
    _signed: bool = False

    def __post_init__(self) -> None:
        if self._width <= 0:
            raise ValueError("_width must be a positive integer")
        if self._byte_order not in _BYTE_ORDERS:
            raise ValueError("_byte_order must be 'big' or 'little'")
