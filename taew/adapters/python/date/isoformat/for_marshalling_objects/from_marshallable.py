from datetime import date, datetime

from taew.domain.marshalling import Marshallable

from ._common import DateIsoformatBase


class FromMarshallable(DateIsoformatBase):
    """Parse marshallable strings into date objects using ISO or custom format.

    Default behavior (when _format is None):
    - Uses date.fromisoformat() to parse "YYYY-MM-DD" format

    With custom format:
    - Uses datetime.strptime(_format) and extracts date portion
    """

    def __call__(self, data: Marshallable) -> object:
        if not isinstance(data, str):
            raise TypeError(
                f"Expected string for date isoformat unmarshalling, got {type(data)}"
            )

        if self._format is None:
            # Use ISO format
            try:
                return date.fromisoformat(data)
            except ValueError as e:
                raise ValueError(f"Unable to parse date from ISO format: {data}") from e
        else:
            # Use custom format (strptime returns datetime, extract date)
            try:
                return datetime.strptime(data, self._format).date()
            except ValueError as e:
                raise ValueError(
                    f"Unable to parse date with format '{self._format}': {data}"
                ) from e
