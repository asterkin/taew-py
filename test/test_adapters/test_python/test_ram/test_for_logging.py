import unittest
from typing import Any
from taew.ports.for_logging import Logger as LoggerProtocol


class TestForLogging(unittest.TestCase):
    def create_ram_logger(self) -> tuple[LoggerProtocol, list[tuple[Any, ...]]]:
        from taew.adapters.python.ram.for_logging import Logger

        calls_list: list[tuple[Any, ...]] = []
        logger = Logger(_calls=calls_list)
        return logger, calls_list

    def test_logging_methods_store_calls_correctly(self) -> None:
        test_cases: tuple[
            tuple[
                str,
                tuple[object, ...],
                dict[str, object],
                tuple[str, object, tuple[object, ...], dict[str, object]],
            ],
            ...,
        ] = (
            # (method_name, call_args, call_kwargs, expected_stored_data)
            (
                "debug",
                ("Debug message %s", "test"),
                {"extra": {"key": "value"}},
                ("debug", "Debug message %s", ("test",), {"extra": {"key": "value"}}),
            ),
            (
                "info",
                ("User logged in",),
                {"exc_info": True, "user_id": 123},
                ("info", "User logged in", (), {"exc_info": True, "user_id": 123}),
            ),
            (
                "warning",
                ("Warning: %s", "something happened"),
                {},
                ("warning", "Warning: %s", ("something happened",), {}),
            ),
            ("error", ("Error occurred",), {}, ("error", "Error occurred", (), {})),
            (
                "critical",
                ("Critical failure!",),
                {},
                ("critical", "Critical failure!", (), {}),
            ),
        )

        for method_name, call_args, call_kwargs, expected in test_cases:
            with self.subTest(method=method_name):
                logger, calls_list = self.create_ram_logger()
                method = getattr(logger, method_name)

                method(*call_args, **call_kwargs)

                self.assertEqual(len(calls_list), 1)
                self.assertEqual(calls_list[0], expected)

    def test_log_method_stores_level_and_message(self) -> None:
        logger, calls_list = self.create_ram_logger()

        logger.log(25, "Custom level message %d", 42)

        self.assertEqual(len(calls_list), 1)
        method, msg_data, args, kwargs = calls_list[0]
        self.assertEqual(method, "log")
        self.assertEqual(msg_data, (25, "Custom level message %d"))
        self.assertEqual(args, (42,))
        self.assertEqual(kwargs, {})

    def test_multiple_calls_stored_in_order(self) -> None:
        logger, calls_list = self.create_ram_logger()

        logger.info("First message")
        logger.error("Second message")
        logger.debug("Third message")

        self.assertEqual(len(calls_list), 3)
        self.assertEqual(calls_list[0][0], "info")
        self.assertEqual(calls_list[1][0], "error")
        self.assertEqual(calls_list[2][0], "debug")


if __name__ == "__main__":
    unittest.main()
