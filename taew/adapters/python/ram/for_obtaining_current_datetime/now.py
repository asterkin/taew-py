# taew/adapters/ram/for_obtaining_current_datetime.py
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Now:
    _now: datetime = field(default_factory=datetime.now)

    def __call__(self) -> datetime:
        return self._now
