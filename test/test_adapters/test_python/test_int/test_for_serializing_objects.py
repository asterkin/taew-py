import unittest

from taew.utils.int import (
    signed_int_bytes_needed,
    unsigned_int_bytes_needed,
)


class TestIntSerializing(unittest.TestCase):
    def test_serialize_deserialize_signed_big(self) -> None:
        from taew.adapters.python.int.for_serializing_objects.serialize import Serialize
        from taew.adapters.python.int.for_serializing_objects.deserialize import (
            Deserialize,
        )

        serialize = Serialize(_byte_order="big", _signed=True)
        deserialize = Deserialize(_byte_order="big", _signed=True)

        for value in [0, 1, 127, 128, -1, -128, -129, 2**31 - 1, -(2**31)]:
            with self.subTest(value=value):
                data = serialize(value)
                self.assertEqual(len(data), signed_int_bytes_needed(value))
                out = deserialize(data)
                self.assertEqual(out, value)

    def test_serialize_deserialize_unsigned_little(self) -> None:
        from taew.adapters.python.int.for_serializing_objects.serialize import Serialize
        from taew.adapters.python.int.for_serializing_objects.deserialize import (
            Deserialize,
        )

        serialize = Serialize(_byte_order="little", _signed=False)
        deserialize = Deserialize(_byte_order="little", _signed=False)

        for value in [0, 1, 255, 256, 2**16 - 1, 2**16, 2**64 - 1]:
            with self.subTest(value=value):
                data = serialize(value)
                self.assertEqual(len(data), unsigned_int_bytes_needed(value))
                out = deserialize(data)
                self.assertEqual(out, value)

    def test_serialize_unsigned_negative_raises(self) -> None:
        from taew.adapters.python.int.for_serializing_objects.serialize import Serialize

        serialize = Serialize(_byte_order="big", _signed=False)
        with self.assertRaises(OverflowError):
            _ = serialize(-1)

    def test_deserialize_empty_raises(self) -> None:
        from taew.adapters.python.int.for_serializing_objects.deserialize import (
            Deserialize,
        )

        deserialize = Deserialize(_byte_order="big", _signed=True)
        with self.assertRaises(ValueError):
            _ = deserialize(b"")


if __name__ == "__main__":
    unittest.main()
