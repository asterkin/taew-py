import unittest

from taew.utils.int import (
    signed_int_bytes_needed,
    unsigned_int_bytes_needed,
)


class TestIntUtils(unittest.TestCase):
    def test_signed_minimal_width(self) -> None:
        cases = [
            (0, 1),
            (1, 1),
            (127, 1),
            (128, 2),
            (-1, 1),
            (-128, 1),
            (-129, 2),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(signed_int_bytes_needed(value), expected)

    def test_unsigned_minimal_width(self) -> None:
        cases = [
            (0, 1),
            (1, 1),
            (255, 1),
            (256, 2),
            ((1 << 16) - 1, 2),
            (1 << 16, 3),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(unsigned_int_bytes_needed(value), expected)

    def test_large_values(self) -> None:
        self.assertEqual(unsigned_int_bytes_needed((1 << 64) - 1), 8)
        self.assertEqual(unsigned_int_bytes_needed(1 << 64), 9)


if __name__ == "__main__":
    unittest.main()
