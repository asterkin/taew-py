from dataclasses import dataclass


def _has_duplicates(seq: tuple[object, ...]) -> bool:
    n = len(seq)
    for i in range(n):
        for j in range(i + 1, n):
            if seq[i] == seq[j]:
                return True
    return False


@dataclass(eq=False, frozen=True)
class ChoicesBase:
    """Base for streaming choices on top of fixed-width int framing.

    Initializes IntStreamBase with computed width based on number of choices
    (always unsigned, big-endian). Stores `_choices` for index mapping.
    """

    _choices: tuple[object, ...] = ()

    def __post_init__(self) -> None:
        if not self._choices:
            raise ValueError("_choices must contain at least one value")
        if _has_duplicates(self._choices):
            raise ValueError("_choices must not contain duplicate values")
