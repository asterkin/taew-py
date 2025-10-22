import logging
import unittest
from taew.ports.for_logging import Logger as LoggerProtocol


class TestForLogging(unittest.TestCase):
    def create_stdlib_logger(self) -> LoggerProtocol:
        from taew.adapters.python.logging.for_logging import Logger

        return Logger("test_logger", {"level": logging.INFO})  # type: ignore[return-value]

    def test_logger_returns_stdlib_logger_instance(self) -> None:
        logger = self.create_stdlib_logger()

        self.assertIsInstance(logger, logging.Logger)

    def test_logger_implements_protocol_methods(self) -> None:
        logger = self.create_stdlib_logger()

        # Test that all protocol methods exist and are callable
        self.assertTrue(hasattr(logger, "debug"))
        self.assertTrue(hasattr(logger, "info"))
        self.assertTrue(hasattr(logger, "warning"))
        self.assertTrue(hasattr(logger, "error"))
        self.assertTrue(hasattr(logger, "critical"))
        self.assertTrue(hasattr(logger, "log"))

    def test_logger_with_different_names_creates_different_instances(self) -> None:
        from taew.adapters.python.logging.for_logging import Logger

        logger1 = Logger("test_logger1", {"level": logging.DEBUG})
        logger2 = Logger("test_logger2", {"level": logging.INFO})

        # Both should be stdlib Logger instances
        self.assertIsInstance(logger1, logging.Logger)
        self.assertIsInstance(logger2, logging.Logger)

        # Should have different names
        self.assertEqual(logger1.name, "test_logger1")
        self.assertEqual(logger2.name, "test_logger2")

    def test_configuration_is_applied_only_once(self) -> None:
        from taew.adapters.python.logging.for_logging import Logger

        # Reset the configured flag to test configuration
        Logger._configured = False  # type: ignore[attr-defined]

        # First instance should configure logging
        logger1 = Logger("config_test1", {"level": logging.WARNING})

        # Second instance should not reconfigure (configuration is already done)
        logger2 = Logger(
            "config_test2", {"level": logging.ERROR}
        )  # Different level, should be ignored

        # Both should be stdlib Logger instances
        self.assertIsInstance(logger1, logging.Logger)
        self.assertIsInstance(logger2, logging.Logger)

        # Configuration should have been applied (can't easily test basicConfig effects,
        # but we can verify the flag was set)
        self.assertTrue(Logger._configured)  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
