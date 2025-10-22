import unittest
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestChoicesValidation(unittest.TestCase):
    def _get_configure(self, choices: tuple[object, ...]) -> ConfigureProtocol:
        from taew.adapters.python.choices.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_choices=choices)

    def test_duplicate_choices_raise_error(self) -> None:
        # Duplicate False appears twice
        with self.assertRaises(ValueError):
            _ = self._get_configure((False, True, False))

    def test_empty_choices_raise_error(self) -> None:
        with self.assertRaises(ValueError):
            _ = self._get_configure(())


if __name__ == "__main__":
    unittest.main()
