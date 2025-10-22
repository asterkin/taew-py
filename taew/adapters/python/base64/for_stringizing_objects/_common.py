from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class Base64Config:
    """Shared configuration for Base64 stringizing adapters."""

    _urlsafe: bool = False
    _altchars: bytes | None = None
    _text_encoding: str = "ascii"
    _errors: str = "strict"
