from datetime import datetime

from taew.domain.marshalling import Marshallable


class ToMarshallable:
    """Convert datetime objects to marshallable float timestamps.

    Converts datetime to Unix timestamp (seconds since epoch as float).
    Preserves microsecond precision.

    Timezone handling:
    - Timezone-aware datetimes are converted to UTC before generating timestamp
    - Naive datetimes are assumed to be in local time (platform-dependent)
    - Timezone information is NOT preserved in the marshalled form
    """

    def __call__(self, value: object) -> Marshallable:
        match value:
            case datetime():
                return value.timestamp()
            case _:
                raise TypeError(
                    f"Unsupported type for datetime timestamp marshalling: {type(value)}"
                )
