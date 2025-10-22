from __future__ import annotations
import importlib
from .class_ import Class
from .function import Function
from dataclasses import dataclass
from collections.abc import Iterable
from functools import cached_property
from typing import Optional, get_origin
from types import ModuleType, GenericAlias
from .object_description import extract_object_description
from taew.adapters.python.ast.for_browsing_code_tree.module import Module as AstModule


@dataclass(eq=False, frozen=True)
class Module:
    _ast_module: AstModule
    _module_name: str

    @staticmethod
    def get_module(ast_module: AstModule, module_name: str) -> Module:
        return Module(ast_module, module_name)

    @cached_property
    def _module(self) -> ModuleType:
        try:
            return importlib.import_module(self._module_name)
        except ModuleNotFoundError as e:
            print(e)
            raise ImportError(f"Module '{self._module_name}' not found") from e
        except Exception as e:
            raise ImportError(
                f"Failed to import module '{self._module_name}': {e}"
            ) from e

    @cached_property
    def description(self) -> str:
        if "_module" in self.__dict__:
            try:
                return extract_object_description(self._module)
            except Exception:
                return ""
        return self._ast_module.description or ""

    def items(self) -> Iterable[tuple[str, Function | Class]]:
        for name in dir(self._module):
            if name.startswith("_"):
                continue
            try:
                yield name, self[name]
            except KeyError:
                continue

    def __getitem__(self, name: str) -> Function | Class:
        try:
            obj = getattr(self._module, name)
        except AttributeError:
            raise KeyError(f"Object '{name}' not found in module '{self._module_name}'")

        match obj:
            case type():
                try:
                    return Class.from_class(obj, self._module)
                except Exception as e:
                    raise KeyError(f"Cannot wrap '{name}' as Class: {e}")
            case GenericAlias():
                try:
                    return Class.from_class(get_origin(obj), self._module)
                except Exception as e:
                    raise KeyError(f"Cannot wrap '{name}' as Class: {e}")
            case _ if callable(obj):
                try:
                    return Function.from_callable(obj)
                except Exception as e:
                    raise KeyError(f"Cannot wrap '{name}' as Function: {e}")
            case _:
                raise KeyError(f"'{name}' is neither callable nor a class")

    def get(
        self, name: str, default: Optional[Function | Class] = None
    ) -> Optional[Function | Class]:
        try:
            return self[name]
        except KeyError:
            return default

    def __contains__(self, name: str) -> bool:
        if name.startswith("_"):
            return False
        try:
            obj = getattr(self._module, name)
            return isinstance(obj, type) or callable(obj)
        except AttributeError:
            return False

    @property
    def _simple_name(self) -> str:
        return self._module_name.rsplit(".", 1)[-1]
