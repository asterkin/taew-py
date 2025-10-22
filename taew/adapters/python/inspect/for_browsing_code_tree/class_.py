from __future__ import annotations
import re
from types import ModuleType
from .function import Function
from dataclasses import dataclass
from typing import Any, Iterable, Pattern, Optional
from .object_description import extract_object_description
from taew.ports.for_browsing_code_tree import Function as FunctionProtocol


_PRIVATE_METHOD_PATTERN: Pattern[str] = re.compile(r"^_[^_].*|^__(?!.*__$).*")


def _is_private(func_name: str) -> bool:
    return bool(_PRIVATE_METHOD_PATTERN.match(func_name))


@dataclass(eq=False, frozen=True)
class Class:
    _class: type
    py_module: ModuleType

    @classmethod
    def from_class(cls, class_obj: Any, py_module: ModuleType) -> Class:
        """Factory method with validation."""
        if not hasattr(class_obj, "__class__") or not isinstance(class_obj, type):
            raise TypeError(f"Expected class, got {type(class_obj).__name__}")
        return cls(class_obj, py_module)

    @property
    def description(self) -> str:
        try:
            return extract_object_description(self._class)
        except Exception:
            return ""

    @property
    def type_(self) -> type:
        return self._class

    def items(self) -> Iterable[tuple[str, FunctionProtocol]]:
        """Yield public methods including __magic_methods__, excluding inherited from object."""
        try:
            # Get methods defined in this class only, not inherited
            class_dict = self._class.__dict__
            for name, method in class_dict.items():
                if callable(method) and not _is_private(name):
                    try:
                        yield name, Function.from_callable(method)
                    except (TypeError, ValueError):
                        continue
        except Exception:
            return

    def __getitem__(self, name: str) -> FunctionProtocol:
        if _is_private(name) and name != "__init__":
            raise KeyError(f"Method '{name}' is private")

        try:
            method = getattr(self._class, name)
            if not callable(method):
                raise KeyError(f"'{name}' is not callable")
            return Function.from_callable(method)
        except AttributeError:
            raise KeyError(f"Method '{name}' not found")
        except (TypeError, ValueError) as e:
            raise KeyError(f"Cannot create Function for '{name}': {e}")

    def get(
        self, name: str, default: Optional[FunctionProtocol] = None
    ) -> Optional[FunctionProtocol]:
        try:
            return self[name]
        except KeyError:
            return default

    def __contains__(self, name: str) -> bool:
        if _is_private(name) and name != "__init__":
            return False
        try:
            method = getattr(self._class, name)
            return callable(method)
        except AttributeError:
            return False

    def __call__(self, *args: Any, **kwargs: Any) -> object:
        return self._class(*args, **kwargs)
