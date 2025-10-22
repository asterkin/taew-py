from typing import ClassVar
from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class PickleSerde:
    _protocol: int = 5
    _fix_imports: bool = True
    _encoding: str = "ASCII"
    _errors: str = "strict"
    _media_type: ClassVar[str] = "application/octet-stream"
    _roundtrippable: ClassVar[bool] = True
