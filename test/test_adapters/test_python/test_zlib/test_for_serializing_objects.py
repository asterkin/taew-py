"""Unit tests for zlib-based serialization adapter."""

import unittest


class TestZlibSerialization(unittest.TestCase):
    """Test cases for zlib-based serialization with identity defaults."""

    def test_round_trip_bytes_with_compression(self) -> None:
        """Test serialization and deserialization round trip with bytes using identity defaults."""
        from taew.adapters.python.zlib.for_serializing_objects.serialize import (
            Serialize,
        )
        from taew.adapters.python.zlib.for_serializing_objects.deserialize import (
            Deserialize,
        )

        test_cases = (
            b"Hello, World!",
            b"A" * 1000,  # Repetitive data compresses well
            b"",
            b"\x00\x01\x02\x03\x04",
        )

        serialize = Serialize(_level=6)
        deserialize = Deserialize()

        for data in test_cases:
            with self.subTest(data=data[:20]):
                # Serialize (compress) bytes
                compressed = serialize(data)
                self.assertIsInstance(compressed, bytes)

                # Verify compression occurred for non-empty data
                if len(data) > 0:
                    self.assertGreater(len(compressed), 0)

                # Deserialize (decompress) back to bytes
                decompressed = deserialize(compressed)
                self.assertEqual(data, decompressed)

    def test_compression_reduces_size_for_repetitive_data(self) -> None:
        """Test that compression actually reduces size for repetitive data."""
        from taew.adapters.python.zlib.for_serializing_objects.serialize import (
            Serialize,
        )

        # Highly repetitive data should compress well
        data = b"A" * 10000

        serialize = Serialize(_level=6)
        compressed = serialize(data)

        # Compressed size should be significantly smaller
        self.assertLess(len(compressed), len(data))

    def test_identity_serialize_validates_bytes_type(self) -> None:
        """Test that identity serializer validates input is bytes."""
        from taew.adapters.python.zlib.for_serializing_objects.serialize import (
            Serialize,
        )

        serialize = Serialize(_level=6)

        # Non-bytes input should raise ValueError
        with self.assertRaises(ValueError) as context:
            serialize("not bytes")  # type: ignore

        self.assertIn("Expected bytes, got str", str(context.exception))


if __name__ == "__main__":
    unittest.main()
