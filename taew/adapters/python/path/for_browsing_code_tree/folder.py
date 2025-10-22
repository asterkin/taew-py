from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from collections.abc import Callable, Iterable
from typing import Optional
from taew.ports.for_browsing_code_tree import Module, Package


@dataclass(eq=False, frozen=True)
class Folder:
    _folder_path: Path
    _module_prefix: str  # e.g., 'myproject.subpkg'
    _create_module: Callable[[Path, str], Module]
    _create_package: Callable[[Path, str], Package]

    def items(self) -> Iterable[tuple[str, Package | Module]]:
        for path in self._folder_path.iterdir():
            name = path.stem if path.is_file() else path.name
            fqname = f"{self._module_prefix}.{name}" if self._module_prefix else name

            if path.is_dir():
                yield name, self._create_package(path, fqname)
            elif path.is_file() and path.suffix == ".py":
                yield name, self._create_module(path, fqname)

    def __getitem__(self, name: str) -> Package | Module:
        module_path = self._folder_path / f"{name}.py"
        package_path = self._folder_path / name

        fqname = f"{self._module_prefix}.{name}" if self._module_prefix else name

        if package_path.is_dir():
            return self._create_package(package_path, fqname)
        elif module_path.exists():
            return self._create_module(module_path, fqname)

        raise KeyError(f"'{name}' not found in '{self._folder_path}'")

    def get(
        self, name: str, default: Optional[Package | Module] = None
    ) -> Optional[Package | Module]:
        try:
            return self[name]
        except KeyError:
            return default

    def __contains__(self, name: str) -> bool:
        module_path = self._folder_path / f"{name}.py"
        package_path = self._folder_path / name
        return package_path.is_dir() or module_path.exists()
