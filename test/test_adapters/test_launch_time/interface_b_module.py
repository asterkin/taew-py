from typing import Protocol


class InterfaceB(Protocol):
    def __call__(self, x: str) -> str: ...
