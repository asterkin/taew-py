"""Launch-time adapters for interface binding and instantiation."""

from .bind import bind
from .create_instance import create_instance

__all__ = ["bind", "create_instance"]
