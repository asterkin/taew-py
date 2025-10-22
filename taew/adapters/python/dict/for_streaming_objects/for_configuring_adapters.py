from types import TracebackType, GenericAlias
from typing import Any, Self, cast
from collections.abc import Collection

from taew.adapters.python.sequence.for_streaming_objects.for_configuring_adapters import (
    Configure as SequenceConfigure,
)
from taew.ports.for_streaming_objects import SequenceContext


def _dict_items(obj: object) -> Collection[object]:
    return cast(Collection[object], cast(dict[Any, Any], obj).items())


class _DictContext:
    def __init__(self, _: int) -> None:
        self._items: list[tuple[object, object]] = []
        self._keys: set[object] = set()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    def append(self, item: object) -> None:
        if not isinstance(item, tuple):
            raise TypeError(
                f"Dict stream expects tuple[key, value], got {type(item).__name__}"
            )
        item = cast(tuple[object, object], item)
        if len(item) != 2:
            raise ValueError(
                f"Dict stream expects tuple[key, value], got {len(item)} items"
            )  # type: ignore
        key, value = item
        if key in self._keys:
            raise ValueError(f"Duplicate key in dict stream: {key!r}")
        self._keys.add(key)
        self._items.append((key, value))

    def value(self) -> object:
        return dict(self._items)


def _dict_target(count: int) -> SequenceContext:
    return _DictContext(count)


class Configure(SequenceConfigure):
    def __init__(self, _args: tuple[Any, ...]) -> None:
        if len(_args) != 2:
            raise ValueError("Dict streamer expects exactly two types: key and value")
        # Pass tuple with args as a tuple - sequence will detect it's parametrized
        super().__init__(
            _args=(GenericAlias(tuple, _args),),
            _from=_dict_items,
            _target=_dict_target,
        )
