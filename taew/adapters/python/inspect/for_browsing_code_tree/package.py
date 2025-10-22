from __future__ import annotations
from pathlib import Path
from .module import Module
from typing import Optional, cast
from dataclasses import dataclass
from collections.abc import Iterable
from functools import cached_property
from taew.ports.for_browsing_code_tree import Function, Class
from taew.adapters.python.path.for_browsing_code_tree.folder import Folder
from taew.adapters.python.ast.for_browsing_code_tree.module import Module as AstModule


def _get_package_folder(packege_path: Path, package_name: str) -> Folder:
    from ._folder import Folder as FolderImpl

    return FolderImpl(
        root_path=packege_path,
        name_prefix=package_name,
    )


@dataclass(eq=False, frozen=True)
class Package:
    _package_path: Path
    _package_name: str
    _init_module: Optional[AstModule] = None
    _folder_impl: Optional[Folder] = None

    @staticmethod
    def get_package(package_path: Path, package_name: str) -> Package:
        init_path = package_path / "__init__.py"
        init_module = AstModule.from_path(init_path) if init_path.exists() else None
        folder_impl = (
            _get_package_folder(package_path, package_name)
            if not (init_module)
            else None
        )

        return Package(
            _package_path=package_path,
            _package_name=package_name,
            _init_module=init_module,
            _folder_impl=folder_impl,
        )

    @cached_property
    def _delegate_module(self) -> Module:
        if self._init_module is None:
            raise ValueError(
                f"Package '{self._package_name}' has no __init__.py module."
            )
        return Module.get_module(self._init_module, self._package_name)

    @cached_property
    def description(self) -> str:
        return self._init_module.description if self._init_module is not None else ""

    @property
    def version(self) -> str:
        return self._init_module.version if self._init_module is not None else ""

    def items(self) -> Iterable[tuple[str, Package | Module | Function | Class]]:
        if self._folder_impl is not None:
            for name, item in self._folder_impl.items():
                if not name.startswith("_"):
                    yield name, cast(Package | Module | Function | Class, item)
        else:
            for name, module_item in self._delegate_module.items():
                yield name, cast(Function | Class, module_item)

    def __getitem__(self, name: str) -> Package | Module | Function | Class:
        if self._folder_impl is not None:
            return cast(Package | Module | Function | Class, self._folder_impl[name])
        elif self._init_module is not None:
            return cast(Function | Class, self._delegate_module[name])
        else:
            raise RuntimeError(
                f"Package '{self._package_name}' has no items to retrieve."
            )

    def get(
        self, name: str, default: Optional[Package | Module | Function | Class] = None
    ) -> Optional[Package | Module | Function | Class]:
        try:
            return self[name]
        except (KeyError, RuntimeError):
            return default

    def __contains__(self, name: str) -> bool:
        if name.startswith("_"):
            return False
        try:
            self[name]
            return True
        except (KeyError, RuntimeError):
            return False
