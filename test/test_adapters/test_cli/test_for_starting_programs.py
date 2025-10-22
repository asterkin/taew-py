import unittest
import sys
from typing import Optional, cast
from unittest.mock import Mock, patch
from taew.domain.argument import POSITIONAL_ONLY
from taew.domain.configuration import PortsMapping
from taew.ports.for_starting_programs import Main as MainProtocol
from taew.ports.for_building_command_parsers import (
    Build as BuildProtocol,
    Builder as BuilderProtocol,
)
from taew.ports.for_browsing_code_tree import (
    Function as FunctionProtocol,
    Module as ModuleProtocol,
    Package as PackageProtocol,
    Class as ClassProtocol,
)
from taew.ports.for_stringizing_objects import Dumps as DumpsProtocol


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        self._cmd_args = ["myapp", "dummy", "123"]
        self._ports = PortsMapping({})
        self._version = "0.1.0"
        self._mock_binder = Mock()
        self._mock_builder = self._get_builder()
        self._mock_build = self._get_build()
        self._mock_dumps = self._get_dumps()
        self._module = sys.modules[self.__module__]

    def _get_builder(self) -> BuilderProtocol:
        mock_builder = Mock(spec=BuilderProtocol)
        mock_builder.__iter__ = Mock()
        mock_builder.__iter__.return_value = iter(self._cmd_args[1:])
        mock_builder.add_command = Mock()
        mock_builder.add_subcommand = Mock()
        mock_builder.add_usage = Mock()
        mock_builder.execute = Mock(return_value=None)  # Default to None
        mock_builder.error = Mock()
        return mock_builder

    def _get_build(self) -> BuildProtocol:
        mock_build = Mock()
        mock_build.return_value = self._mock_builder
        return mock_build

    def _get_dumps(self) -> DumpsProtocol:
        mock_dumps = Mock(spec=DumpsProtocol)
        mock_dumps.return_value = "formatted_output"
        return mock_dumps

    def _get_func(self) -> FunctionProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            Argument,
            ReturnValue,
        )

        return Function(
            description="A dummy function",
            items_=(
                (
                    "value",
                    Argument(
                        annotation=int,
                        spec=(int, ()),
                        description="A value",
                        _default_value=None,
                        _has_default=True,
                        kind=POSITIONAL_ONLY,  # type: ignore
                    ),
                ),
            ),
            returns=ReturnValue(None, (None, ()), ""),
        )

    def _get_module(self) -> ModuleProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.module import Module

        return Module("Dummy module", items={"dummy": self._get_func()})

    def _get_package(self) -> PackageProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.package import Package

        return Package(
            "Dummy package", items={"dummy": self._get_func()}, version="0.1.0"
        )

    def _get_main(self, root: Optional[PackageProtocol] = None) -> MainProtocol:
        from taew.adapters.cli.for_starting_programs import Main

        return Main(
            _root=self._get_package() if root is None else root,
            _ports=self._ports,
            _binder=self._mock_binder,
            _build=self._mock_build,
            _dumps=self._mock_dumps,
        )

    def test_function_resolution_and_execution(self) -> None:
        main = self._get_main()

        # should execute without error
        main(self._cmd_args)

    def test_function_execution_with_none_result(self) -> None:
        """Test that no output is printed when execute returns None"""
        main = self._get_main()
        self._mock_builder.execute.return_value = None  # type: ignore

        with patch("builtins.print") as mock_print:
            main(self._cmd_args)

        # Verify dumps was not called and nothing was printed
        self._mock_dumps.assert_not_called()  # type: ignore
        mock_print.assert_not_called()

    def test_function_execution_with_result_prints_output(self) -> None:
        """Test that output is printed when execute returns a non-None result"""
        main = self._get_main()
        expected_result = {"status": "success", "data": [1, 2, 3]}
        self._mock_builder.execute.return_value = expected_result  # type: ignore
        self._mock_dumps.return_value = "formatted_result_output"  # type: ignore

        with patch("builtins.print") as mock_print:
            main(self._cmd_args)

        # Verify dumps was called with the result and output was printed
        self._mock_dumps.assert_called_once_with(expected_result)  # type: ignore
        mock_print.assert_called_once_with("formatted_result_output")

    def test_function_execution_with_various_result_types(self) -> None:
        """Test printing behavior with different result types"""
        main = self._get_main()

        test_cases = [
            ("string_result", "formatted_string"),
            (42, "formatted_number"),
            ([1, 2, 3], "formatted_list"),
            ({"key": "value"}, "formatted_dict"),
            (True, "formatted_boolean"),
        ]

        for result_value, formatted_output in test_cases:
            with self.subTest(result_type=type(result_value).__name__):
                # Reset mocks
                self._mock_dumps.reset_mock()  # type: ignore
                self._mock_builder.execute.return_value = result_value  # type: ignore
                self._mock_dumps.return_value = formatted_output  # type: ignore

                with patch("builtins.print") as mock_print:
                    main(self._cmd_args)

                self._mock_dumps.assert_called_once_with(result_value)  # type: ignore
                mock_print.assert_called_once_with(formatted_output)

    def test_dumps_adapter_integration(self) -> None:
        """Test integration with the dumps adapter"""

        # Use a real to_str adapter instead of mock
        def _get_real_dumps() -> DumpsProtocol:
            from taew.adapters.python.pprint.for_stringizing_objects.dumps import Dumps

            return Dumps()

        # Create main with real dumps adapter
        from taew.adapters.cli.for_starting_programs import Main

        main = Main(
            _root=self._get_package(),
            _ports=self._ports,
            _binder=self._mock_binder,
            _build=self._mock_build,
            _dumps=_get_real_dumps(),
        )

        test_result = {"message": "Hello, World!", "count": 42}
        self._mock_builder.execute.return_value = test_result  # type: ignore

        with patch("builtins.print") as mock_print:
            main(self._cmd_args)

        # Verify something was printed (exact format depends on pprint)
        mock_print.assert_called_once()
        printed_output = mock_print.call_args[0][0]
        self.assertIsInstance(printed_output, str)
        self.assertIn("Hello, World!", printed_output)
        self.assertIn("42", printed_output)

    def test_unknown_command_adds_usage(self) -> None:
        root = self._get_package()
        # Create a new mock builder with unknown command
        unknown_cmd_args = ["myapp", "unknown", "123"]
        mock_builder = Mock(spec=BuilderProtocol)
        mock_builder.__iter__ = Mock()
        mock_builder.__iter__.return_value = iter(unknown_cmd_args[1:])
        mock_builder.add_command = Mock()
        mock_builder.add_subcommand = Mock()
        mock_builder.add_usage = Mock()
        mock_builder.execute = Mock(return_value=None)
        mock_builder.error = Mock()

        mock_build = Mock()
        mock_build.return_value = mock_builder

        from taew.adapters.cli.for_starting_programs import Main

        main = Main(
            _root=root,
            _ports=self._ports,
            _binder=self._mock_binder,
            _build=mock_build,
            _dumps=self._mock_dumps,
        )

        # should not raise
        main(unknown_cmd_args)
        mock_builder.add_item_description.assert_called_once_with(
            "dummy", "A dummy function"
        )

    def test_class_without_call_triggers_error(self) -> None:
        from taew.adapters.python.ram.for_browsing_code_tree.class_ import Class
        from taew.adapters.python.ram.for_browsing_code_tree.package import Package

        dummy_class = Class("Class without call", _functions={}, py_module=self._module)
        root = Package(
            "Root", items={"Dummy": cast(ClassProtocol, dummy_class)}, version="0.1.0"
        )

        main = self._get_main(root)
        self._cmd_args[1] = "dummy"

        main(self._cmd_args)
        self._mock_builder.error.assert_called_once()  # type: ignore

    def test_class_instantiation_error(self) -> None:
        from taew.adapters.python.ram.for_browsing_code_tree.class_ import Class
        from taew.adapters.python.ram.for_browsing_code_tree.package import Package

        dummy_class = Class(
            "Class", _functions={"__call__": self._get_func()}, py_module=self._module
        )

        root = Package(
            "Root", items={"Dummy": cast(ClassProtocol, dummy_class)}, version="0.1.0"
        )
        main = self._get_main(root)
        self._mock_binder.create_instance.side_effect = Exception(
            "instantiation failed"
        )
        self._cmd_args[1] = "dummy"

        main(self._cmd_args)
        self._mock_builder.error.assert_called_once()  # type: ignore

    def test_class_instantiation_non_callable(self) -> None:
        from taew.adapters.python.ram.for_browsing_code_tree.class_ import Class
        from taew.adapters.python.ram.for_browsing_code_tree.package import Package

        dummy_class = Class(
            "Class", _functions={"__call__": self._get_func()}, py_module=self._module
        )

        root = Package(
            "Root", items={"Dummy": cast(ClassProtocol, dummy_class)}, version="0.1.0"
        )
        main = self._get_main(root)
        self._mock_binder.create_instance.return_value = object()  # not callable
        self._cmd_args[1] = "dummy"

        main(self._cmd_args)
        self._mock_builder.error.assert_called_once()  # type: ignore

    def test_class_with_call_and_result_prints_output(self) -> None:
        """Test that class execution with result prints output"""
        from taew.adapters.python.ram.for_browsing_code_tree.class_ import Class
        from taew.adapters.python.ram.for_browsing_code_tree.package import Package

        dummy_class = Class(
            "Class", _functions={"__call__": self._get_func()}, py_module=self._module
        )

        root = Package(
            "Root", items={"Dummy": cast(ClassProtocol, dummy_class)}, version="0.1.0"
        )
        main = self._get_main(root)

        # Mock successful class instantiation
        mock_instance = Mock()
        mock_instance.__call__ = Mock()  # type: ignore
        self._mock_binder.create_instance.return_value = mock_instance

        # Set execution result
        expected_result = "class_execution_result"
        self._mock_builder.execute.return_value = expected_result  # type: ignore
        self._mock_dumps.return_value = "formatted_class_result"  # type: ignore

        self._cmd_args[1] = "dummy"

        with patch("builtins.print") as mock_print:
            main(self._cmd_args)

        # Verify output was printed
        self._mock_dumps.assert_called_once_with(expected_result)  # type: ignore
        mock_print.assert_called_once_with("formatted_class_result")

    def test_empty_result_string_still_prints(self) -> None:
        """Test that empty string result is still printed"""
        main = self._get_main()
        self._mock_builder.execute.return_value = ""  # type: ignore # Empty string, but not None
        self._mock_dumps.return_value = "''"  # type: ignore

        with patch("builtins.print") as mock_print:
            main(self._cmd_args)

        # Even empty string should be printed since it's not None
        self._mock_dumps.assert_called_once_with("")  # type: ignore
        mock_print.assert_called_once_with("''")

    def test_zero_result_still_prints(self) -> None:
        """Test that zero value result is still printed"""
        main = self._get_main()
        self._mock_builder.execute.return_value = 0  # type: ignore # Falsy but not None
        self._mock_dumps.return_value = "0"  # type: ignore

        with patch("builtins.print") as mock_print:
            main(self._cmd_args)

        # Zero should be printed since it's not None
        self._mock_dumps.assert_called_once_with(0)  # type: ignore
        mock_print.assert_called_once_with("0")

    def test_false_result_still_prints(self) -> None:
        """Test that False result is still printed"""
        main = self._get_main()
        self._mock_builder.execute.return_value = False  # type: ignore # Falsy but not None
        self._mock_dumps.return_value = "False"  # type: ignore

        with patch("builtins.print") as mock_print:
            main(self._cmd_args)

        # False should be printed since it's not None
        self._mock_dumps.assert_called_once_with(False)  # type: ignore
        mock_print.assert_called_once_with("False")


if __name__ == "__main__":
    unittest.main()
