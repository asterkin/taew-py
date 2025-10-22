import unittest
from taew.utils.strings import pascal_to_snake, snake_to_pascal


class TestStrUtils(unittest.TestCase):
    def test_pascal_to_snake(self) -> None:
        self.assertEqual(pascal_to_snake("PascalCase"), "pascal_case")
        self.assertEqual(pascal_to_snake("ThisIsATest"), "this_is_a_test")
        self.assertEqual(pascal_to_snake("ConvertMe"), "convert_me")

    def test_snake_to_pascal(self) -> None:
        self.assertEqual(snake_to_pascal("snake_case"), "SnakeCase")
        self.assertEqual(snake_to_pascal("this_is_a_test"), "ThisIsATest")
        self.assertEqual(snake_to_pascal("convert_me"), "ConvertMe")


if __name__ == "__main__":
    unittest.main()
