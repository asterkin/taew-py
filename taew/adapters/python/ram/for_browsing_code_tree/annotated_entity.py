from typing import Any
from dataclasses import dataclass
from taew.domain.argument import ArgumentKind


@dataclass(eq=False, frozen=True)
class DefaultValue:
    """RAM adapter implementation of default parameter values."""

    _value: Any
    _is_empty: bool

    def is_empty(self) -> bool:
        """Returns True if no default value is available."""
        return self._is_empty

    @property
    def value(self) -> Any:
        """Returns the actual default value. Only call if not is_empty()."""
        return self._value


@dataclass(eq=False, frozen=True)
class AnnotatedEntity:
    annotation: Any
    spec: tuple[Any, tuple[Any, ...]]
    description: str


@dataclass(eq=False, frozen=True)
class ReturnValue(AnnotatedEntity):
    pass


@dataclass(eq=False, frozen=True)
class Argument(AnnotatedEntity):
    """RAM adapter implementation of function/method parameters with type validation."""

    _default_value: Any
    _has_default: bool
    kind: ArgumentKind

    @property
    def default(self) -> DefaultValue:
        """Returns default value information for this parameter."""
        return DefaultValue(_value=self._default_value, _is_empty=not self._has_default)

    def has_valid_type(self, value: Any) -> bool:
        """Returns True if value is compatible with this argument's type."""
        # Simple type checking for basic types
        if self.annotation in (int, str, float, bool, type(None)):
            return isinstance(value, self.annotation)
        # For complex types, return True (permissive for RAM adapter)
        return True
