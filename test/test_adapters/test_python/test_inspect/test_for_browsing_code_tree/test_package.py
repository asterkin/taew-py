import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from taew.adapters.python.inspect.for_browsing_code_tree.package import Package


class TestPackage(unittest.TestCase):
    def setUp(self) -> None:
        self.package_path = Path("/fake/package")
        self.package_name = "fake_package"

    def test_description_empty_when_no_init(self) -> None:
        pkg = Package(self.package_path, self.package_name, _init_module=None)
        self.assertEqual(pkg.description, "")

    def test_description_from_ast_module(self) -> None:
        ast_mod = MagicMock()
        ast_mod.description = "Package docstring"
        pkg = Package(self.package_path, self.package_name, _init_module=ast_mod)
        self.assertEqual(pkg.description, "Package docstring")

    def test_version_empty_when_no_init(self) -> None:
        pkg = Package(self.package_path, self.package_name, _init_module=None)
        self.assertEqual(pkg.version, "")

    def test_version_from_ast_module(self) -> None:
        ast_mod = MagicMock()
        ast_mod.version = "1.2.3"
        pkg = Package(self.package_path, self.package_name, _init_module=ast_mod)
        self.assertEqual(pkg.version, "1.2.3")

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.package._get_package_folder"
    )
    def test_items_from_filesystem_when_empty(self, mock_get_folder: MagicMock) -> None:
        mock_folder = MagicMock()
        mock_folder.items.return_value = [
            ("mod1", "MockedModule"),
            ("subpkg", "MockedPackage"),
        ]
        mock_get_folder.return_value = mock_folder

        pkg = Package.get_package(self.package_path, self.package_name)

        items = dict(pkg.items())

        self.assertEqual(items["mod1"], "MockedModule")
        self.assertEqual(items["subpkg"], "MockedPackage")

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.module.Module.get_module"
    )
    def test_items_delegates_when_not_empty(self, mock_get_module: MagicMock) -> None:
        mock_module = MagicMock()
        mock_module.items.return_value = [("X", "Y")]
        mock_get_module.return_value = mock_module

        ast_mod = MagicMock()
        ast_mod.__bool__.return_value = True

        pkg = Package(self.package_path, self.package_name, _init_module=ast_mod)
        self.assertEqual(dict(pkg.items()), {"X": "Y"})

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.module.Module.get_module"
    )
    def test_getitem_delegates_when_not_empty(self, mock_get_module: MagicMock) -> None:
        mock_module = MagicMock()
        mock_module.__getitem__.return_value = "Z"
        mock_get_module.return_value = mock_module

        ast_mod = MagicMock()
        ast_mod.__bool__.return_value = True

        pkg = Package(self.package_path, self.package_name, _init_module=ast_mod)
        self.assertEqual(pkg["any"], "Z")

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.package.AstModule.from_path"
    )
    def test_get_package_constructs_correctly(self, mock_from_path: MagicMock) -> None:
        mock_ast_mod = MagicMock()
        mock_from_path.return_value = mock_ast_mod

        path = Path("/fake/mypkg")
        with patch("pathlib.Path.exists", return_value=True):
            pkg = Package.get_package(path, "mypkg")

        self.assertEqual(pkg._package_path, path)  # type: ignore
        self.assertEqual(pkg._package_name, "mypkg")  # type: ignore
        self.assertEqual(pkg._init_module, mock_ast_mod)  # type: ignore


if __name__ == "__main__":
    unittest.main()
