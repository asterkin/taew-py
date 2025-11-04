"""Tests for testing utilities."""

import unittest

from taew.utils.test import normalize_timing_data


class TestNormalizeTimingData(unittest.TestCase):
    """Tests for normalize_timing_data function."""

    def test_normalize_datetime_objects(self) -> None:
        """Should replace datetime.datetime() objects with <DATETIME>."""
        text = "Created at datetime.datetime(2025, 1, 15, 10, 30, 0)"
        result = normalize_timing_data(text)
        self.assertEqual(result, "Created at <DATETIME>")

    def test_normalize_datetime_with_microseconds(self) -> None:
        """Should handle datetime objects with microseconds."""
        text = "Timestamp: datetime.datetime(2025, 1, 15, 10, 30, 0, 123456)"
        result = normalize_timing_data(text)
        self.assertEqual(result, "Timestamp: <DATETIME>")

    def test_normalize_datetime_with_timezone(self) -> None:
        """Should handle datetime objects with timezone info."""
        text = "Time: datetime.datetime(2025, 1, 15, 10, 30, 0, tzinfo=datetime.timezone.utc)"
        result = normalize_timing_data(text)
        self.assertEqual(result, "Time: <DATETIME>")

    def test_normalize_timestamp_parameter(self) -> None:
        """Should replace timestamp= parameters specifically."""
        text = "Event(id=123, timestamp=datetime.datetime(2025, 1, 15, 10, 30, 0))"
        result = normalize_timing_data(text)
        self.assertEqual(result, "Event(id=123, timestamp=<TIMESTAMP>)")

    def test_normalize_uuid(self) -> None:
        """Should replace UUIDs with <UUID>."""
        text = "ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        result = normalize_timing_data(text)
        self.assertEqual(result, "ID: <UUID>")

    def test_normalize_multiple_uuids(self) -> None:
        """Should replace multiple UUIDs in the same text."""
        text = (
            "Source: 12345678-1234-1234-1234-123456789012, "
            "Target: abcdefab-cdef-abcd-efab-cdefabcdefab"
        )
        result = normalize_timing_data(text)
        self.assertEqual(result, "Source: <UUID>, Target: <UUID>")

    def test_normalize_mixed_data(self) -> None:
        """Should normalize mixed datetime and UUID data."""
        text = (
            "Record(id=a1b2c3d4-e5f6-7890-abcd-ef1234567890, "
            "created=datetime.datetime(2025, 1, 15, 10, 30, 0), "
            "timestamp=datetime.datetime(2025, 1, 15, 10, 30, 1))"
        )
        result = normalize_timing_data(text)
        expected = "Record(id=<UUID>, created=<DATETIME>, timestamp=<TIMESTAMP>)"
        self.assertEqual(result, expected)

    def test_preserve_non_timing_data(self) -> None:
        """Should preserve text that doesn't match timing patterns."""
        text = "User: John Doe, Status: active, Count: 42"
        result = normalize_timing_data(text)
        self.assertEqual(result, text)

    def test_empty_string(self) -> None:
        """Should handle empty string."""
        result = normalize_timing_data("")
        self.assertEqual(result, "")

    def test_multiline_text(self) -> None:
        """Should handle multiline text."""
        text = """Line 1: datetime.datetime(2025, 1, 15, 10, 30, 0)
Line 2: ID a1b2c3d4-e5f6-7890-abcd-ef1234567890
Line 3: Normal text"""
        result = normalize_timing_data(text)
        expected = """Line 1: <DATETIME>
Line 2: ID <UUID>
Line 3: Normal text"""
        self.assertEqual(result, expected)

    def test_case_sensitive_uuid(self) -> None:
        """Should only match lowercase UUIDs."""
        # UUIDs with uppercase should not be matched (per the regex pattern)
        text_upper = "ID: A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
        result_upper = normalize_timing_data(text_upper)
        self.assertEqual(result_upper, text_upper)  # Should not be normalized

        # Lowercase UUIDs should be matched
        text_lower = "ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        result_lower = normalize_timing_data(text_lower)
        self.assertEqual(result_lower, "ID: <UUID>")

    def test_partial_datetime_not_matched(self) -> None:
        """Should not match partial datetime-like strings."""
        text = "Module: datetime.datetime"
        result = normalize_timing_data(text)
        self.assertEqual(result, text)

    def test_datetime_in_different_contexts(self) -> None:
        """Should handle datetime objects in various contexts."""
        text = (
            "List: [datetime.datetime(2025, 1, 15), datetime.datetime(2025, 1, 16)], "
            "Dict: {'start': datetime.datetime(2025, 1, 1), 'end': datetime.datetime(2025, 12, 31)}"
        )
        result = normalize_timing_data(text)
        expected = (
            "List: [<DATETIME>, <DATETIME>], "
            "Dict: {'start': <DATETIME>, 'end': <DATETIME>}"
        )
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
