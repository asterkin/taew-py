from io import BytesIO
from collections.abc import Mapping
from dataclasses import dataclass, field

from taew.ports.for_streaming_objects import Read as ReadProtocol


@dataclass(eq=False, frozen=True)
class Read:
    """Union reader that selects the payload reader based on the next choice."""

    _readers: Mapping[str | type[object], ReadProtocol]
    _read_choice: ReadProtocol = field(init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            choice_reader = self._readers["choices"]
        except KeyError as exc:
            raise ValueError("Union reader requires a 'choices' entry") from exc
        object.__setattr__(self, "_read_choice", choice_reader)

    def __call__(self, stream: BytesIO) -> object:
        choice = self._read_choice(stream)
        if not isinstance(choice, (str, type)):
            raise TypeError(f"Invalid union choice marker: {choice!r}")
        try:
            read = self._readers[choice]
        except KeyError as exc:
            raise ValueError(
                f"Union reader missing handler for choice {choice!r}"
            ) from exc
        return read(stream)
