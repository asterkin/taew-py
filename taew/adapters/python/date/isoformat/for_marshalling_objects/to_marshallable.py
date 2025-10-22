from datetime import date

from taew.domain.marshalling import Marshallable

from ._common import DateIsoformatBase


class ToMarshallable(DateIsoformatBase):
    """Convert date objects to marshallable string using ISO or custom format.

    Default behavior (when _format is None):
    - Uses date.isoformat() to produce "YYYY-MM-DD" format

    With custom format:
    - Uses date.strftime(_format) for custom formatting
    """

    def __call__(self, value: object) -> Marshallable:
        match value:
            case date():
                return (
                    value.isoformat()
                    if self._format is None
                    else value.strftime(self._format)
                )
            case _:
                raise TypeError(
                    f"Unsupported type for date isoformat marshalling: {type(value)}"
                )
