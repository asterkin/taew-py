from typing import Any

from taew.adapters.python.list.for_streaming_objects.for_configuring_adapters import (
    Configure as ListConfigure,
)
from taew.adapters.python.list.for_streaming_objects.for_configuring_adapters import (
    ListTargetContext,
)
from taew.ports.for_streaming_objects import SequenceContext


class _TupleTarget(ListTargetContext):
    def value(self) -> object:
        return tuple(self._items)


def _tuple_target(count: int) -> SequenceContext:
    return _TupleTarget(count)


class Configure(ListConfigure):
    def __init__(self, _args: tuple[Any, ...]) -> None:
        super().__init__(_args=_args, _target=_tuple_target)
