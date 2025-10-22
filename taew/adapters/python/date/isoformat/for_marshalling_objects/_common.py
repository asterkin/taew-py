from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, eq=False)
class DateIsoformatBase:
    """Base class for date isoformat marshalling adapters with configurable format.

    Supports both ISO format (default) and custom strftime/strptime formats.
    """

    _format: Optional[str] = None  # None means use isoformat()/fromisoformat()
