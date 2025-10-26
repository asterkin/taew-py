from dataclasses import dataclass


@dataclass(eq=False, frozen=True)
class BuildBase:
    _adapters: str = "taew.adapters.python"
    _root: str = ""
