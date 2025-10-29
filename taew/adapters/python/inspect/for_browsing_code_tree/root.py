from pathlib import Path
from ._common import RootBase


class Root(RootBase):
    def change_root(self, new_root: str) -> Root:
        return Root(Path(new_root))
