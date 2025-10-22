from typing import Final, Literal
from dataclasses import dataclass


_BYTE_ORDERS: Final[tuple[Literal["big", "little"], ...]] = ("big", "little")


@dataclass(eq=False, frozen=True)
class SerdeBase:
    """Common configuration for integer (de)serialization.

    Provides shared parameters and validation used by Serialize and
    Deserialize adapters.
    """

    _byte_order: Literal["big", "little"] = "big"
    _signed: bool = True

    def __post_init__(self) -> None:
        if self._byte_order not in _BYTE_ORDERS:
            raise ValueError("_byte_order must be 'big' or 'little'")
