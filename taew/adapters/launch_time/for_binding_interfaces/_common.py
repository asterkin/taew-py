from dataclasses import dataclass

from taew.ports.for_browsing_code_tree import Root


@dataclass(eq=False, frozen=True)
class BindBase:
    _root: Root
