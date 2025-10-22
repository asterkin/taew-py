import pickle
from dataclasses import dataclass

from ._common import PickleSerde


@dataclass(eq=False, frozen=True)
class Serialize(PickleSerde):
    def __call__(self, value: object) -> bytes:
        return pickle.dumps(
            value, protocol=self._protocol, fix_imports=self._fix_imports
        )
