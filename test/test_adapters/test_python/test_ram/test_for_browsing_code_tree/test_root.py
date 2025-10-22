import unittest
from taew.ports.for_browsing_code_tree import (
    Root as RootProtocol,
    Module as ModuleProtocol,
    Package as PackageProtocol,
)


class TestRoot(unittest.TestCase):
    def _get_module(self, description: str = "module desc") -> ModuleProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.module import Module

        return Module(description=description, items={})

    def _get_root(self) -> RootProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.root import Root
        from taew.adapters.python.ram.for_browsing_code_tree.package import Package

        mod: ModuleProtocol = self._get_module()
        pkg: PackageProtocol = Package(
            description="package desc", items={}, version="1.0.0"
        )

        # Root is a MappingProxyType alias, so we pass a dict
        return Root({"m": mod, "p": pkg})

    def test_items_and_getitem(self) -> None:
        root = self._get_root()
        items = dict(root.items())
        self.assertIn("m", items)
        self.assertIn("p", items)
        self.assertIs(root["m"], items["m"])
        self.assertIs(root["p"], items["p"])

    def test_immutable(self) -> None:
        root = self._get_root()
        with self.assertRaises(TypeError):
            root["m"] = None  # type: ignore
        with self.assertRaises(TypeError):
            del root["m"]  # type: ignore

    def test_change_root(self) -> None:
        import pickle
        import base64

        root = self._get_root()

        # Create simple dict data that can be pickled
        # In real usage, this would contain serializable representations of modules/packages
        new_root_data: dict[str, dict[str, str]] = {
            "new_module": {"description": "test", "items": "{}"}
        }
        pickled_data = pickle.dumps(new_root_data)
        new_root_string = base64.b64encode(pickled_data).decode("utf-8")
        new_root = root.change_root(new_root_string)

        # Verify new root has different contents
        self.assertNotEqual(list(root.items()), list(new_root.items()))
        self.assertTrue("new_module" in new_root)
        self.assertFalse("m" in new_root)
        self.assertFalse("p" in new_root)


if __name__ == "__main__":
    unittest.main()
