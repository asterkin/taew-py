import unittest
from taew.ports.for_serializing_objects import (
    Serialize as SerializeProtocol,
    Deserialize as DeserializeProtocol,
)


class StrDumps:
    """Simple dumps adapter that expects strings and passes them through."""

    def __call__(self, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Expected str, got {type(value).__name__}")
        return value


class StrLoads:
    """Simple loads adapter that passes strings through as objects."""

    def __call__(self, buf: str) -> object:
        return buf


class TestSerialize(unittest.TestCase):
    """Test cases for Serialize adapter."""

    def create_serialize_adapter(
        self, encoding: str = "utf-8", errors: str = "strict"
    ) -> SerializeProtocol:
        from taew.adapters.python.str.for_serializing_objects.serialize import Serialize

        return Serialize(_dumps=StrDumps(), _encoding=encoding, _errors=errors)

    def test_serialize_basic_string(self) -> None:
        """Test serialization of basic ASCII string."""
        serialize = self.create_serialize_adapter()
        result = serialize("hello world")
        expected = b"hello world"
        self.assertEqual(result, expected)

    def test_serialize_unicode_string(self) -> None:
        """Test serialization of Unicode string."""
        serialize = self.create_serialize_adapter()
        result = serialize("Hello 世界! 🌍")
        expected = "Hello 世界! 🌍".encode("utf-8")
        self.assertEqual(result, expected)

    def test_serialize_empty_string(self) -> None:
        """Test serialization of empty string."""
        serialize = self.create_serialize_adapter()
        result = serialize("")
        expected = b""
        self.assertEqual(result, expected)

    def test_serialize_with_different_encoding(self) -> None:
        """Test serialization with different encodings."""
        # UTF-16
        serialize = self.create_serialize_adapter(encoding="utf-16")
        result = serialize("hello")
        expected = "hello".encode("utf-16")
        self.assertEqual(result, expected)

        # ASCII
        serialize = self.create_serialize_adapter(encoding="ascii")
        result = serialize("hello")
        expected = b"hello"
        self.assertEqual(result, expected)

    def test_serialize_encoding_error_handling(self) -> None:
        """Test encoding error handling strategies."""
        # ASCII encoding with unicode characters - strict mode
        serialize = self.create_serialize_adapter(encoding="ascii", errors="strict")
        with self.assertRaises(UnicodeEncodeError):
            serialize("Hello 世界!")

        # ASCII encoding with unicode characters - ignore mode
        serialize = self.create_serialize_adapter(encoding="ascii", errors="ignore")
        result = serialize("Hello 世界!")
        expected = b"Hello !"
        self.assertEqual(result, expected)

        # ASCII encoding with unicode characters - replace mode
        serialize = self.create_serialize_adapter(encoding="ascii", errors="replace")
        result = serialize("Hello 世界!")
        expected = b"Hello ??!"
        self.assertEqual(result, expected)

    def test_serialize_non_string_raises_error(self) -> None:
        """Test that non-string input raises ValueError."""
        serialize = self.create_serialize_adapter()

        with self.assertRaises(ValueError) as context:
            serialize(123)
        self.assertIn("Expected str, got int", str(context.exception))

        with self.assertRaises(ValueError) as context:
            serialize(b"bytes")
        self.assertIn("Expected str, got bytes", str(context.exception))

        with self.assertRaises(ValueError) as context:
            serialize(None)
        self.assertIn("Expected str, got NoneType", str(context.exception))


class TestDeserialize(unittest.TestCase):
    """Test cases for Deserialize adapter."""

    def create_deserialize_adapter(
        self, encoding: str = "utf-8", errors: str = "strict"
    ) -> DeserializeProtocol:
        from taew.adapters.python.str.for_serializing_objects.deserialize import (
            Deserialize,
        )

        return Deserialize(_loads=StrLoads(), _encoding=encoding, _errors=errors)

    def test_deserialize_basic_bytes(self) -> None:
        """Test deserialization of basic ASCII bytes."""
        deserialize = self.create_deserialize_adapter()
        result = deserialize(b"hello world")
        expected = "hello world"
        self.assertEqual(result, expected)

    def test_deserialize_unicode_bytes(self) -> None:
        """Test deserialization of Unicode bytes."""
        deserialize = self.create_deserialize_adapter()
        utf8_bytes = "Hello 世界! 🌍".encode("utf-8")
        result = deserialize(utf8_bytes)
        expected = "Hello 世界! 🌍"
        self.assertEqual(result, expected)

    def test_deserialize_empty_bytes(self) -> None:
        """Test deserialization of empty bytes."""
        deserialize = self.create_deserialize_adapter()
        result = deserialize(b"")
        expected = ""
        self.assertEqual(result, expected)

    def test_deserialize_with_different_encoding(self) -> None:
        """Test deserialization with different encodings."""
        # UTF-16
        deserialize = self.create_deserialize_adapter(encoding="utf-16")
        utf16_bytes = "hello".encode("utf-16")
        result = deserialize(utf16_bytes)
        expected = "hello"
        self.assertEqual(result, expected)

        # ASCII
        deserialize = self.create_deserialize_adapter(encoding="ascii")
        result = deserialize(b"hello")
        expected = "hello"
        self.assertEqual(result, expected)

    def test_deserialize_decoding_error_handling(self) -> None:
        """Test decoding error handling strategies."""
        # Invalid UTF-8 bytes - strict mode
        deserialize = self.create_deserialize_adapter(encoding="utf-8", errors="strict")
        with self.assertRaises(UnicodeDecodeError):
            deserialize(b"\xff\xfe")

        # Invalid UTF-8 bytes - ignore mode
        deserialize = self.create_deserialize_adapter(encoding="utf-8", errors="ignore")
        result = deserialize(b"hello\xff\xfeworld")
        expected = "helloworld"
        self.assertEqual(result, expected)

        # Invalid UTF-8 bytes - replace mode
        deserialize = self.create_deserialize_adapter(
            encoding="utf-8", errors="replace"
        )
        result = deserialize(b"hello\xff\xfeworld")
        expected = "hello\ufffd\ufffdworld"
        self.assertEqual(result, expected)

    def test_deserialize_non_bytes_raises_error(self) -> None:
        """Test that non-bytes input raises ValueError."""
        deserialize = self.create_deserialize_adapter()

        with self.assertRaises(ValueError) as context:
            deserialize("string")  # type: ignore
        self.assertIn("Expected bytes, got str", str(context.exception))

        with self.assertRaises(ValueError) as context:
            deserialize(123)  # type: ignore
        self.assertIn("Expected bytes, got int", str(context.exception))

        with self.assertRaises(ValueError) as context:
            deserialize(None)  # type: ignore
        self.assertIn("Expected bytes, got NoneType", str(context.exception))


class TestRoundTrip(unittest.TestCase):
    """Test round-trip serialization and deserialization."""

    def test_round_trip_utf8(self) -> None:
        """Test round-trip with UTF-8 encoding."""
        from taew.adapters.python.str.for_serializing_objects.serialize import Serialize
        from taew.adapters.python.str.for_serializing_objects.deserialize import (
            Deserialize,
        )

        serialize = Serialize(_dumps=StrDumps(), _encoding="utf-8")
        deserialize = Deserialize(_loads=StrLoads(), _encoding="utf-8")

        original = "Hello 世界! 🌍 Testing UTF-8"
        serialized = serialize(original)
        restored = deserialize(serialized)

        self.assertEqual(restored, original)

    def test_round_trip_different_encodings(self) -> None:
        """Test round-trip with various encodings."""
        from taew.adapters.python.str.for_serializing_objects.serialize import Serialize
        from taew.adapters.python.str.for_serializing_objects.deserialize import (
            Deserialize,
        )

        test_strings = ["hello world", "café", "résumé"]
        encodings = ["utf-8", "utf-16", "latin-1"]

        for encoding in encodings:
            serialize = Serialize(_dumps=StrDumps(), _encoding=encoding)
            deserialize = Deserialize(_loads=StrLoads(), _encoding=encoding)

            for original in test_strings:
                if encoding == "latin-1" and any(ord(c) > 255 for c in original):
                    continue  # Skip strings that can't be encoded in latin-1

                with self.subTest(encoding=encoding, string=original):
                    serialized = serialize(original)
                    restored = deserialize(serialized)
                    self.assertEqual(restored, original)

    def test_round_trip_with_error_handling(self) -> None:
        """Test round-trip with error handling configurations."""
        from taew.adapters.python.str.for_serializing_objects.serialize import Serialize
        from taew.adapters.python.str.for_serializing_objects.deserialize import (
            Deserialize,
        )

        # Test with ignore errors - should work but may lose information
        serialize = Serialize(_dumps=StrDumps(), _encoding="ascii", _errors="ignore")
        deserialize = Deserialize(
            _loads=StrLoads(), _encoding="ascii", _errors="ignore"
        )

        original = "Hello world!"  # ASCII only
        serialized = serialize(original)
        restored = deserialize(serialized)

        self.assertEqual(restored, original)

    def test_defaults_identity_stringizers(self) -> None:
        """Serialize/Deserialize use identity dumps/loads by default for str."""
        from taew.adapters.python.str.for_serializing_objects.serialize import Serialize
        from taew.adapters.python.str.for_serializing_objects.deserialize import (
            Deserialize,
        )

        serialize = Serialize()  # default identity dumps
        deserialize = Deserialize()  # default identity loads

        original = "Sample π 字"
        data = serialize(original)
        restored = deserialize(data)
        self.assertEqual(restored, original)


if __name__ == "__main__":
    unittest.main()
