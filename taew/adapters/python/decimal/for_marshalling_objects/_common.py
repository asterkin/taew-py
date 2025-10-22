from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class DecimalBase:
    """Base class for decimal marshalling adapters with configurable precision."""

    _context: Optional[str] = None  # None means use default decimal context
