import unittest
from io import BytesIO


class MockLengthWriter:
    """Mock length writer that writes length as 4-byte big-endian int."""

    def __call__(self, obj: object, stream: BytesIO) -> None:
        if not isinstance(obj, int):
            raise TypeError(f"Expected int, got {type(obj)}")
        stream.write(obj.to_bytes(4, "big", signed=False))


class MockLengthReader:
    """Mock length reader that reads length as 4-byte big-endian int."""

    def __call__(self, stream: BytesIO) -> object:
        data = stream.read(4)
        if len(data) < 4:
            raise ValueError("Insufficient data for length prefix")
        return int.from_bytes(data, "big", signed=False)


class TestBytesStreaming(unittest.TestCase):
    def test_read_write_bytes(self) -> None:
        from taew.adapters.python.bytes.for_streaming_objects.read import Read
        from taew.adapters.python.bytes.for_streaming_objects.write import Write

        write_adapter = Write(_write_length=MockLengthWriter())
        read_adapter = Read(_read_length=MockLengthReader())

        # Test data
        test_data = b"Hello, streaming bytes!"

        # Write to stream
        stream = BytesIO()
        write_adapter(test_data, stream)

        # Read from stream
        stream.seek(0)
        result = read_adapter(stream)

        self.assertEqual(result, test_data)

    def test_read_write_bytearray(self) -> None:
        from taew.adapters.python.bytes.for_streaming_objects.read import Read
        from taew.adapters.python.bytes.for_streaming_objects.write import Write

        write_adapter = Write(_write_length=MockLengthWriter())
        read_adapter = Read(_read_length=MockLengthReader())

        # Test with bytearray
        test_data = bytearray(b"Test bytearray data")

        stream = BytesIO()
        write_adapter(test_data, stream)

        stream.seek(0)
        result = read_adapter(stream)

        self.assertEqual(result, bytes(test_data))

    def test_read_write_memoryview(self) -> None:
        from taew.adapters.python.bytes.for_streaming_objects.read import Read
        from taew.adapters.python.bytes.for_streaming_objects.write import Write

        write_adapter = Write(_write_length=MockLengthWriter())
        read_adapter = Read(_read_length=MockLengthReader())

        # Test with memoryview
        original_data = b"Memory view test data"
        test_data = memoryview(original_data)

        stream = BytesIO()
        write_adapter(test_data, stream)

        stream.seek(0)
        result = read_adapter(stream)

        self.assertEqual(result, original_data)

    def test_write_invalid_type_raises(self) -> None:
        from taew.adapters.python.bytes.for_streaming_objects.write import Write

        write_adapter = Write(_write_length=MockLengthWriter())

        stream = BytesIO()
        with self.assertRaises(TypeError):
            write_adapter("invalid string", stream)

    def test_read_insufficient_data_raises(self) -> None:
        from taew.adapters.python.bytes.for_streaming_objects.read import Read

        read_adapter = Read(_read_length=MockLengthReader())

        # Write length prefix indicating 10 bytes but only provide 5
        stream = BytesIO()
        stream.write(b"\x00\x00\x00\x0a")  # length = 10
        stream.write(b"12345")  # only 5 bytes
        stream.seek(0)

        with self.assertRaises(ValueError):
            read_adapter(stream)

    def test_read_negative_length_raises(self) -> None:
        from taew.adapters.python.bytes.for_streaming_objects.read import Read

        # Mock length reader that returns negative value
        class NegativeLengthReader:
            def __call__(self, stream: BytesIO) -> object:
                return -1

        read_adapter = Read(_read_length=NegativeLengthReader())

        stream = BytesIO()
        with self.assertRaises(ValueError):
            read_adapter(stream)


if __name__ == "__main__":
    unittest.main()
