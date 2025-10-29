"""Common base class for Root implementations."""

from pathlib import Path
from typing import Optional, cast

from .module import Module as ModuleAdapter
from .package import Package as PackageAdapter
from taew.adapters.python.ast.for_browsing_code_tree.module import Module as AstModule
from taew.adapters.python.path.for_browsing_code_tree.folder import (
    Folder as FolderBase,
)
from taew.ports.for_browsing_code_tree import (
    Module as ModuleProtocol,
    Package as PackageProtocol,
)


class RootBase(FolderBase):
    """Base class for Root with underscore-prefixed parameter naming.

    Uses _root_path parameter to align with dataclass Configure naming convention.
    """

    def __init__(self, _root_path: Path, name_prefix: Optional[str] = None) -> None:
        """Initialize Root with underscore-prefixed parameter.

        Args:
            _root_path: Path to the root directory
            name_prefix: Optional prefix for module names
        """
        super().__init__(
            _root_path,
            "" if name_prefix is None else name_prefix,
            _create_module=lambda p, n: cast(
                ModuleProtocol, ModuleAdapter.get_module(AstModule.from_path(p), n)
            ),
            _create_package=lambda p, n: cast(
                PackageProtocol, PackageAdapter.get_package(p, n)
            ),
        )
