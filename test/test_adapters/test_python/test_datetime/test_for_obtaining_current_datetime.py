# test/test_adapters/test_python/test_datetime/test_for_obtaining_current_datetime.py
import unittest
from datetime import datetime
from taew.ports.for_obtaining_current_datetime import Now as NowProtocol


class TestForObtainingCurrentDateTime(unittest.TestCase):
    def create_now_adapter(self) -> NowProtocol:
        from taew.adapters.python.datetime.for_obtaining_current_datetime import now

        return now

    def test_returns_current_datetime(self) -> None:
        now_adapter = self.create_now_adapter()
        before = datetime.now()
        result = now_adapter()
        after = datetime.now()

        self.assertIsInstance(result, datetime)
        self.assertGreaterEqual(result, before)
        self.assertLessEqual(result, after)


if __name__ == "__main__":
    unittest.main()
