import unittest
from typing import Any, cast
from decimal import Decimal

from taew.ports.for_stringizing_objects import (
    Dumps as DumpsProtocol,
    Loads as LoadsProtocol,
)


class TestForStringizingObjects(unittest.TestCase):
    """Test decimal stringizing adapters."""

    def _get_dumps_adapter(self) -> DumpsProtocol:
        from taew.adapters.python.decimal.for_stringizing_objects.dumps import (
            Dumps,
        )

        return Dumps()

    def _get_loads_adapter(self) -> LoadsProtocol:
        from taew.adapters.python.decimal.for_stringizing_objects.loads import (
            Loads,
        )

        return Loads()

    def test_decimal_to_str_round_trip(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        test_cases = [
            Decimal("0"),
            Decimal("123"),
            Decimal("-456.789"),
            Decimal("3.1415926535897932384626433832795028841971"),
            Decimal("1E10"),
            Decimal("1.23E-4"),
            Decimal("+123.456"),
            Decimal("000123.456000"),
        ]

        for decimal_val in test_cases:
            with self.subTest(decimal=decimal_val):
                str_repr = dumps(decimal_val)
                restored = loads(str_repr)
                self.assertEqual(decimal_val, restored)
                self.assertIsInstance(restored, Decimal)

    def test_loads_valid_strings(self) -> None:
        loads = self._get_loads_adapter()

        test_cases = [
            ("123", Decimal("123")),
            ("123.456", Decimal("123.456")),
            ("-123.456", Decimal("-123.456")),
            ("0.0", Decimal("0.0")),
            ("1E10", Decimal("1E10")),
            ("1e10", Decimal("1e10")),
            ("1.23E-4", Decimal("1.23E-4")),
            ("1.23e-4", Decimal("1.23e-4")),
            ("+123.456", Decimal("+123.456")),
            ("000123.456000", Decimal("000123.456000")),
        ]

        for string, expected in test_cases:
            with self.subTest(string=string):
                result = loads(string)
                self.assertEqual(expected, result)
                self.assertIsInstance(result, Decimal)

    def test_dumps_unsupported_type(self) -> None:
        dumps = self._get_dumps_adapter()

        unsupported_values: list[Any] = [
            "123.456",
            123.456,
            123,
            None,
            [],
        ]

        for value in unsupported_values:
            with self.subTest(value=value):
                with self.assertRaises(TypeError) as cm:
                    dumps(value)

                self.assertIn(
                    "Unsupported type for decimal serialization", str(cm.exception)
                )

    def test_loads_invalid_decimal_format(self) -> None:
        loads = self._get_loads_adapter()

        invalid_strings = [
            "not-a-decimal",
            "123.45.67",
            "123.456.789",
            "abc123",
            "123abc",
            "",
            "   ",
        ]

        for invalid_string in invalid_strings:
            with self.subTest(string=invalid_string):
                with self.assertRaises(ValueError) as cm:
                    loads(invalid_string)

                self.assertIn("Unable to parse decimal from string", str(cm.exception))

    def test_decimal_special_values(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        special_cases = [
            Decimal("0"),
            Decimal("-0"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            Decimal("NaN"),
        ]

        for special_value in special_cases:
            with self.subTest(value=special_value):
                try:
                    converted_str = dumps(special_value)
                    converted_back = loads(converted_str)

                    self.assertIsInstance(converted_back, Decimal)
                    decimal_result = cast(Decimal, converted_back)
                    if special_value.is_nan():
                        self.assertTrue(decimal_result.is_nan())
                    else:
                        self.assertEqual(special_value, decimal_result)

                except Exception:
                    pass

    def test_protocol_compliance(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        self.assertTrue(callable(dumps))
        str_result = dumps(Decimal("42.5"))
        self.assertIsInstance(str_result, str)

        self.assertTrue(callable(loads))
        obj_result = loads("42.5")
        self.assertIsInstance(obj_result, object)
        self.assertIsInstance(obj_result, Decimal)

    def test_adapter_immutability(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        with self.assertRaises(AttributeError):
            dumps._context = "modified"  # type: ignore

        with self.assertRaises(AttributeError):
            loads._context = "modified"  # type: ignore

    def test_adapter_inequality(self) -> None:
        dumps1 = self._get_dumps_adapter()
        dumps2 = self._get_dumps_adapter()

        loads1 = self._get_loads_adapter()
        loads2 = self._get_loads_adapter()

        self.assertNotEqual(dumps1, dumps2)
        self.assertNotEqual(loads1, loads2)

    def test_return_types_consistency(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        test_decimals = [
            Decimal("0"),
            Decimal("1.23"),
            Decimal("-456.789"),
            Decimal("1E10"),
        ]

        for decimal_val in test_decimals:
            with self.subTest(decimal=decimal_val):
                str_result = dumps(decimal_val)
                self.assertIsInstance(str_result, str)

                decimal_result = loads(str_result)
                self.assertIsInstance(decimal_result, object)
                self.assertIsInstance(decimal_result, Decimal)

    def test_large_numbers_precision(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        large_numbers = [
            Decimal("123456789012345678901234567890.123456789012345678901234567890"),
            Decimal("0.000000000000000000000000000001"),
            Decimal("999999999999999999999999999999999999999999999999999999999999.99"),
        ]

        for large_num in large_numbers:
            with self.subTest(number=large_num):
                str_repr = dumps(large_num)
                restored = loads(str_repr)
                self.assertEqual(large_num, restored)

    def test_scientific_notation_handling(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        scientific_cases = [
            Decimal("1.23E+10"),
            Decimal("1.23E-10"),
            Decimal("5E+100"),
            Decimal("2.5E-50"),
            Decimal("1.0E+0"),
            Decimal("0E+10"),
        ]

        for sci_num in scientific_cases:
            with self.subTest(number=sci_num):
                str_repr = dumps(sci_num)
                restored = loads(str_repr)
                self.assertEqual(sci_num, restored)

    def test_negative_zero_handling(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        negative_zero = Decimal("-0")
        positive_zero = Decimal("0")

        neg_zero_str = dumps(negative_zero)
        pos_zero_str = dumps(positive_zero)

        restored_neg = loads(neg_zero_str)
        restored_pos = loads(pos_zero_str)

        self.assertEqual(negative_zero, restored_neg)
        self.assertEqual(positive_zero, restored_pos)

    def test_trailing_zeros_preservation(self) -> None:
        dumps = self._get_dumps_adapter()
        loads = self._get_loads_adapter()

        trailing_zero_cases = [
            Decimal("1.0"),
            Decimal("1.00"),
            Decimal("1.000"),
            Decimal("123.4500"),
            Decimal("0.10"),
            Decimal("0.100"),
        ]

        for decimal_val in trailing_zero_cases:
            with self.subTest(decimal=decimal_val):
                str_repr = dumps(decimal_val)
                restored = loads(str_repr)

                self.assertEqual(decimal_val, restored)
                self.assertEqual(str(decimal_val), str(restored))


if __name__ == "__main__":
    unittest.main()
