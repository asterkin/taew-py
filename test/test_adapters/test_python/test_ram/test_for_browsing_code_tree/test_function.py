import unittest
from taew.domain.argument import POSITIONAL_OR_KEYWORD
from taew.ports.for_browsing_code_tree import (
    Function as FunctionProtocol,
    Call as CallProtocol,
    Argument as ArgumentProtocol,
    ReturnValue as ReturnValueProtocol,
)


class TestFunctionCall(unittest.TestCase):
    def _call(self) -> CallProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.call import Call

        return Call()

    def _arg(self, name: str, arg_type: type) -> tuple[str, ArgumentProtocol]:
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            Argument,
        )

        return name, Argument(
            annotation=arg_type,
            spec=(arg_type, ()),
            description=name,
            _default_value=None,
            _has_default=False,
            kind=POSITIONAL_OR_KEYWORD,  # type: ignore
        )

    def _returns(self, r_type: type | None) -> ReturnValueProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
        )

        return ReturnValue(
            annotation=r_type,
            spec=(r_type, ()),
            description="returns",
        )

    def _function(
        self,
        name: str,
        r_type: type | None,
    ) -> FunctionProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function

        # Define mock metadata for a function f(x: int, y: int = 5) -> int
        items = (self._arg("x", int), self._arg("y", int))

        return Function(
            description=name,
            items_=items,
            returns=self._returns(r_type),
            call=self._call(),
        )

    def test_simple_function(self) -> None:
        # Create function with test-based call validator
        func = self._function("Adds two numbers", int)

        # This should pass all checks and return int()
        result = func(3, y=4)
        self.assertEqual(result, 0)  # int() default return used by validator

    def test_argument_missing(self) -> None:
        func = self._function("Test missing arguments", int)

        self.assertRaises(ValueError, func)


if __name__ == "__main__":
    unittest.main()
