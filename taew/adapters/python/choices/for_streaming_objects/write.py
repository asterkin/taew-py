from io import BytesIO
from dataclasses import dataclass
from typing import cast

from ._common import ChoicesBase
from taew.ports.for_streaming_objects import Write as IntWrite


@dataclass(eq=False, frozen=True)
class Write(ChoicesBase):
    _write_int: IntWrite = cast(IntWrite, None)

    def __call__(self, obj: object, stream: BytesIO) -> None:
        try:
            idx = self._choices.index(obj)
        except ValueError as e:
            raise ValueError(f"Value {obj!r} not in choices") from e
        # Delegate to int write using our framing config
        self._write_int(idx, stream)
