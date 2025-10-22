import shutil
import unittest
from pathlib import Path
from typing import TypeAlias
from dataclasses import dataclass

from taew.ports.for_storing_data import (
    DataRepository as DataRepositoryProtocol,
    MutableDataRepository as MutableDataRepositoryProtocol,
)
from taew.ports.for_serializing_objects import Serialize as SerializeProtocol
from taew.ports.for_serializing_objects import Deserialize as DeserializeProtocol


@dataclass(frozen=True)
class Rec:
    id: str
    val: int


Repo: TypeAlias = DataRepositoryProtocol[str, Rec]
MutRepo: TypeAlias = MutableDataRepositoryProtocol[str, Rec]


class TestMutableDataRepository(unittest.TestCase):
    def setUp(self) -> None:
        folder = Path("/tmp/repo-sample")
        if folder.exists():
            shutil.rmtree(folder)

    def _get_mutable(self) -> MutRepo:
        from taew.adapters.python.dir.for_storing_data.mutable_data_repository import (
            MutableDataRepository,
        )
        from taew.adapters.python.pickle.for_serializing_objects.serialize import (
            Serialize,
        )
        from taew.adapters.python.pickle.for_serializing_objects.deserialize import (
            Deserialize,
        )

        return MutableDataRepository(
            _folder=Path("/tmp/repo-sample"),
            _extension="pkl",
            _key_type=str,
            _deserialize=(Deserialize(), DeserializeProtocol),
            _serialize=(Serialize(), SerializeProtocol),
        )

    def _get_readonly(self) -> Repo:
        return self._get_mutable()

    def test_delete_missing_raises(self) -> None:
        m = self._get_mutable()
        with self.assertRaises(KeyError):
            del m["nope"]

    def test_set_and_get_roundtrip(self) -> None:
        m = self._get_mutable()
        r = Rec("a", 1)
        m["a"] = r
        out = self._get_readonly()["a"]
        self.assertEqual(out, r)


if __name__ == "__main__":
    unittest.main()
