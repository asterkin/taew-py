from decimal import Decimal, InvalidOperation

from ._common import DecimalBase


class Loads(DecimalBase):
    """Parse string representations back to Decimal objects."""

    def __call__(self, buf: str) -> object:
        try:
            return Decimal(buf)
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Unable to parse decimal from string: {buf}") from e
