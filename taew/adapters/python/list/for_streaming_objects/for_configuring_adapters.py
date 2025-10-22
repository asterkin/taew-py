from builtins import BaseException
from collections.abc import Collection
from typing import Any, Callable, Self, cast

from taew.ports.for_streaming_objects import SequenceContext
from taew.adapters.python.sequence.for_streaming_objects.for_configuring_adapters import (
    Configure as SequenceConfigure,
)


def _identity(obj: object) -> Collection[object]:
    return cast(Collection[object], obj)


class ListTargetContext(SequenceContext):
    def __init__(self, _: int) -> None:
        self._items: list[object] = []

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
        self._items.append(item)

    def value(self) -> object:
        return list(self._items)


def _list_target(count: int) -> SequenceContext:
    return ListTargetContext(count)


class Configure(SequenceConfigure):
    def __init__(
        self,
        _args: tuple[Any, ...],
        _target: Callable[[int], SequenceContext] | None = None,
    ) -> None:
        if len(_args) != 1:
            raise ValueError("List streamer expects exactly one item type")
        super().__init__(
            _args=_args,
            _from=_identity,
            _target=_list_target if _target is None else _target,
        )
