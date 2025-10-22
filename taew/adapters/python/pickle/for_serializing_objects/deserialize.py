import pickle
from dataclasses import dataclass

from ._common import PickleSerde


@dataclass(eq=False, frozen=True)
class Deserialize(PickleSerde):
    def __call__(self, buf: bytes) -> object:
        return pickle.loads(
            buf,
            fix_imports=self._fix_imports,
            encoding=self._encoding,
            errors=self._errors,
        )
