import logging
from typing import Any


class Logger(logging.Logger):
    _configured: bool = False

    def __new__(cls, name: str, config: dict[str, Any]) -> logging.Logger:  # type: ignore
        try:
            if not cls._configured:
                logging.basicConfig(**config)
                cls._configured = True

            # Return the actual stdlib Logger instance
            return logging.getLogger(name)
        except Exception as e:
            # Handle or log the exception as needed
            print(f"Error configuring logger: {e}")
            raise

    # TODO: It's a workaround to pass global config arguments
    # need to find a better way
    def __init__(self, name: str, config: dict[str, Any]) -> None:  # type: ignore
        super().__init__(name)
