import unittest
import sys
from taew.ports.for_browsing_code_tree import (
    Class as ClassProtocol,
    Function as FunctionProtocol,
    Call as CallProtocol,
    Argument as ArgumentProtocol,
    ReturnValue as ReturnValueProtocol,
)
from taew.domain.argument import ArgumentKind, POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD


class TestRamClass(unittest.TestCase):
    def setUp(self) -> None:
        self._module = sys.modules[self.__module__]

    def _call(self) -> CallProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.call import Call

        return Call()

    def _arg(
        self, name: str, arg_type: type, arg_kind: ArgumentKind
    ) -> tuple[str, ArgumentProtocol]:
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
        args: tuple[tuple[str, ArgumentProtocol], ...],
        r_type: type | None,
    ) -> FunctionProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function

        return Function(
            description=name,
            items_=(
                self._arg(
                    "self",
                    object,
                    POSITIONAL_ONLY,  # type: ignore
                ),
            )
            + args,
            returns=self._returns(r_type),
            call=self._call(),
        )

    def _class(
        self, description: str, functions: dict[str, FunctionProtocol]
    ) -> ClassProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.class_ import Class

        return Class(
            description=description, _functions=functions, py_module=self._module
        )

    def test_happy_path(self) -> None:
        cls = self._class(
            description="Test class",
            functions={
                "__init__": self._function(
                    "__init__",
                    (
                        self._arg(
                            "x",
                            int,
                            POSITIONAL_OR_KEYWORD,  # type: ignore
                        ),
                    ),
                    None,
                ),
                "foo": self._function("foo", (), int),
            },
        )

        instance = cls(10)
        self.assertEqual(instance.foo(), 0)  # type: ignore

    def test_missing_method(self) -> None:
        cls = self._class(
            description="No methods",
            functions={"__init__": self._function("__init__", (), None)},
        )

        instance = cls()
        with self.assertRaises(AttributeError):
            instance.bar()  # type: ignore

    @unittest.expectedFailure
    def test_invalid_constructor_args(self) -> None:
        cls = self._class(
            description="Constructor with one arg",
            functions={
                "__init__": self._function(
                    "__init__",
                    (
                        self._arg(
                            "x",
                            int,
                            POSITIONAL_OR_KEYWORD,  # type: ignore
                        ),
                    ),
                    None,
                )
            },
        )

        cls()  # Missing required argument: 'x'


if __name__ == "__main__":
    unittest.main()
