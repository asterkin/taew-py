import unittest
import io
import sys
from typing import Any
from collections.abc import Sequence
from contextlib import redirect_stdout, redirect_stderr

from taew.domain.argument import POSITIONAL_OR_KEYWORD
from taew.domain.configuration import PortConfigurationDict
from taew.ports import for_stringizing_objects as stringizing_port
from taew.ports.for_building_command_parsers import Builder as BuilderProtocol
from taew.ports.for_browsing_code_tree import (
    Function as FunctionProtocol,
    Module as ModuleProtocol,
)
from taew.ports.for_stringizing_objects import Loads


class StubFind:
    def __init__(self, mapping: dict[Any, tuple[type[Any], Any]] | None = None) -> None:
        self._mapping = mapping or {}
        self.calls: list[tuple[Any, Any]] = []

    def __call__(self, arg: Any, port: Any) -> tuple[type[Any], Any]:
        self.calls.append((arg, port))
        if arg in self._mapping:
            return self._mapping[arg]
        raise LookupError(f"No configuration for {arg!r}")


class StubBind:
    def __init__(self, loads: Loads | None) -> None:
        self._loads = loads
        self.calls: list[tuple[type[Any], Any]] = []

    def __call__(self, interface: type[Any], ports: Any) -> Loads:
        self.calls.append((interface, ports))
        if self._loads is None:
            raise LookupError("No loads configured")
        return self._loads


