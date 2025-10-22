from typing import Protocol, Any


class Logger(Protocol):
    """Protocol for logging operations with direct stdlib Logger compatibility.

    Provides zero-cost abstraction over Python's standard logging.Logger by
    exactly matching its method signatures. This allows direct usage of stdlib
    Logger instances without wrapper overhead.

    All methods support:
    - String formatting via *args: logger.info("Hello %s", name)
    - Metadata via **kwargs: logger.info("Event", extra={"user_id": 123})
    - Exception info: logger.error("Failed", exc_info=True)
    """

    def debug(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity DEBUG."""
        ...

    def info(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity INFO."""
        ...

    def warning(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity WARNING."""
        ...

    def error(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity ERROR."""
        ...

    def critical(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with severity CRITICAL."""
        ...

    def log(self, level: int, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg % args with the integer severity level."""
        ...
