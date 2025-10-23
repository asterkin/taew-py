import logging
import unittest
from pathlib import Path

from taew.domain.logging import INFO, DEBUG, WARNING, LogLevel
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.ports.for_logging import Logger as LoggerProtocol


class TestLoggingConfigureIntegration(unittest.TestCase):
    """Integration tests for logging adapter configuration."""

    def _get_configure(self, name: str, level: LogLevel = INFO) -> ConfigureProtocol:
        from taew.adapters.python.logging.for_logging.for_configuring_adapters import (
            Configure,
        )

        return Configure(_name=name, _level=level)

    def _bind(self, cfg: ConfigureProtocol) -> LoggerProtocol:
        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces import Bind

        ports = cfg()
        root = InspectRoot(Path("."))
        bind = Bind(root)
        return bind(LoggerProtocol, ports)

    def test_configure_with_default_level(self) -> None:
        """Test Configure with default INFO level."""
        cfg = self._get_configure("test_logger")
        logger = self._bind(cfg)

        self.assertIsNotNone(logger)
        # Verify it's a stdlib Logger instance
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")  # type: ignore[attr-defined]

    def test_configure_with_custom_level(self) -> None:
        """Test Configure with custom DEBUG level."""
        cfg = self._get_configure("debug_logger", DEBUG)
        logger = self._bind(cfg)

        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "debug_logger")  # type: ignore[attr-defined]

    def test_configure_with_warning_level(self) -> None:
        """Test Configure with WARNING level."""
        cfg = self._get_configure("warning_logger", WARNING)
        logger = self._bind(cfg)

        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "warning_logger")  # type: ignore[attr-defined]

    def test_configure_returns_ports_mapping(self) -> None:
        """Test that Configure returns a valid PortsMapping."""
        cfg = self._get_configure("config_test")
        ports = cfg()

        self.assertIsInstance(ports, dict)
        self.assertGreater(len(ports), 0)

    def test_multiple_loggers_with_different_names(self) -> None:
        """Test creating multiple loggers with different names."""
        cfg1 = self._get_configure("logger1", INFO)
        cfg2 = self._get_configure("logger2", DEBUG)

        logger1 = self._bind(cfg1)
        logger2 = self._bind(cfg2)

        self.assertIsInstance(logger1, logging.Logger)
        self.assertIsInstance(logger2, logging.Logger)
        self.assertEqual(logger1.name, "logger1")  # type: ignore[attr-defined]
        self.assertEqual(logger2.name, "logger2")  # type: ignore[attr-defined]
        self.assertNotEqual(logger1.name, logger2.name)  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
