from typing import NewType

"""
Clean logging level constants without enum verbosity.

Advantages:

- Clean imports: from taew.domain.logging import DEBUG, INFO
- Direct usage: if level == DEBUG: instead of LogLevel.DEBUG
- Order preserved: level >= WARNING to check severity
- Type safety: NewType provides compile-time checking
- Standard compatibility: Same integer values as Python logging module
- No protocol overhead: Direct integer comparisons

Pattern matching becomes elegant:
match level:
    case DEBUG:
        # debug handling
    case INFO:
        # info handling
    case WARNING | ERROR | CRITICAL:
        # error handling

Enums are overkill for simple integer constants, and this approach gives better ergonomics without sacrificing type safety.
"""

LogLevel = NewType("LogLevel", int)

DEBUG = LogLevel(10)
INFO = LogLevel(20)
WARNING = LogLevel(30)
ERROR = LogLevel(40)
CRITICAL = LogLevel(50)

__all__ = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "LogLevel",
]
