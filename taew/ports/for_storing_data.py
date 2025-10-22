from typing import TypeVar, Callable, Optional, Any, Self
from collections.abc import Iterable, Mapping, MutableMapping, MutableSequence, Sequence

K = TypeVar("K")
V = TypeVar("V")


class DataRepository(Mapping[K, V]):
    """Generic read-only data repository with query capabilities.

    Extends collections.abc.Mapping to provide standard dictionary-like
    read operations (__getitem__, __iter__, __len__, etc.) while adding
    a powerful query method for filtering and sorting stored data.

    Type Parameters:
        K: Key type for accessing stored data
        V: Value type of stored data items
    """

    def query(
        self,
        *,
        filter_fn: Callable[[V], bool],
        sort_key: Optional[Callable[[V], Any]] = None,
        reverse: bool = False,
    ) -> Iterable[V]:
        """Query stored data with filtering and optional sorting.

        Args:
            filter_fn: Function that takes a value and returns True if it
                      should be included in results
            sort_key: Optional function that takes a value and returns a
                     comparison key for sorting
            reverse: Whether to reverse the sort order (default: False)

        Returns:
            Iterable of values that match the filter criteria, optionally sorted
        """
        # default implementation using existing Mapping methods
        # need to convert to list for sorting
        # db backends can override for efficiency
        filtered_values = [value for value in self.values() if filter_fn(value)]

        if sort_key is not None:
            filtered_values.sort(key=sort_key, reverse=reverse)

        return filtered_values


class MutableDataRepository(DataRepository[K, V], MutableMapping[K, V]):
    """Generic mutable data repository extending read-only capabilities.

    Combines DataRepository's query capabilities with MutableMapping's
    write operations (__setitem__, __delitem__, etc.) to provide a
    complete data storage interface.

    Inherits query() method from DataRepository to avoid duplication.

    Type Parameters:
        K: Key type for accessing stored data
        V: Value type of stored data items
    """

    def __enter__(self) -> Self:
        """Enter context manager - default no-op implementation.

        Returns:
            Self: The repository instance for use in the with statement
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Exit context manager - default no-op implementation.

        Args:
            exc_type: Exception type if an exception occurred, None otherwise
            exc_val: Exception value if an exception occurred, None otherwise
            exc_tb: Exception traceback if an exception occurred, None otherwise
        """
        pass


class DataSequence(Sequence[V]):
    """Generic read-only sequence repository with query capabilities.

    Extends collections.abc.Sequence to provide standard list-like read
    operations (__getitem__, __len__, __iter__, etc.) while adding a
    query method for filtering and optional sorting of stored items.

    Type Parameters:
        V: Value type of stored sequence items
    """

    def query(
        self,
        *,
        filter_fn: Callable[[V], bool],
        sort_key: Optional[Callable[[V], Any]] = None,
        reverse: bool = False,
    ) -> Iterable[V]:
        """Query stored items with filtering and optional sorting.

        Notes:
            - The default implementation materializes results from iteration
              into a list to support in-memory sorting when ``sort_key`` is
              provided. Adapters that support native filtering/sorting (e.g.,
              database-backed) may override this to stream results and/or
              push sorting to the backend.

        Args:
            filter_fn: Function that takes a value and returns True if it
                       should be included in results
            sort_key: Optional function that takes a value and returns a
                      comparison key for sorting
            reverse: Whether to reverse the sort order (default: False)

        Returns:
            Iterable of values that match the filter criteria, optionally sorted
        """
        # default implementation using existing Sequence methods
        filtered_values = [value for value in self if filter_fn(value)]

        if sort_key is not None:
            filtered_values.sort(key=sort_key, reverse=reverse)

        return filtered_values


class MutableDataSequence(DataSequence[V], MutableSequence[V]):
    """Generic mutable sequence repository extending read-only capabilities.

    Combines DataSequence's query capabilities with MutableSequence's
    write operations (insert, __setitem__, __delitem__, etc.) to provide a
    complete sequence storage interface.

    Inherits query() method from DataSequence to avoid duplication.

    Type Parameters:
        V: Value type of stored sequence items
    """

    def __enter__(self) -> Self:
        """Enter context manager - default no-op implementation.

        Returns:
            Self: The sequence instance for use in the with statement
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Exit context manager - default no-op implementation.

        Args:
            exc_type: Exception type if an exception occurred, None otherwise
            exc_val: Exception value if an exception occurred, None otherwise
            exc_tb: Exception traceback if an exception occurred, None otherwise
        """
        pass