class TestBuilder(unittest.TestCase):
    def _get_func(self) -> FunctionProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
            Argument,
        )

        return Function(
            description="Test function",
            items_=(
                (
                    "arg1",
                    Argument(
                        annotation=int,
                        spec=(int, ()),
                        description="first argument",
                        _default_value=None,
                        _has_default=True,
                        kind=POSITIONAL_OR_KEYWORD,
                    ),
                ),
                (
                    "arg2",
                    Argument(
                        annotation=str,
                        spec=(str, ()),
                        description="second argument",
                        _default_value=None,
                        _has_default=True,
                        kind=POSITIONAL_OR_KEYWORD,
                    ),
                ),
            ),
            returns=ReturnValue(int, (int, ()), ""),
        )

    def _get_module(self) -> ModuleProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.module import Module

        return Module("test module", items={"test_function": self._get_func()})

    def _get_builder(
        self,
        description: str,
        version: str,
        cmd_args: Sequence[str],
        *,
        find_mapping: dict[Any, tuple[type[Any], Any]] | None = None,
        loads: Loads | None = None,
    ) -> BuilderProtocol:
        from taew.adapters.python.argparse.for_building_command_parsers.build import (
            Build,
        )

        self._find_stub = StubFind(find_mapping)
        self._bind_stub = StubBind(loads)
        build = Build(self._find_stub, self._bind_stub)  # type: ignore
        return build(description, version, cmd_args)

    def setUp(self) -> None:
        self._sys_args = sys.argv

    def tearDown(self) -> None:
        sys.argv = self._sys_args
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    def test_help_output(self) -> None:
        args = ["myapp", "--help"]
        sys.argv = args
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        with (
            redirect_stdout(out_buf),
            redirect_stderr(err_buf),
            self.assertRaises(SystemExit),
        ):
            builder = self._get_builder("test cli", "0.1.0", args)
            builder.add_command("dummy", "desc", self._get_func())
            builder.execute(None, args)
        output = out_buf.getvalue()
        err = err_buf.getvalue()
        self.assertIn("usage:", output)
        self.assertIn("dummy", output)
        self.assertEqual(err, "")

    def test_command_execution(self) -> None:
        args = ["myapp", "dummy", "42", "hello"]
        sys.argv = args
        func = self._get_func()
        builder = self._get_builder("test cli", "0.1.0", args)
        builder.add_command("dummy", "desc", func)
        result = builder.execute(func, args)  # function call will check arguments
        # Since execute now returns Any, verify it returns something
        self.assertIsNotNone(result)

    def test_command_execution_with_return_value(self) -> None:
        """Test that execute returns the result of the executed function"""
        args = ["myapp", "dummy", "42", "hello"]
        sys.argv = args

        expected_result = "test_return_value"

        def mock_func(arg1: int, arg2: str) -> str:
            self.assertEqual(arg1, 42)
            self.assertEqual(arg2, "hello")
            return expected_result

        builder = self._get_builder("test cli", "0.1.0", args)
        builder.add_command("dummy", "desc", self._get_func())
        result = builder.execute(mock_func, args)

        self.assertEqual(result, expected_result)

    def test_execute_with_none_function(self) -> None:
        """Test execute with None function returns None"""
        args = ["myapp", "--version"]
        sys.argv = args

        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            builder = self._get_builder("test cli", "0.1.0", args)
            _ = builder.execute(None, args)

    def test_unknown_command_prints_usage(self) -> None:
        args = ["myapp", "unknown"]
        sys.argv = args
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        with (
            redirect_stdout(out_buf),
            redirect_stderr(err_buf),
            self.assertRaises(SystemExit),
        ):
            builder = self._get_builder("test cli", "0.1.0", args)
            builder.add_item_description("known", "A known command")
            builder.execute(None, args)
        output = out_buf.getvalue()
        err = err_buf.getvalue()
        self.assertIn("usage:", err)
        self.assertEqual(output, "")

    def test_version_output(self) -> None:
        args = ["myapp", "--version"]
        sys.argv = args
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        with (
            redirect_stdout(out_buf),
            redirect_stderr(err_buf),
            self.assertRaises(SystemExit),
        ):
            builder = self._get_builder("test cli", "0.1.0", args)
            builder.execute(None, args)
        output = out_buf.getvalue()
        err = err_buf.getvalue()
        self.assertIn("myapp", output)
        self.assertIn("0.1.0", output)
        self.assertEqual(err, "")

    def test_builder_iterator(self) -> None:
        """Test the __iter__ method that filters out help/version flags"""
        args = ["myapp", "cmd1", "--help", "arg1", "-v", "arg2", "--version"]
        builder = self._get_builder("test cli", "0.1.0", args)

        # Should filter out -h, --help, -v, --version
        filtered_args = list(builder)
        self.assertEqual(filtered_args, ["cmd1", "arg1", "arg2"])

    def test_subcommand_handling(self) -> None:
        """Test adding and using subcommands"""
        args = ["myapp", "parent", "child", "42", "hello"]
        sys.argv = args

        builder = self._get_builder("test cli", "0.1.0", args)
        builder.add_subcommand("parent", "Parent command")
        builder.add_command("child", "Child command", self._get_func())

        # Execute with a mock function to verify it's called and returns value
        expected_result = "subcommand_result"

        def mock_func(*args: Any, **kwargs: Any) -> str:
            self.assertEqual(args, (42, "hello"))
            return expected_result

        result = builder.execute(mock_func, args)
        self.assertEqual(result, expected_result)

    def _get_func_with_different_kinds(self) -> FunctionProtocol:
        """Create a function with KEYWORD_ONLY, VAR_POSITIONAL arguments"""
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
            Argument,
        )
        from taew.domain.argument import KEYWORD_ONLY, VAR_POSITIONAL, POSITIONAL_ONLY

        return Function(
            description="Complex function",
            items_=(
                (
                    "pos_only",
                    Argument(
                        annotation=str,
                        spec=(str, ()),
                        description="positional only",
                        _default_value=None,
                        _has_default=True,
                        kind=POSITIONAL_ONLY,
                    ),
                ),
                (
                    "var_pos",
                    Argument(
                        annotation=str,
                        spec=(str, ()),
                        description="var positional",
                        _default_value=None,
                        _has_default=True,
                        kind=VAR_POSITIONAL,
                    ),
                ),
                (
                    "kw_only",
                    Argument(
                        annotation=int,
                        spec=(int, ()),
                        description="keyword only",
                        _default_value=None,
                        _has_default=True,
                        kind=KEYWORD_ONLY,
                    ),
                ),
                (
                    "optional_kw",
                    Argument(
                        annotation=str,
                        spec=(str, ()),
                        description="optional keyword",
                        _default_value="default",
                        _has_default=True,
                        kind=KEYWORD_ONLY,
                    ),
                ),
            ),
            returns=ReturnValue(None, (None, ()), ""),
        )

    def test_keyword_only_arguments(self) -> None:
        """Test KEYWORD_ONLY argument handling"""
        args = ["myapp", "cmd", "pos_val", "123", "default_val"]
        sys.argv = args

        func = self._get_func_with_different_kinds()
        builder = self._get_builder("test cli", "0.1.0", args)
        builder.add_command("cmd", "Command with keyword args", func)

        expected_result = "keyword_test_result"

        def mock_func(*args: Any, **kwargs: Any) -> str:
            self.assertEqual(args, ("pos_val",))  # Only pos_only arg
            self.assertEqual(kwargs["kw_only"], 123)  # Still passed as kwarg
            self.assertEqual(kwargs["optional_kw"], "default_val")  # Optional kwarg
            return expected_result

        result = builder.execute(mock_func, args)
        self.assertEqual(result, expected_result)

    def _get_func_with_bool(self) -> FunctionProtocol:
        """Create function with boolean arguments"""
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
            Argument,
        )
        from taew.domain.argument import POSITIONAL_ONLY, KEYWORD_ONLY

        return Function(
            description="Bool function",
            items_=(
                (
                    "bool_pos",
                    Argument(
                        annotation=bool,
                        spec=(bool, ()),
                        description="bool positional",
                        _default_value=None,
                        _has_default=True,
                        kind=POSITIONAL_ONLY,
                    ),
                ),
                (
                    "bool_kw",
                    Argument(
                        annotation=bool,
                        spec=(bool, ()),
                        description="bool keyword",
                        _default_value=None,
                        _has_default=True,
                        kind=KEYWORD_ONLY,
                    ),
                ),
            ),
            returns=ReturnValue(None, (None, ()), ""),
        )

    def test_boolean_positional_argument(self) -> None:
        """Test boolean conversion for positional arguments"""
        for bool_val, expected in [
            ("true", True),
            ("false", False),
            ("1", True),
            ("0", False),
        ]:
            with self.subTest(bool_val=bool_val):
                args = ["myapp", "cmd", bool_val, "--bool-kw"]
                sys.argv = args

                func = self._get_func_with_bool()
                builder = self._get_builder("test cli", "0.1.0", args)
                builder.add_command("cmd", "Bool command", func)

                test_result = f"bool_result_{expected}"

                def mock_func(*args: Any, **kwargs: Any) -> str:
                    self.assertEqual(args[0], expected)
                    return test_result

                result = builder.execute(mock_func, args)
                self.assertEqual(result, test_result)

    def test_invalid_boolean_positional(self) -> None:
        """Test error handling for invalid boolean values"""
        args = ["myapp", "cmd", "invalid_bool", "--bool-kw"]
        sys.argv = args

        with self.assertRaises(SystemExit):
            func = self._get_func_with_bool()
            builder = self._get_builder("test cli", "0.1.0", args)
            builder.add_command("cmd", "Bool command", func)
            builder.execute(lambda *a, **k: None, args)

    def test_unsupported_type_error(self) -> None:
        """Test error for unsupported argument types"""
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
            Argument,
        )

        func = Function(
            description="Function with unsupported type",
            items_=(
                (
                    "bad_arg",
                    Argument(
                        annotation=list,
                        spec=(list, ()),
                        description="unsupported type",
                        _default_value=None,
                        _has_default=True,
                        kind=POSITIONAL_OR_KEYWORD,
                    ),
                ),
            ),
            returns=ReturnValue(None, (None, ()), ""),
        )

        args = ["myapp", "cmd"]
        sys.argv = args

        with self.assertRaises(SystemExit):
            builder = self._get_builder("test cli", "0.1.0", args)
            builder.add_command("cmd", "Bad command", func)

    def test_var_keyword_not_supported(self) -> None:
        """Test that VAR_KEYWORD raises an error"""
        from taew.domain.argument import VAR_KEYWORD
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
            Argument,
        )

        func = Function(
            description="Function with kwargs",
            items_=(
                (
                    "kwargs",
                    Argument(
                        annotation=dict,
                        spec=(dict, ()),
                        description="var keyword",
                        _default_value=None,
                        _has_default=True,
                        kind=VAR_KEYWORD,
                    ),
                ),
            ),
            returns=ReturnValue(None, (None, ()), ""),
        )

        args = ["myapp", "cmd"]
        sys.argv = args

        with self.assertRaises(SystemExit):
            builder = self._get_builder("test cli", "0.1.0", args)
            builder.add_command("cmd", "Command with kwargs", func)

    def test_custom_type_uses_find_and_bind(self) -> None:
        class Custom: ...

        def custom_loads(value: str) -> str:
            return f"parsed:{value}"

        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
            Argument,
        )

        func = Function(
            description="Custom function",
            items_=(
                (
                    "value",
                    Argument(
                        annotation=Custom,
                        spec=(Custom, ()),
                        description="custom",
                        _default_value=None,
                        _has_default=True,
                        kind=POSITIONAL_OR_KEYWORD,
                    ),
                ),
            ),
            returns=ReturnValue(None, (None, ()), ""),
        )

        port_config = PortConfigurationDict(adapter="custom.for_stringizing_objects")

        args = ["myapp", "cmd", "raw"]
        sys.argv = args
        builder = self._get_builder(
            "test cli",
            "0.1.0",
            args,
            find_mapping={Custom: (Custom, port_config)},
            loads=custom_loads,  # type: ignore
        )
        builder.add_command("cmd", "desc", func)

        def run(value: Any) -> str:
            self.assertEqual(value, "parsed:raw")
            return "ok"

        result = builder.execute(run, args)
        self.assertEqual(result, "ok")
        self.assertEqual(self._find_stub.calls, [(Custom, stringizing_port)])
        self.assertEqual(len(self._bind_stub.calls), 1)
        interface, ports = self._bind_stub.calls[0]
        self.assertIs(interface, Loads)
        self.assertEqual(ports[stringizing_port], port_config)

    def test_error_method(self) -> None:
        """Test the error method directly"""
        args = ["myapp"]

        err_buf = io.StringIO()
        with redirect_stderr(err_buf), self.assertRaises(SystemExit):
            builder = self._get_builder("test cli", "0.1.0", args)
            builder.error("Custom error message")

        self.assertIn("Custom error message", err_buf.getvalue())

    def test_execute_without_command(self) -> None:
        """Test execute when no command is provided"""
        args = ["myapp"]
        sys.argv = args

        out_buf = io.StringIO()
        with redirect_stdout(out_buf), self.assertRaises(SystemExit) as cm:
            builder = self._get_builder("test cli", "0.1.0", args)
            builder.execute(None, args)

        self.assertEqual(cm.exception.code, 1)
        self.assertIn("usage:", out_buf.getvalue())

    def test_float_argument(self) -> None:
        """Test float type conversion"""
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
            Argument,
        )

        func = Function(
            description="Float function",
            items_=(
                (
                    "float_arg",
                    Argument(
                        annotation=float,
                        spec=(float, ()),
                        description="float arg",
                        _default_value=None,
                        _has_default=True,
                        kind=POSITIONAL_OR_KEYWORD,
                    ),
                ),
            ),
            returns=ReturnValue(None, (None, ()), ""),
        )

        args = ["myapp", "cmd", "3.14"]
        sys.argv = args

        builder = self._get_builder("test cli", "0.1.0", args)
        builder.add_command("cmd", "Float command", func)

        expected_result = "float_test_result"

        def mock_func(*args: Any, **kwargs: Any) -> str:
            self.assertAlmostEqual(args[0], 3.14)
            return expected_result

        result = builder.execute(mock_func, args)
        self.assertEqual(result, expected_result)

    def test_execute_return_value_types(self) -> None:
        """Test that execute properly returns different types of values"""
        args = ["myapp", "cmd", "42", "hello"]
        sys.argv = args

        builder = self._get_builder("test cli", "0.1.0", args)
        builder.add_command("cmd", "desc", self._get_func())

        # Test various return types
        test_cases = [
            ("string_result", str),
            (42, int),
            (3.14, float),
            (True, bool),
            ([1, 2, 3], list),
            ({"key": "value"}, dict),
            (None, type(None)),
        ]

        for expected_result, expected_type in test_cases:
            with self.subTest(result_type=expected_type.__name__):

                def mock_func(*args: Any, **kwargs: Any) -> Any:
                    return expected_result

                result = builder.execute(mock_func, args)
                self.assertEqual(result, expected_result)
                self.assertIsInstance(result, expected_type)


if __name__ == "__main__":
    unittest.main()
