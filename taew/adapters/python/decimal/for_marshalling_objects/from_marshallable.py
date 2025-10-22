from decimal import Decimal, InvalidOperation

from taew.domain.marshalling import Marshallable
from ._common import DecimalBase


class FromMarshallable(DecimalBase):
    """Parse marshallable string representations back to Decimal objects."""

    def __call__(self, data: Marshallable) -> object:
        if not isinstance(data, str):
            raise TypeError(
                f"Expected string for decimal unmarshalling, got {type(data)}"
            )
        try:
            return Decimal(data)
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Unable to parse decimal from string: {data}") from e
