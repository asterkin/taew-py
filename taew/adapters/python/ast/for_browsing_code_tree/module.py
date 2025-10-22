from __future__ import annotations
import ast
from pathlib import Path


class Function:
    def __init__(self, node: ast.FunctionDef) -> None:
        self._node = node

    @property
    def description(self) -> str:
        return ast.get_docstring(self._node) or ""


class Class:
    def __init__(self, node: ast.ClassDef) -> None:
        self._node = node

    @property
    def description(self) -> str:
        return ast.get_docstring(self._node) or ""


class Module:
    def __init__(self, tree: ast.Module) -> None:
        self._tree = tree

    @staticmethod
    def from_path(path: Path) -> Module:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            return Module(tree)
        except Exception as e:
            raise SyntaxError(f"Failed to parse module at {path}: {e}") from e

    @property
    def description(self) -> str:
        return ast.get_docstring(self._tree) or ""

    @property
    def version(self) -> str:
        for node in self._tree.body:
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "__version__"
                and isinstance(node.value, ast.Constant)
            ):
                return str(node.value.value)
        return ""

    def __getitem__(self, key: str) -> Function | Class:
        for node in self._tree.body:
            match node:
                case ast.FunctionDef(name=name) if name == key:
                    return Function(node)
                case ast.ClassDef(name=name) if name == key:
                    return Class(node)
                case _:
                    continue
        raise KeyError(key)

    def __bool__(self) -> bool:
        for node in self._tree.body:
            match node:
                case ast.FunctionDef(name=name) | ast.ClassDef(name=name) if (
                    not name.startswith("_")
                ):
                    return True
                case ast.Assign(targets=[ast.Name(id="__all__")]):
                    return True
                case _:
                    continue
        return False
