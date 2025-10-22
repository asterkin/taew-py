from collections.abc import Collection
from typing import Any, Self, cast

from taew.adapters.python.sequence.for_streaming_objects.for_configuring_adapters import (
    Configure as SequenceConfigure,
)
from taew.ports.for_streaming_objects import SequenceContext


def _identity(obj: object) -> Collection[object]:
    return cast(Collection[object], obj)


class _SetContext(SequenceContext):
    def __init__(self, _: int) -> None:
        self._items: set[object] = set()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _tb: object | None,
    ) -> None:
        return None

    def append(self, item: object) -> None:
        if item in self._items:
            raise ValueError(f"Duplicate item in set stream: {item!r}")
        self._items.add(item)

    def value(self) -> object:
        return set(self._items)


def _set_target(count: int) -> SequenceContext:
    return _SetContext(count)


class Configure(SequenceConfigure):
    def __init__(self, _args: tuple[Any, ...]) -> None:
        if len(_args) != 1:
            raise ValueError("Set streamer expects exactly one item type")
        super().__init__(
            _args=_args,
            _from=_identity,
            _target=_set_target,
        )
