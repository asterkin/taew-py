import unittest
import tempfile
from pathlib import Path
from textwrap import dedent
from taew.adapters.python.ast.for_browsing_code_tree.module import Module


class TestAstModuleAdapter(unittest.TestCase):
    def _write_module(self, content: str) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".py", mode="w", encoding="utf-8"
        )
        tmp.write(dedent(content))
        tmp.close()
        return Path(tmp.name)

    def test_description(self) -> None:
        path = self._write_module("""
            \"\"\"Module docstring.\"\"\"
            def foo(): pass
        """)
        mod = Module.from_path(path)
        self.assertEqual(mod.description, "Module docstring.")

    def test_description_missing(self) -> None:
        path = self._write_module("def foo(): pass")
        mod = Module.from_path(path)
        self.assertEqual(mod.description, "")

    def test_version_found(self) -> None:
        path = self._write_module("""
            __version__ = "1.2.3"
            def foo(): pass
        """)
        mod = Module.from_path(path)
        self.assertEqual(mod.version, "1.2.3")

    def test_version_missing(self) -> None:
        path = self._write_module("def foo(): pass")
        mod = Module.from_path(path)
        self.assertEqual(mod.version, "")

    def test_getitem_function(self) -> None:
        path = self._write_module("""
            def foo():
                \"\"\"Function doc.\"\"\"
                pass
        """)
        mod = Module.from_path(path)
        func = mod["foo"]
        self.assertEqual(func.description, "Function doc.")

    def test_getitem_class(self) -> None:
        path = self._write_module("""
            class Bar:
                \"\"\"Class doc.\"\"\"
                pass
        """)
        mod = Module.from_path(path)
        cls = mod["Bar"]
        self.assertEqual(cls.description, "Class doc.")

    def test_getitem_not_found(self) -> None:
        path = self._write_module("def foo(): pass")
        mod = Module.from_path(path)
        with self.assertRaises(KeyError):
            _ = mod["bar"]

    def test_bool_true_public_function(self) -> None:
        path = self._write_module("def foo(): pass")
        mod = Module.from_path(path)
        self.assertTrue(mod)

    def test_bool_true_public_class(self) -> None:
        path = self._write_module("class Foo: pass")
        mod = Module.from_path(path)
        self.assertTrue(mod)

    def test_bool_true_all_assign(self) -> None:
        path = self._write_module("__all__ = ['foo']")
        mod = Module.from_path(path)
        self.assertTrue(mod)

    def test_bool_false_private(self) -> None:
        path = self._write_module("def _foo(): pass\nclass _Bar: pass")
        mod = Module.from_path(path)
        self.assertFalse(mod)

    def test_invalid_syntax_raises(self) -> None:
        path = self._write_module("def invalid(: pass")
        with self.assertRaises(SyntaxError):
            Module.from_path(path)


if __name__ == "__main__":
    unittest.main()
