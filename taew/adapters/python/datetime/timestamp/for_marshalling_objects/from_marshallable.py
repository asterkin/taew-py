from datetime import datetime

from taew.domain.marshalling import Marshallable


class FromMarshallable:
    """Parse marshallable float timestamps back to datetime objects.

    Converts Unix timestamp (seconds since epoch) to naive datetime.
    Returns naive datetime in local time.

    Note: Timezone information is NOT preserved. If the original datetime
    was timezone-aware, the timezone is lost during round-trip conversion.
    """

    def __call__(self, data: Marshallable) -> object:
        if not isinstance(data, (int, float)):
            raise TypeError(
                f"Expected int or float for datetime timestamp unmarshalling, got {type(data)}"
            )
        try:
            return datetime.fromtimestamp(float(data))
        except (ValueError, OSError, OverflowError) as e:
            raise ValueError(f"Unable to parse datetime from timestamp: {data}") from e
