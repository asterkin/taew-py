import pprint as _pp
from typing import ClassVar
from dataclasses import dataclass, field


@dataclass(eq=False, frozen=True, slots=True, kw_only=True)
class Dumps:
    """Converts Python objects to pretty-printed strings using the pprint module.

    This adapter provides human-readable string representations of Python data structures
    with configurable formatting options. Note: This is a one-way conversion only -
    pprint output is not designed to be parseable back to the original object.
    """

    _width: int = 80
    _compact: bool = True
    _media_type: ClassVar[str] = "text/plain"
    _roundtrippable: ClassVar[bool] = False
    _printer: _pp.PrettyPrinter = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_printer",
            _pp.PrettyPrinter(width=self._width, compact=self._compact),
        )

    def __call__(self, value: object) -> str:
        return self._printer.pformat(value)
