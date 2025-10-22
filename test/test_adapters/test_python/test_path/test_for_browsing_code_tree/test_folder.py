import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from taew.adapters.python.path.for_browsing_code_tree.folder import Folder


class TestFolder(unittest.TestCase):
    def setUp(self) -> None:
        self.folder_path = Path("/mock/project")
        self.module_path = self.folder_path / "mod1.py"
        self.package_path = self.folder_path / "pkg1"

        self.mock_module_factory = MagicMock(return_value="MockedModule")
        self.mock_package_factory = MagicMock(return_value="MockedPackage")

        self.folder = Folder(
            _folder_path=self.folder_path,
            _module_prefix="mypkg",
            _create_module=self.mock_module_factory,
            _create_package=self.mock_package_factory,
        )

    @patch("pathlib.Path.iterdir")
    @patch("pathlib.Path.is_file", new=lambda self: self.suffix == ".py")  # type: ignore
    @patch("pathlib.Path.is_dir", new=lambda self: self.suffix != ".py")  # type: ignore
    def test_items_from_filesystem(self, mock_iterdir: MagicMock) -> None:
        mock_iterdir.return_value = [self.module_path, self.package_path]

        items = dict(self.folder.items())

        self.assertEqual(items["mod1"], "MockedModule")
        self.assertEqual(items["pkg1"], "MockedPackage")

        self.mock_module_factory.assert_called_with(self.module_path, "mypkg.mod1")
        self.mock_package_factory.assert_called_with(self.package_path, "mypkg.pkg1")

    @patch("pathlib.Path.exists", return_value=True)
    def test_getitem_module(self, _: MagicMock) -> None:
        result = self.folder["mod1"]
        self.assertEqual(result, "MockedModule")
        self.mock_module_factory.assert_called_with(
            self.folder_path / "mod1.py", "mypkg.mod1"
        )

    @patch("pathlib.Path.is_dir", return_value=True)
    def test_getitem_package(self, _: MagicMock) -> None:
        result = self.folder["pkg1"]
        self.assertEqual(result, "MockedPackage")
        self.mock_package_factory.assert_called_with(
            self.folder_path / "pkg1", "mypkg.pkg1"
        )

    @patch("pathlib.Path.exists", return_value=False)
    @patch("pathlib.Path.is_dir", return_value=False)
    def test_getitem_keyerror(self, *_: MagicMock) -> None:
        with self.assertRaises(KeyError) as ctx:
            self.folder["nonexistent"]
        self.assertIn("nonexistent", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
