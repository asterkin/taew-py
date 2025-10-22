from typing import Literal, TypeAlias
from dataclasses import dataclass, field, InitVar

Width: TypeAlias = Literal[4, 8]
FormatType: TypeAlias = Literal["<", ">"]
TypeCode: TypeAlias = Literal["f", "d"]


@dataclass(eq=False, frozen=True)
class FloatStreamBase:
    """Base configuration for IEEE-754 float streaming.

    Configurator provides width (4/8), byte-order format ('<'/'>'), and
    struct type code ('f'/'d'). Base validates and computes `_fmt` once.
    """

    _width: Width = 8
    _format: InitVar[FormatType] = ">"
    _type: InitVar[TypeCode] = "d"
    _fmt: str = field(init=False)

    def __post_init__(self, _format: FormatType, _type: TypeCode) -> None:
        if (self._width, _type) not in ((4, "f"), (8, "d")):
            raise ValueError("Width/type mismatch: use 4/'f' or 8/'d'")
        if _format not in ("<", ">"):
            raise ValueError("_format must be '<' or '>'")
        object.__setattr__(self, "_fmt", f"{_format}{_type}")
