import unittest
import sys
from taew.ports.for_browsing_code_tree import (
    Package as PackageProtocol,
    Function as FunctionProtocol,
    Class as ClassProtocol,
    Module as ModuleProtocol,
)


class TestPackage(unittest.TestCase):
    def setUp(self) -> None:
        self._module = sys.modules[self.__module__]

    def _get_package(self) -> PackageProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.class_ import Class
        from taew.adapters.python.ram.for_browsing_code_tree.module import Module
        from taew.adapters.python.ram.for_browsing_code_tree.package import Package
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function

        # Create dummy Function, Class, and Module implementations
        func: FunctionProtocol = Function(
            description="func desc",
            items_=(),
            returns=None,  # type: ignore
            call=None,  # type: ignore
        )
        cls: ClassProtocol = Class(
            description="class desc", _functions={}, py_module=self._module
        )
        mod: ModuleProtocol = Module(description="module desc", items={})

        return Package(
            description="test package",
            items={"f": func, "C": cls, "m": mod},
            version="1.0.0",
        )

    def test_description(self) -> None:
        package = self._get_package()
        self.assertEqual(package.description, "test package")

    def test_version(self) -> None:
        package = self._get_package()
        self.assertEqual(package.version, "1.0.0")

    def test_items_and_getitem(self) -> None:
        package = self._get_package()
        items = dict(package.items())
        self.assertIn("f", items)
        self.assertIn("C", items)
        self.assertIn("m", items)
        self.assertIs(package["f"], items["f"])
        self.assertIs(package["C"], items["C"])
        self.assertIs(package["m"], items["m"])

    def test_immutable(self) -> None:
        package = self._get_package()
        with self.assertRaises(TypeError):
            package["f"] = None  # type: ignore
        with self.assertRaises(TypeError):
            del package["f"]  # type: ignore


if __name__ == "__main__":
    unittest.main()
