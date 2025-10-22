from io import BytesIO
from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class Write:
    def __call__(self, obj: object, stream: BytesIO) -> None:
        # Stream None as zero bytes; validate input is None for clarity
        if obj is not None:  # type: ignore[reportUnnecessaryComparison]
            raise TypeError(f"Unsupported type for None write: {type(obj)}")
        # Do nothing
        return None
