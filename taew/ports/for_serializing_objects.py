from io import BytesIO
from typing import Protocol


class Serialize(Protocol):  # object -> bytes
    def __call__(self, value: object) -> bytes: ...


class Deserialize(Protocol):  # bytes -> object
    def __call__(self, buf: bytes) -> object: ...


class DeserializeStream(Protocol):  # BytesIO -> object
    def __call__(self, stream: BytesIO) -> object: ...


class Dumps(Protocol):  # object -> str
    def __call__(self, value: object) -> str: ...


class Loads(Protocol):  # str -> object
    def __call__(self, buf: str) -> object: ...
