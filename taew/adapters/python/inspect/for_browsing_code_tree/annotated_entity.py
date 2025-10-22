import inspect
from taew.domain.argument import ArgumentKind
from taew.ports.for_browsing_code_tree import is_protocol
from docstring_parser import DocstringMeta, DocstringParam
from typing import get_origin, get_args, Any, Optional, cast, Union


class DefaultValue:
    """Inspect adapter implementation of default parameter values."""

    def __init__(self, param: inspect.Parameter) -> None:
        self._param = param

    def is_empty(self) -> bool:
        """Returns True if no default value is available."""
        return self._param.default is inspect.Parameter.empty

    @property
    def value(self) -> Any:
        """Returns the actual default value. Only call if not is_empty()."""
        return self._param.default


class AnnotatedEntity:
    def __init__(
        self, annotation: Any, docstring_param: Optional[DocstringMeta] = None
    ) -> None:
        self._annotation = annotation
        self._docstring_param = docstring_param

    @property
    def annotation(self) -> Any:
        return self._annotation

    @property
    def spec(self) -> tuple[Any, tuple[Any, ...]]:
        # Handle empty annotations gracefully
        if self._annotation is inspect.Parameter.empty:
            return None, ()
        return get_origin(self._annotation), get_args(self._annotation)

    @property
    def description(self) -> str:
        return (
            self._docstring_param.description
            if self._docstring_param and self._docstring_param.description
            else ""
        )


class Argument(AnnotatedEntity):
    """Inspect adapter implementation of function/method parameters with type validation."""

    def __init__(
        self, param: inspect.Parameter, docstring_param: Optional[DocstringParam] = None
    ):
        super().__init__(param.annotation, docstring_param)
        self._param = param

    @property
    def default(self) -> DefaultValue:
        """Returns default value information for this parameter."""
        return DefaultValue(self._param)

    @property
    def kind(self) -> ArgumentKind:
        """Returns the parameter kind (positional, keyword, etc.)."""
        # This is correct if value is within Literal[0,1,2,3,4]
        # it's up to adapter to ensure this and avoid extra conversion
        return cast(ArgumentKind, self._param.kind.value)

    def has_valid_type(self, value: Any) -> bool:
        """Returns True if value is compatible with this argument's type."""
        if is_protocol(self):
            return True  # cannot check protocol type compliance
        annotation = self._param.annotation
        if annotation == Any:
            return True
        # Handle variadic arguments (*args and **kwargs) - must check container type even with no annotation
        if self._param.kind == inspect.Parameter.VAR_POSITIONAL:
            # *args: value should be tuple, validate each element against annotation if present
            if not isinstance(value, tuple):
                return False
            if annotation is inspect.Parameter.empty:
                return True  # No type hint = accept any tuple
            if isinstance(annotation, type):
                return all(isinstance(item, annotation) for item in value)  # type: ignore[misc]
            return True  # Permissive for complex annotation types

        if self._param.kind == inspect.Parameter.VAR_KEYWORD:
            # **kwargs: value should be dict, validate each value against annotation if present
            if not isinstance(value, dict):
                return False
            if annotation is inspect.Parameter.empty:
                return True  # No type hint = accept any dict
            if isinstance(annotation, type):
                return all(isinstance(v, annotation) for v in value.values())  # type: ignore[misc]
            return True  # Permissive for complex annotation types

        # For non-variadic arguments, no type hint means accept anything
        if annotation is inspect.Parameter.empty:
            return True

        # Handle basic types
        if isinstance(annotation, type):
            return isinstance(value, annotation)

        # Handle typing generics (Optional, Union, etc.)
        origin = get_origin(annotation)
        if origin is Union:
            args = get_args(annotation)
            return any(isinstance(value, arg) for arg in args if isinstance(arg, type))
        # Handle Optional (which is Union[T, None])
        if origin is type(Union):
            args = get_args(annotation)
            if len(args) == 2 and type(None) in args:
                non_none_type = next(t for t in args if t is not type(None))
                if value is None or (
                    isinstance(non_none_type, type) and isinstance(value, non_none_type)
                ):
                    return True
            return any(isinstance(value, arg) for arg in args if isinstance(arg, type))

        return True  # Fallback: permissive for complex types


class ReturnValue(AnnotatedEntity):
    pass
