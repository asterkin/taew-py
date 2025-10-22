# taew/ports/for_obtaining_current_datetime.py
from typing import Protocol
from datetime import datetime


class Now(Protocol):
    """Protocol for obtaining current datetime."""

    def __call__(self) -> datetime: ...
