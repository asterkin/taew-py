from base64 import b64decode
from base64 import urlsafe_b64decode
from binascii import Error as BinasciiError
from dataclasses import dataclass

from ._common import Base64Config


@dataclass(eq=False, frozen=True)
class Loads(Base64Config):
    """Convert Base64 string to bytes.

    Uses standard Base64 or URL-safe variant. Accepts text encoded with
    configurable ``_text_encoding`` (default ASCII). When ``_urlsafe`` is
    False, decoding honors ``_altchars`` and ``_validate``.
    """

    _validate: bool = True

    def _decode(self, data: bytes) -> bytes:
        if self._urlsafe:
            return urlsafe_b64decode(data)
        return b64decode(data, altchars=self._altchars, validate=self._validate)

    def __call__(self, buf: str) -> object:
        if not isinstance(buf, str):  # type: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Unsupported type for base64 loads: {type(buf)}")

        try:
            raw = buf.encode(self._text_encoding, self._errors)
            return self._decode(raw)
        except (UnicodeEncodeError, BinasciiError, ValueError) as e:
            raise ValueError(f"Unable to decode base64 string: {e}") from e
