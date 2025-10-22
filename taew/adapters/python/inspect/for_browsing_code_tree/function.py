import inspect
from dataclasses import dataclass
from typing import Any, Iterable, Callable
from docstring_parser import parse, Docstring
from .annotated_entity import Argument, ReturnValue
from taew.domain.function import FunctionInvocationError


@dataclass(frozen=True)
class Function:
    _func: Callable[..., Any]
    _signature: inspect.Signature
    _docstring: Docstring
    _param_docs: dict[str, Any]

    @classmethod
    def from_callable(cls, func: Callable[..., Any]) -> "Function":
        """Create Function from callable with full introspection."""
        if not callable(func):
            raise TypeError(f"Expected callable, got {type(func).__name__}")

        try:
            signature = inspect.signature(func)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot create signature for {func}: {e}") from e

        try:
            docstring_text = inspect.getdoc(func) or ""
            docstring = parse(docstring_text)
        except Exception:
            # Fallback to empty docstring if parsing fails
            docstring = Docstring()  # Could log warning here if logging is available
        try:
            param_docs = (
                {p.arg_name: p for p in docstring.params} if docstring.params else {}
            )
        except (AttributeError, TypeError):
            # Fallback to empty param docs if docstring parsing had issues
            param_docs = {}

        return cls(func, signature, docstring, param_docs)

    @property
    def description(self) -> str:
        if self._docstring and self._docstring.short_description:
            return self._docstring.short_description
        return ""

    @property
    def returns(self) -> ReturnValue:
        return ReturnValue(self._signature.return_annotation, self._docstring.returns)

    def items(self) -> Iterable[tuple[str, Argument]]:
        for param_name, param in self._signature.parameters.items():
            docstring_param = self._param_docs.get(param_name)
            argument = Argument(param, docstring_param)
            yield param_name, argument

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            bound_args = self._signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
        except TypeError as e:
            raise FunctionInvocationError(
                self._func.__qualname__, "signature_error", str(e)
            ) from None

        return self._func(*bound_args.args, **bound_args.kwargs)
