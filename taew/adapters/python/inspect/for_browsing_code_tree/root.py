from __future__ import annotations
from pathlib import Path
from ._folder import Folder


class Root(Folder):
    def change_root(self, new_root: str) -> Root:
        return Root(Path(new_root))
