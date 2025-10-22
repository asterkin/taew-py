from typing import Any
from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class Logger:
    """RAM-based logger that stores all log calls for testing verification.

    Provides a fast, cheap replacement for mocks by storing all logging
    arguments in a list. Enables easy verification of log messages, levels,
    and context data in unit tests.
    """

    _calls: list[tuple[Any, ...]]

    def debug(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity DEBUG."""
        self._calls.append(("debug", msg, args, kwargs))

    def info(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity INFO."""
        self._calls.append(("info", msg, args, kwargs))

    def warning(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity WARNING."""
        self._calls.append(("warning", msg, args, kwargs))

    def error(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity ERROR."""
        self._calls.append(("error", msg, args, kwargs))

    def critical(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity CRITICAL."""
        self._calls.append(("critical", msg, args, kwargs))

    def log(self, level: int, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with the integer severity level."""
        self._calls.append(("log", (level, msg), args, kwargs))
