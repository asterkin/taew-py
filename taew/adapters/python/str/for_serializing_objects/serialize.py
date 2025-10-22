from dataclasses import dataclass
from taew.ports.for_stringizing_objects import Dumps
from ._common import SerdeBase


def _identity_dumps(value: object) -> str:
    if isinstance(value, str):
        return value
    raise ValueError(f"Expected str, got {type(value).__name__}")


@dataclass(eq=False, frozen=True)
class Serialize(SerdeBase):
    """Serialize objects to bytes via string encoding.

    First converts object to string using _dumps, then encodes to bytes.
    """

    _dumps: Dumps = _identity_dumps

    def __call__(self, value: object) -> bytes:
        # First convert object to string using dumps
        str_value = self._dumps(value)

        # Then encode string to bytes
        return str_value.encode(encoding=self._encoding, errors=self._errors)
