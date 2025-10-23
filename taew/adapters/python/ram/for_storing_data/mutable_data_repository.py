"""RAM-based MutableDataRepository implementation.

Provides read-write key-value storage backed by in-memory dictionary.
"""

from typing import TypeVar
from collections import UserDict

from taew.ports.for_storing_data import (
    MutableDataRepository as MutableDataRepositoryProtocol,
)

K = TypeVar("K")
V = TypeVar("V")


class MutableDataRepository(UserDict[K, V], MutableDataRepositoryProtocol[K, V]):
    """RAM-based mutable data repository extending read-only capabilities.

    Inherits all functionality from dict, providing
    full mutable dictionary operations.
    The query, __enter__ and __exit__ methods are inherited from the ABC.
    """

    pass
