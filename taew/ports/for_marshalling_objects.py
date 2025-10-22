"""Port for marshalling objects to/from marshallable primitives.

This port defines the intermediate stage of the marshalling process:
converting domain objects to and from marshallable data structures
(compositions of scalars, lists, and dictionaries).

The complete marshalling pipeline typically involves:
1. ToMarshallable: Domain object → Marshallable primitives (this port)
2. Format encoding: Marshallable primitives → str|bytes (format-specific adapters)

And the reverse for unmarshalling:
1. Format decoding: str|bytes → Marshallable primitives (format-specific adapters)
2. FromMarshallable: Marshallable primitives → Domain object (this port)
"""

from typing import Protocol

from taew.domain.marshalling import Marshallable


class ToMarshallable(Protocol):
    """Protocol for converting domain objects to marshallable primitives.

    Implementations take a domain object (e.g., NamedTuple, dataclass, custom class)
    and convert it to a marshallable data structure composed of scalars, lists,
    and dictionaries that can be subsequently encoded to various formats (JSON,
    YAML, XML, etc.).
    """

    def __call__(self, value: object) -> Marshallable: ...


class FromMarshallable(Protocol):
    """Protocol for reconstructing domain objects from marshallable primitives.

    Implementations take a marshallable data structure (composed of scalars,
    lists, and dictionaries) and reconstruct the original domain object.

    This is the inverse operation of ToMarshallable and is used after decoding
    from format-specific representations (JSON, YAML, XML, etc.).
    """

    def __call__(self, data: Marshallable) -> object: ...
