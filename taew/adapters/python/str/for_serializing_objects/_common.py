from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class SerdeBase:
    """Shared config for string (de)serialization.

    Holds text encoding parameters used by Serialize and Deserialize. Kept
    minimal and focused; adapters validate input types themselves.
    """

    _encoding: str = "utf-8"
    _errors: str = "strict"

    def __post_init__(self) -> None:
        if not self._encoding:
            raise ValueError("_encoding must be a non-empty codec name")
