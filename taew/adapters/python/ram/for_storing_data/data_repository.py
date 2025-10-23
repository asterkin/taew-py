"""RAM-based DataRepository implementation.

Provides read-only key-value storage backed by in-memory dictionary.
"""

from typing import TypeVar
from collections import UserDict

from taew.ports.for_storing_data import DataRepository as DataRepositoryProtocol

K = TypeVar("K")
V = TypeVar("V")


class DataRepository(UserDict[K, V], DataRepositoryProtocol[K, V]):
    """RAM-based read-only data repository with query capabilities.

    Extends dict to provide standard dictionary operations while implementing
    the DataRepository ABC. The query method is inherited from the ABC.
    """

    pass
