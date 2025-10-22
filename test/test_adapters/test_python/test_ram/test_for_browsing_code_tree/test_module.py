import unittest
import sys
from taew.ports.for_browsing_code_tree import (
    Module as ModuleProtocol,
    Function as FunctionProtocol,
    Class as ClassProtocol,
)


class TestModule(unittest.TestCase):
    def setUp(self) -> None:
        self._module = sys.modules[self.__module__]

    def _get_module(self) -> ModuleProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.class_ import Class
        from taew.adapters.python.ram.for_browsing_code_tree.module import Module
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function

        # Create dummy Function and Class implementations
        func: FunctionProtocol = Function(
            description="func desc",
            items_=(),
            returns=None,  # type: ignore
            call=None,  # type: ignore
        )
        cls: ClassProtocol = Class(
            description="class desc", _functions={}, py_module=self._module
        )

        return Module(description="test module", items={"f": func, "C": cls})

    def test_description(self) -> None:
        module = self._get_module()
        self.assertEqual(module.description, "test module")

    def test_items_and_getitem(self) -> None:
        module = self._get_module()
        items = dict(module.items())
        self.assertIn("f", items)
        self.assertIn("C", items)
        self.assertIs(module["f"], items["f"])
        self.assertIs(module["C"], items["C"])

    def test_immutable(self) -> None:
        module = self._get_module()
        with self.assertRaises(TypeError):
            module["f"] = None  # type: ignore
        with self.assertRaises(TypeError):
            del module["f"]  # type: ignore


if __name__ == "__main__":
    unittest.main()
