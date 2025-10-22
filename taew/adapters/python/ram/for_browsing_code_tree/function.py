from .call import Call
from typing import NamedTuple, Any
from taew.ports.for_browsing_code_tree import (
    Argument,
    ReturnValue,
    Call as CallProtocol,
)


class Function(NamedTuple):
    description: str
    returns: ReturnValue
    items_: tuple[tuple[str, Argument], ...]
    call: CallProtocol = Call()

    def items(self) -> tuple[tuple[str, Argument], ...]:
        return self.items_

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.call(self, *args, **kwds)
