from __future__ import annotations

import shutil
import unittest
from pathlib import Path
from typing import TypeAlias
from dataclasses import dataclass

from taew.ports.for_storing_data import (
    DataSequence as DataSequenceProtocol,
    MutableDataSequence as MutableDataSequenceProtocol,
)
from taew.ports.for_serializing_objects import Serialize as SerializeProtocol
from taew.ports.for_serializing_objects import Deserialize as DeserializeProtocol


@dataclass(frozen=True)
class Item:
    id: int
    name: str


DataSeq: TypeAlias = DataSequenceProtocol[Item]
MutableDataSeq: TypeAlias = MutableDataSequenceProtocol[Item]


class TestDataSequence(unittest.TestCase):
    def setUp(self) -> None:
        folder = Path("/tmp/seq-sample")
        if folder.exists():
            shutil.rmtree(folder)

    def _get_mutable(self) -> MutableDataSeq:
        from taew.adapters.python.dir.for_storing_data.mutable_data_sequence import (
            MutableDataSequence,
        )
        from taew.adapters.python.pickle.for_serializing_objects.serialize import (
            Serialize,
        )
        from taew.adapters.python.pickle.for_serializing_objects.deserialize import (
            Deserialize,
        )

        return MutableDataSequence(
            _folder=Path("/tmp/seq-sample"),
            _extension="pkl",
            _deserialize=(Deserialize(), DeserializeProtocol),
            _serialize=(Serialize(), SerializeProtocol),
        )

    def _get_readonly_with_data(self) -> DataSeq:
        m = self._get_mutable()
        m.insert(0, Item(1, "one"))
        m.append(Item(2, "two"))
        m.append(Item(3, "three"))
        return m

    def test_len_iter_get(self) -> None:
        seq = self._get_readonly_with_data()
        self.assertEqual(len(seq), 3)
        self.assertEqual([x.name for x in seq], ["one", "two", "three"])
        self.assertEqual(seq[0].name, "one")
        self.assertEqual(seq[-1].name, "three")

    def test_slice_view_and_nested_slice(self) -> None:
        seq = self._get_readonly_with_data()
        sub = seq[1:]  # two, three
        self.assertEqual(len(sub), 2)
        self.assertEqual([x.name for x in sub], ["two", "three"])

        sub2 = sub[:1]  # two
        self.assertEqual(len(sub2), 1)
        self.assertEqual([x.name for x in sub2], ["two"])

    def test_setitem_insert_delete(self) -> None:
        m = self._get_mutable()
        m.append(Item(10, "ten"))
        m.append(Item(20, "twenty"))
        m.append(Item(30, "thirty"))

        # overwrite middle
        m[1] = Item(25, "twenty-five")
        self.assertEqual([x.id for x in m], [10, 25, 30])

        # insert at head
        m.insert(0, Item(5, "five"))
        self.assertEqual([x.id for x in m], [5, 10, 25, 30])

        # delete last
        del m[-1]
        self.assertEqual([x.id for x in m], [5, 10, 25])

    def test_delete_head_and_middle(self) -> None:
        m = self._get_mutable()
        m.append(Item(1, "one"))
        m.append(Item(2, "two"))
        m.append(Item(3, "three"))
        m.append(Item(4, "four"))

        # delete head -> shifts left
        del m[0]
        self.assertEqual([x.id for x in m], [2, 3, 4])

        # delete middle -> shifts left
        del m[1]
        self.assertEqual([x.id for x in m], [2, 4])

    def test_insert_with_negative_index(self) -> None:
        m = self._get_mutable()
        m.append(Item(100, "a"))
        m.append(Item(200, "b"))
        m.append(Item(300, "c"))

        # insert before last using -1
        m.insert(-1, Item(250, "x"))
        self.assertEqual([x.id for x in m], [100, 200, 250, 300])

    def test_out_of_range_and_step_mutation(self) -> None:
        m = self._get_mutable()
        m.append(Item(1, "one"))
        with self.assertRaises(IndexError):
            _ = m[1]

        # create a stepped view and ensure mutation is blocked
        v = m[::2]
        with self.assertRaises(TypeError):
            v[0] = Item(1, "ONE")
        with self.assertRaises(TypeError):
            del v[0]

    def test_corrupted_files_handling(self) -> None:
        # Arrange
        m = self._get_mutable()
        m.append(Item(1, "one"))
        m.append(Item(2, "two"))
        m.append(Item(3, "three"))

        # Simulate a missing last file to hit exists-guards without collisions
        folder = Path("/tmp/seq-sample")
        (folder / "2.pkl").unlink()

        # Inserting at index 1 should shift while skipping missing src on first pass
        m.insert(1, Item(4, "four"))
        self.assertEqual(m[0].id, 1)
        self.assertEqual(m[1].id, 4)
        self.assertEqual(m[2].id, 2)


if __name__ == "__main__":
    unittest.main()
