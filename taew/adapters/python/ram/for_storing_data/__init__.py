from typing import TypeVar, Callable, Optional, Any, Iterable

K = TypeVar("K")
V = TypeVar("V")


class DataRepository(dict[K, V]):
    """RAM-based read-only data repository with query capabilities.

    Extends dict to provide standard dictionary operations while implementing
    the DataRepository protocol with query functionality for filtering and sorting.
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
        filtered_values = [value for value in self.values() if filter_fn(value)]

        if sort_key is not None:
            filtered_values.sort(key=sort_key, reverse=reverse)

        return filtered_values


class MutableDataRepository(DataRepository[K, V]):
    """RAM-based mutable data repository extending read-only capabilities.

    Inherits all functionality from DataRepository and dict, providing
    both query capabilities and full mutable dictionary operations.
    """

    pass
