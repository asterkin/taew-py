# taew/ports/for_starting_programs.py
from typing import Protocol
from collections.abc import Sequence


class Main(Protocol):
    """Generic program entry point."""

    def __call__(self, cmd_args: Sequence[str]) -> None: ...
