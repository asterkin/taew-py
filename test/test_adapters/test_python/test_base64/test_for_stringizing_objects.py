import os
import unittest

from taew.ports.for_stringizing_objects import (
    Dumps as DumpsProtocol,
    Loads as LoadsProtocol,
)


class TestBase64Stringizing(unittest.TestCase):
    def _get_dumps(self, **kwargs: object) -> DumpsProtocol:
        from taew.adapters.python.base64.for_stringizing_objects.dumps import Dumps
        from typing import cast, Any

        return cast(DumpsProtocol, Dumps(**cast(Any, kwargs)))

    def _get_loads(self, **kwargs: object) -> LoadsProtocol:
        from taew.adapters.python.base64.for_stringizing_objects.loads import Loads
        from typing import cast, Any

        return cast(LoadsProtocol, Loads(**cast(Any, kwargs)))

    def test_roundtrip_basic(self) -> None:
        dumps = self._get_dumps()
        loads = self._get_loads()

        cases = [b"", b"hello", os.urandom(64)]
        for data in cases:
            with self.subTest(length=len(data)):
                s = dumps(data)
                self.assertIsInstance(s, str)
                out = loads(s)
                self.assertEqual(out, data)

    def test_urlsafe_variant(self) -> None:
        dumps = self._get_dumps(_urlsafe=True)
        loads = self._get_loads(_urlsafe=True)

        data = b"\xff\xfe\xfd\xfc" + os.urandom(12)
        s = dumps(data)
        self.assertNotIn("+", s)
        self.assertNotIn("/", s)
        out = loads(s)
        self.assertEqual(out, data)

    def test_altchars(self) -> None:
        dumps = self._get_dumps(_altchars=b"._")
        loads = self._get_loads(_altchars=b"._")

        # Use data that will definitely contain '+' or '/' in base64, which get replaced by "._"
        data = b"\xff\xfe" * 16  # This will produce '+' and '/' in standard base64
        s = dumps(data)
        # The altchars should replace '+' with '.' and '/' with '_'
        self.assertTrue("." in s or "_" in s)
        self.assertNotIn("+", s)
        self.assertNotIn("/", s)
        out = loads(s)
        self.assertEqual(out, data)

    def test_invalid_input_raises(self) -> None:
        loads = self._get_loads(_validate=True)
        with self.assertRaises(ValueError):
            loads("not base64!!!")


if __name__ == "__main__":
    unittest.main()
