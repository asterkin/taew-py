from base64 import b64encode
from base64 import urlsafe_b64encode
from dataclasses import dataclass

from ._common import Base64Config


@dataclass(eq=False, frozen=True)
class Dumps(Base64Config):
    """Convert bytes to Base64 string.

    Uses standard Base64 or URL-safe variant. Returns text encoded with
    configurable ``_text_encoding`` (default ASCII).
    """

    def _encode(self, data: bytes) -> bytes:
        if self._urlsafe:
            return urlsafe_b64encode(data)
        if self._altchars is not None:
            return b64encode(data, altchars=self._altchars)
        return b64encode(data)

    def __call__(self, value: object) -> str:
        if not isinstance(value, bytes):  # type: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Unsupported type for base64 dumps: {type(value)}")

        encoded = self._encode(value)
        return encoded.decode(self._text_encoding, self._errors)
