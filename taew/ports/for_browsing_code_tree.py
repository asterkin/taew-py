from __future__ import annotations
from types import ModuleType
from functools import cached_property
from collections.abc import Mapping

from taew.domain.argument import ArgumentKind
from typing import Protocol, Any, Iterable, TypeGuard, Optional, cast


class DefaultValue(Protocol):
    """Protocol for representing default parameter values."""

    def is_empty(self) -> bool:
        """Returns True if no default value is available."""
        ...

    @property
    def value(self) -> Any:
        """Returns the actual default value. Only call if not is_empty()."""
        ...


class AnnotatedEntity(Protocol):
    """Protocol for entities that have type annotations and descriptions."""

    @property
    def annotation(self) -> Any:
        """The type annotation of this entity."""
        ...

    @property
    def spec(self) -> tuple[Any, tuple[Any, ...]]:
        """Specification tuple containing type and type arguments."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description of this entity."""
        ...


class ReturnValue(AnnotatedEntity, Protocol):
    pass


class Argument(AnnotatedEntity, Protocol):
    """Protocol for function/method parameters with type validation capabilities."""

    @property
    def default(self) -> DefaultValue:
        """Returns default value information for this parameter."""
        ...

    @property
    def kind(self) -> ArgumentKind:
        """Returns the parameter kind (positional, keyword, etc.)."""
        ...

    def has_valid_type(self, value: Any) -> bool:
        """Returns True if value is compatible with this argument's type."""
        ...


class Function(Protocol):
    @property
    def description(self) -> str: ...

    @property
    def returns(self) -> ReturnValue: ...

    def items(self) -> Iterable[tuple[str, Argument]]: ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class Call(Protocol):
    def __call__(self, func: Function, *args: Any, **kwds: Any) -> Any: ...


class Class(Protocol):
    @property
    def description(self) -> str: ...

    @property
    def py_module(self) -> ModuleType: ...

    @property
    def type_(self) -> type: ...

    def items(self) -> Iterable[tuple[str, Function]]: ...

    def __getitem__(self, name: str) -> Function: ...

    def get(
        self, name: str, default: Optional[Function] = None
    ) -> Optional[Function]: ...

    def __contains__(self, name: str) -> bool: ...

    def __call__(self, *args: Any, **kwargs: Any) -> object: ...


class Module(Protocol):
    @cached_property
    def description(self) -> str: ...

    def items(self) -> Iterable[tuple[str, Function | Class]]: ...

    def __getitem__(self, name: str) -> Function | Class: ...

    def get(
        self, name: str, default: Optional[Function | Class] = None
    ) -> Optional[Function | Class]: ...

    def __contains__(self, name: str) -> bool: ...


class Package(Protocol):
    @cached_property
    def description(self) -> str: ...

    @property
    def version(self) -> str: ...

    def items(self) -> Iterable[tuple[str, Module | Package | Function | Class]]: ...

    def __getitem__(self, name: str) -> Module | Package | Function | Class: ...

    def get(
        self, name: str, default: Optional[Module | Package | Function | Class] = None
    ) -> Optional[Module | Package | Function | Class]: ...

    def __contains__(self, name: str) -> bool: ...


class Root(Protocol):
    def items(self) -> Iterable[tuple[str, Package | Module]]: ...

    def __getitem__(self, name: str) -> Package | Module: ...

    def get(
        self, name: str, default: Optional[Package | Module] = None
    ) -> Optional[Package | Module]: ...

    def __contains__(self, name: str) -> bool: ...

    def change_root(self, new_root: str) -> Root: ...


# when Python 3.14 is GA, switch to __match__ methods
def is_package(obj: object) -> TypeGuard[Package]:
    return obj.__class__.__name__ == "Package"


def is_module(obj: object) -> TypeGuard[Module]:
    return obj.__class__.__name__ == "Module"


def is_class(obj: object) -> TypeGuard[Class]:
    return obj.__class__.__name__ == "Class"


def is_function(obj: object) -> TypeGuard[Function]:
    return obj.__class__.__name__ == "Function"


def _is_protocol(annotation: type) -> bool:
    """Check if a type is a Protocol type.

    Uses the robust __subclasscheck__ comparison approach that works
    even without @runtime_checkable decorator.
    """
    from typing import Protocol

    f1 = annotation.__class__.__subclasscheck__  # type: ignore
    f2 = Protocol.__class__.__subclasscheck__  # type: ignore
    return f1 == f2  # type: ignore


def _is_abc(annotation: type) -> bool:
    """Check if a type is an Abstract Base Class."""
    return bool(getattr(annotation, "__abstractmethods__", None))


def is_interface_type(annotation: type) -> bool:
    """Check if a type is either a Protocol or ABC."""
    return _is_protocol(annotation) or _is_abc(annotation)


def is_protocol(arg: Argument) -> bool:
    """Check if an Argument annotation is a Protocol type."""
    return _is_protocol(arg.annotation)


def is_abc(arg: Argument) -> bool:
    """Check if an Argument annotation is an Abstract Base Class."""
    return _is_abc(arg.annotation)


def is_interface(item: Argument | Class) -> bool:
    """Check if an Argument annotation or Class type is an interface type (Protocol or ABC)."""
    if is_class(item):
        return is_interface_type(item.type_)
    else:
        return is_interface_type(item.annotation)  # type: ignore[union-attr]


def is_interface_mapping(arg: Argument) -> Optional[type]:
    """Check if argument is a mapping to interfaces, returning the interface type if so.

    Detects patterns like:
    - Mapping[type, SomeProtocol]
    - Dict[str, SomeABC]
    - Mapping[KeyType, InterfaceType]

    Returns the interface type if found, None otherwise.
    """
    origin, args = arg.spec
    if origin not in {Mapping, dict}:
        return None
    if len(args) != 2:
        return None
    _, value_type = args
    return cast(type, value_type) if is_interface_type(value_type) else None
