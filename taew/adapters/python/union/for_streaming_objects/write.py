from io import BytesIO
from collections.abc import Mapping
from dataclasses import dataclass, field

from taew.ports.for_streaming_objects import Write as WriteProtocol


@dataclass(eq=False, frozen=True)
class Write:
    """Union writer that records the concrete type before delegating the payload."""

    _writers: Mapping[str | type[object], WriteProtocol]
    _write_choice: WriteProtocol = field(init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            choice_writer = self._writers["choices"]
        except KeyError as exc:
            raise ValueError("Union writer requires a 'choices' entry") from exc
        object.__setattr__(self, "_write_choice", choice_writer)

    def __call__(self, obj: object, stream: BytesIO) -> None:
        obj_type = type(obj)
        try:
            write = self._writers[obj_type]
        except KeyError as exc:
            raise ValueError(
                f"Union writer missing handler for type {obj_type!r}"
            ) from exc
        self._write_choice(obj_type, stream)
        write(obj, stream)
