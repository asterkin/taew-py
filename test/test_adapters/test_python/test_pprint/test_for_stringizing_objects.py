import unittest
from typing import Any
from dataclasses import dataclass

from taew.ports.for_stringizing_objects import Dumps as DumpsProtocol


class TestPprintDumpsAdapter(unittest.TestCase):
    """Comprehensive test suite for pprint-based Dumps adapter."""

    def _get_dumps(self, **kwargs: Any) -> DumpsProtocol:
        from taew.adapters.python.pprint.for_stringizing_objects.dumps import Dumps

        return Dumps(**kwargs)

    def test_protocol_compliance(self) -> None:
        dumps = self._get_dumps()
        self.assertTrue(callable(dumps))
        result = dumps({"a": 1})
        self.assertIsInstance(result, str)

    def test_basic_data_types(self) -> None:
        dumps = self._get_dumps()

        test_cases = [
            (42, "42"),
            ("hello", "'hello'"),
            ([1, 2, 3], "[1, 2, 3]"),
            ({"a": 1}, "{'a': 1}"),
            ((1, 2), "(1, 2)"),
            ({1, 2, 3}, "{1, 2, 3}"),
            (True, "True"),
            (None, "None"),
        ]

        for value, expected_content in test_cases:
            with self.subTest(value=value):
                result = dumps(value)
                self.assertIsInstance(result, str)
                if expected_content != "{1, 2, 3}":  # Sets are unordered
                    self.assertEqual(result.strip(), expected_content)
                else:
                    self.assertIn("1", result)
                    self.assertIn("2", result)
                    self.assertIn("3", result)

    def test_nested_structures(self) -> None:
        dumps = self._get_dumps()

        nested_dict = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False},
            ],
            "meta": {"total": 2, "page": 1},
        }

        result = dumps(nested_dict)
        self.assertIsInstance(result, str)
        self.assertIn("'users'", result)
        self.assertIn("'Alice'", result)
        self.assertIn("'Bob'", result)
        self.assertIn("'meta'", result)
        self.assertIn("'total': 2", result)

    def test_custom_objects(self) -> None:
        @dataclass
        class Person:
            name: str
            age: int

        dumps = self._get_dumps()
        person = Person("Charlie", 30)
        result = dumps(person)

        self.assertIsInstance(result, str)
        self.assertIn("Person", result)
        self.assertIn("Charlie", result)
        self.assertIn("30", result)

    def test_width_and_compact(self) -> None:
        narrow_dumps = self._get_dumps(_width=40, _compact=False)
        wide_dumps = self._get_dumps(_width=120, _compact=True)

        nested = {"items": [{"i": i, "vals": list(range(10))} for i in range(5)]}

        narrow = narrow_dumps(nested)
        wide = wide_dumps(nested)
        self.assertIsInstance(narrow, str)
        self.assertIsInstance(wide, str)

    def test_dataclass_properties(self) -> None:
        d1 = self._get_dumps(_width=80, _compact=True)
        d2 = self._get_dumps(_width=80, _compact=True)
        d3 = self._get_dumps(_width=60, _compact=True)

        self.assertNotEqual(d1, d2)
        self.assertNotEqual(d1, d3)
        with self.assertRaises(AttributeError):
            d1._width = 100  # type: ignore

    def test_printer_initialization(self) -> None:
        d = self._get_dumps(_width=60, _compact=False)
        self.assertEqual(d._printer._width, 60)  # type: ignore
        self.assertEqual(d._printer._compact, False)  # type: ignore


if __name__ == "__main__":
    unittest.main()
