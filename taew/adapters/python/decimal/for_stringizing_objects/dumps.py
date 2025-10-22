from decimal import Decimal

from ._common import DecimalBase


class Dumps(DecimalBase):
    """Convert Decimal objects to string representations with full precision."""

    def __call__(self, value: object) -> str:
        match value:
            case Decimal():
                return str(value)
            case _:
                raise TypeError(
                    f"Unsupported type for decimal serialization: {type(value)}"
                )
