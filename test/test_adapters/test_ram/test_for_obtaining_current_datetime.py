# test/test_adapters/test_ram/test_for_obtaining_current_datetime.py
import unittest
from datetime import datetime
from taew.ports.for_obtaining_current_datetime import Now as NowProtocol


class TestForObtainingCurrentDateTime(unittest.TestCase):
    def create_now_adapter(self) -> NowProtocol:
        from taew.adapters.python.ram.for_obtaining_current_datetime import Now

        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        return Now(_now=test_datetime)

    def test_returns_set_datetime(self) -> None:
        now_adapter = self.create_now_adapter()
        result = now_adapter()

        expected = datetime(2024, 1, 1, 12, 0, 0)
        self.assertEqual(result, expected)

    def test_returns_same_datetime_on_multiple_calls(self) -> None:
        now_adapter = self.create_now_adapter()

        result1 = now_adapter()
        result2 = now_adapter()

        self.assertEqual(result1, result2)


if __name__ == "__main__":
    unittest.main()
