from types import MappingProxyType
from functools import cached_property
from typing import TypeVar, Generic, Optional
from collections.abc import Iterable, Iterator

V = TypeVar("V")


class NameMapping(Generic[V]):
    def __init__(self, items: dict[str, V]) -> None:
        self._mapping = MappingProxyType(dict(items))  # immutable view

    def __getitem__(self, name: str) -> V:
        return self._mapping[name]

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)

    def items(self) -> Iterable[tuple[str, V]]:
        return self._mapping.items()

    def __repr__(self) -> str:
        return repr(self._mapping)

    def get(self, name: str, default: Optional[V] = None) -> Optional[V]:
        return self._mapping.get(name, default)

    def __contains__(self, name: str) -> bool:
        return name in self._mapping


class DescribedMapping(NameMapping[V]):
    def __init__(self, description: str, items: dict[str, V]) -> None:
        super().__init__(items)
        self._description = description

    @cached_property
    def description(self) -> str:
        return self._description

    def __repr__(self) -> str:
        return f"description: {self._description}\n{super().__repr__()}"
