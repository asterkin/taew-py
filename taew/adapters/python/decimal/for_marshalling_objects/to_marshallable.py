from decimal import Decimal

from taew.domain.marshalling import Marshallable
from ._common import DecimalBase


class ToMarshallable(DecimalBase):
    """Convert Decimal objects to marshallable string representations with full precision."""

    def __call__(self, value: object) -> Marshallable:
        match value:
            case Decimal():
                return str(value)
            case _:
                raise TypeError(
                    f"Unsupported type for decimal marshalling: {type(value)}"
                )
