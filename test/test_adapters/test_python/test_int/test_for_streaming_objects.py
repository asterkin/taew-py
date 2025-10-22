import io
import unittest


class TestIntStreaming(unittest.TestCase):
    def test_write_read_unsigned_big_endian(self) -> None:
        from taew.adapters.python.int.for_streaming_objects.write import Write
        from taew.adapters.python.int.for_streaming_objects.read import Read

        write = Write(_width=4, _byte_order="big", _signed=False)
        read = Read(_width=4, _byte_order="big", _signed=False)

        buf = io.BytesIO()
        write(0x01020304, buf)
        buf.seek(0)
        val = read(buf)
        self.assertEqual(val, 0x01020304)

    def test_write_read_signed_little_endian(self) -> None:
        from taew.adapters.python.int.for_streaming_objects.write import Write
        from taew.adapters.python.int.for_streaming_objects.read import Read

        write = Write(_width=2, _byte_order="little", _signed=True)
        read = Read(_width=2, _byte_order="little", _signed=True)

        buf = io.BytesIO()
        write(-2, buf)
        buf.seek(0)
        val = read(buf)
        self.assertEqual(val, -2)

    def test_insufficient_data_raises(self) -> None:
        from taew.adapters.python.int.for_streaming_objects.read import Read

        read = Read(_width=4, _byte_order="big", _signed=False)
        buf = io.BytesIO(b"\x00\x01")
        with self.assertRaises(ValueError):
            _ = read(buf)

    def test_out_of_range_raises_overflow(self) -> None:
        from taew.adapters.python.int.for_streaming_objects.write import Write

        write = Write(_width=1, _byte_order="big", _signed=False)
        buf = io.BytesIO()
        with self.assertRaises(OverflowError):
            write(256, buf)  # out of range for 1 byte unsigned


if __name__ == "__main__":
    unittest.main()
