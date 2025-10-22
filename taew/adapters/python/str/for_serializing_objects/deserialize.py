from dataclasses import dataclass
from taew.ports.for_stringizing_objects import Loads
from ._common import SerdeBase


def _identity_loads(buf: str) -> object:
    return buf


@dataclass(eq=False, frozen=True)
class Deserialize(SerdeBase):
    """Deserialize bytes to objects via string decoding.

    First decodes bytes to string, then converts string to object using _loads.
    """

    _loads: Loads = _identity_loads

    def __call__(self, buf: bytes) -> object:
        if not isinstance(buf, bytes):  # type: ignore[reportUnnecessaryIsInstance]
            raise ValueError(f"Expected bytes, got {type(buf).__name__}")

        # First decode bytes to string
        str_value = buf.decode(encoding=self._encoding, errors=self._errors)

        # Then convert string to object using loads
        return self._loads(str_value)
