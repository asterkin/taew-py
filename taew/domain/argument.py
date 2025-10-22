from typing import NewType

"""
In Python, enums are annoying, since I need to always write ArgumentKind.POSITIONAL_ONLY, etc.
This eliminates the enum verbosity while maintaining type safety:

Advantages:

- Clean imports: from taew.ports import VAR_POSITIONAL
- Direct usage: if arg.kind == VAR_POSITIONAL: instead of ArgumentKind.VAR_POSITIONAL
- Order preserved while arg.kind < KEYWORD_ONLY: to check if arg is a positional argument
- Type safety: Literal provides compile-time checking
- Inspect compatibility: Same integer values as inspect.Parameter.kind
- No protocol overhead: Direct integer comparisons

Pattern matching becomes elegant:
match arg.kind:
    case POSITIONAL_ONLY | POSITIONAL_OR_KEYWORD:
        # handle normal args
    case VAR_POSITIONAL:
        # handle *args
    case VAR_KEYWORD:
        # handle **kwargs
Enums are overkill for simple integer constants, and your approach gives better ergonomics without sacrificing type safety.
"""

ArgumentKind = NewType("ArgumentKind", int)

POSITIONAL_ONLY = ArgumentKind(0)
POSITIONAL_OR_KEYWORD = ArgumentKind(1)
VAR_POSITIONAL = ArgumentKind(2)
KEYWORD_ONLY = ArgumentKind(3)
VAR_KEYWORD = ArgumentKind(4)

__all__ = [
    "POSITIONAL_ONLY",
    "POSITIONAL_OR_KEYWORD",
    "VAR_POSITIONAL",
    "KEYWORD_ONLY",
    "VAR_KEYWORD",
    "ArgumentKind",
]
