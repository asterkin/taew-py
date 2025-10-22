import unittest
from typing import Any

from taew.ports.for_stringizing_objects import (
    Dumps as DumpsProtocol,
    Loads as LoadsProtocol,
)


class TestForStringizingObjects(unittest.TestCase):
    def _get_dumps(self, **kwargs: Any) -> DumpsProtocol:
        from taew.adapters.python.json.for_stringizing_objects.dumps import Dumps

        return Dumps(**kwargs)

    def _get_loads(self, **kwargs: Any) -> LoadsProtocol:
        from taew.adapters.python.json.for_stringizing_objects.loads import Loads

        return Loads(**kwargs)

    def test_roundtrip_simple(self) -> None:
        dumps = self._get_dumps()
        loads = self._get_loads()

        data = {"a": 1, "b": True, "c": None, "d": [1, 2, 3]}
        s = dumps(data)
        r = loads(s)
        self.assertEqual(r, data)

    def test_format_options(self) -> None:
        # sort_keys
        dumps_sorted = self._get_dumps(_sort_keys=True)
        self.assertEqual(dumps_sorted({"b": 2, "a": 1}), '{"a": 1, "b": 2}')

        # indent
        dumps_indented = self._get_dumps(_indent=2)
        out = dumps_indented({"k": "v"})
        self.assertIn('\n  "k": "v"\n', out)

        # separators
        dumps_compact = self._get_dumps(_separators=(",", ":"))
        self.assertEqual(dumps_compact({"a": 1, "b": 2}), '{"a":1,"b":2}')

    def test_parsing_hooks(self) -> None:
        def parse_float_as_str(s: str) -> str:
            return f"float:{s}"

        loads_custom = self._get_loads(_parse_float=parse_float_as_str)
        res = loads_custom('{"x": 3.14}')
        self.assertEqual(res, {"x": "float:3.14"})

    def test_unicode(self) -> None:
        dumps_ascii = self._get_dumps(_ensure_ascii=True)
        dumps_unicode = self._get_dumps(_ensure_ascii=False)
        loads = self._get_loads()

        data = {"message": "Hello 世界", "emoji": "😀"}
        s_ascii = dumps_ascii(data)
        self.assertNotIn("世界", s_ascii)
        s_uni = dumps_unicode(data)
        self.assertIn("世界", s_uni)
        self.assertEqual(loads(s_uni), data)

    def test_immutability_and_equality(self) -> None:
        d1 = self._get_dumps(_sort_keys=True)
        d2 = self._get_dumps(_sort_keys=True)
        self.assertNotEqual(d1, d2)
        with self.assertRaises(AttributeError):
            d1._sort_keys = False  # type: ignore


if __name__ == "__main__":
    unittest.main()
