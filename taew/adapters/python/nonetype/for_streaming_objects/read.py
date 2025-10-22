from io import BytesIO
from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class Read:
    def __call__(self, stream: BytesIO) -> object:
        # Return None without consuming bytes
        return None
