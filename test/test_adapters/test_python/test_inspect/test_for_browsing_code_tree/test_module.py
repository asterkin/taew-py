import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch, MagicMock
from taew.adapters.python.inspect.for_browsing_code_tree.module import Module
from taew.adapters.python.inspect.for_browsing_code_tree.class_ import Class
import taew.adapters.python.inspect.for_browsing_code_tree.module as module_impl
from taew.adapters.python.ast.for_browsing_code_tree.module import Module as AstModule


class TestModule(unittest.TestCase):
    def setUp(self) -> None:
        self.ast_module = MagicMock(spec=AstModule)
        self.fake_path = Path("/fake/module/path.py")

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.module.importlib.import_module"
    )
    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.module.extract_object_description"
    )
    def test_successful_import_and_description(
        self, mock_extract_description: MagicMock, mock_import_module: MagicMock
    ) -> None:
        dummy_mod = ModuleType("dummy")
        mock_import_module.return_value = dummy_mod
        mock_extract_description.return_value = "This is a test module"

        mod = Module.get_module(self.ast_module, "dummy")
        # force import
        _ = mod._module  # type: ignore
        self.assertEqual(mod.description, "This is a test module")
        mock_extract_description.assert_called_once_with(dummy_mod)

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.module.importlib.import_module",
        side_effect=ModuleNotFoundError,
    )
    def test_module_not_found(self, mock_import_module: MagicMock) -> None:
        mod = Module.get_module(self.ast_module, "nonexistent")
        with self.assertRaises(ImportError):
            _ = mod._module  # type: ignore

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.module.importlib.import_module",
        side_effect=RuntimeError("crash"),
    )
    def test_module_import_error(self, mock_import_module: MagicMock) -> None:
        mod = Module.get_module(self.ast_module, "broken")
        with self.assertRaises(ImportError):
            _ = mod._module  # type: ignore

    def test_ast_description_without_import(self) -> None:
        self.ast_module.description = "AST description"
        mod = Module.get_module(self.ast_module, "dummy")
        self.assertEqual(mod.description, "AST description")

    def test_items_filter_and_access(self) -> None:
        with (
            patch.object(module_impl.Class, "from_class", return_value="WrappedClass"),  # type: ignore
            patch.object(
                module_impl.Function,  # type: ignore
                "from_callable",
                return_value="WrappedFunction",
            ),
            patch.object(module_impl.importlib, "import_module") as mock_import_module,  # type: ignore
        ):
            test_module = ModuleType("test_module")
            test_module.MyClass = type("MyClass", (), {})  # type: ignore
            test_module.my_func = lambda x: x  # type: ignore
            test_module._internal = "skip"  # type: ignore
            mock_import_module.return_value = test_module

            ast_module = MagicMock()
            mod = module_impl.Module.get_module(ast_module, "test_module")

            items = dict(mod.items())

            self.assertEqual(items["MyClass"], "WrappedClass")
            self.assertEqual(items["my_func"], "WrappedFunction")
            self.assertNotIn("_internal", items)

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.module.importlib.import_module"
    )
    def test_getitem_errors(self, mock_import_module: MagicMock) -> None:
        dummy_mod = ModuleType("dummy")
        dummy_mod.value = 42  # type: ignore
        mock_import_module.return_value = dummy_mod

        mod = Module.get_module(self.ast_module, "dummy")

        with self.assertRaises(KeyError):
            _ = mod["value"]

        with self.assertRaises(KeyError):
            _ = mod["not_there"]

    def test_simple_name(self) -> None:
        mod = Module.get_module(self.ast_module, "package.module")
        self.assertEqual(mod._simple_name, "module")  # type: ignore

    @patch(
        "taew.adapters.python.inspect.for_browsing_code_tree.module.importlib.import_module"
    )
    def test_generic_alias_support(self, mock_import_module: MagicMock) -> None:
        """Test that dict[str, Something] type aliases are properly handled."""
        with patch.object(
            Class, "from_class", return_value="WrappedDict"
        ) as mock_from_class:  # type: ignore
            dummy_mod = ModuleType("dummy")
            # Create a type alias like RatesRepository: TypeAlias = dict[str, Rate]
            dummy_mod.RatesRepository = dict[str, int]  # type: ignore
            mock_import_module.return_value = dummy_mod

            mod = Module.get_module(self.ast_module, "dummy")

            # Access the type alias
            result = mod["RatesRepository"]

            # Should return wrapped class
            self.assertEqual(result, "WrappedDict")

            # Verify that from_class was called with dict (the origin of dict[str, int])
            mock_from_class.assert_called_once_with(dict, dummy_mod)


if __name__ == "__main__":
    unittest.main()
