from dataclasses import dataclass

from taew.adapters.python.bytes.for_streaming_objects.for_configuring_adapters import (
    Configure as BytesConfigure,
)


@dataclass(eq=False, frozen=True)
class Configure(BytesConfigure):
    """Configure str streaming by composing bytes streamer + str serializer.

    Inherits bytes streamer configurator (which defaults to 2-byte length) and
    supplies a default str serializer when none is provided.
    """

    def __post_init__(self) -> None:
        # Initialize base bytes configurator (sets adapter path and default length)
        super().__post_init__()
        # If no serializer is provided, default to str serializer
        if self._serde is None:
            from taew.adapters.python.str.for_serializing_objects.for_configuring_adapters import (  # noqa: E501
                Configure as StrSerde,
            )

            object.__setattr__(self, "_serde", StrSerde())
