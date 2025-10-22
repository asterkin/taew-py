import shutil
import unittest
from pathlib import Path
from typing import Any

from taew.adapters.python.dir.for_storing_data._common import make_path
from taew.adapters.python.dir.for_storing_data._common import read_value
from taew.adapters.python.dir.for_storing_data._common import validate_key
from taew.adapters.python.dir.for_storing_data._common import validate_extension
from taew.adapters.python.dir.for_storing_data._common import write_value


class TestCommonHelpers(unittest.TestCase):
    def setUp(self) -> None:
        folder = Path("/tmp/common-sample")
        if folder.exists():
            shutil.rmtree(folder)

    def test_validate_extension_accepts_and_rejects(self) -> None:
        for ext in ("pkl", "CSV", "csv1", "_abc", "7z"):
            validate_extension(ext)

        for bad in (".pkl", "pkl.", "p-kl", "csv+", "", "a.b"):
            with self.subTest(ext=bad):
                with self.assertRaises(ValueError):
                    validate_extension(bad)

    def test_validate_key_accepts_and_rejects(self) -> None:
        for key in ("abc", "ABC", "a_b-c", "A1_2-3", "123"):
            validate_key(key)

        for bad in ("a/b", r"a\b", "..", ".", "a.b", "with space", ""):
            with self.subTest(key=bad):
                with self.assertRaises(ValueError):
                    validate_key(bad)

    def test_make_path_builds_expected_path(self) -> None:
        folder = Path("/tmp/common-sample")
        p = make_path(folder, "name", "pkl")
        self.assertEqual(p, folder / "name.pkl")

    def test_write_and_read_value_roundtrip(self) -> None:
        from taew.adapters.python.pickle.for_serializing_objects.serialize import (
            Serialize,
        )
        from taew.adapters.python.pickle.for_serializing_objects.deserialize import (
            Deserialize,
        )

        folder = Path("/tmp/common-sample/nested")
        path = folder / "obj.pkl"

        obj: Any = {"x": 1, "y": (2, 3)}
        write_value(path, obj, "b", Serialize())
        out = read_value(path, "b", Deserialize())
        self.assertEqual(out, obj)


if __name__ == "__main__":
    unittest.main()
