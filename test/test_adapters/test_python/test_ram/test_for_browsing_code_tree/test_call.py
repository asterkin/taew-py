import unittest
from typing import Any
from taew.ports.for_browsing_code_tree import (
    Function as FunctionProtocol,
    Call as CallProtocol,
    Argument as ArgumentProtocol,
    ReturnValue as ReturnValueProtocol,
)
from taew.domain.argument import (
    ArgumentKind,
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    KEYWORD_ONLY,
    VAR_POSITIONAL,
    VAR_KEYWORD,
)


class TestCall(unittest.TestCase):
    def _call(self) -> CallProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.call import Call

        return Call()

    def _function(
        self,
        description: str,
        items: tuple[tuple[str, ArgumentProtocol], ...],
        returns: ReturnValueProtocol,
    ) -> FunctionProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function

        return Function(
            description=description, items_=items, returns=returns, call=self._call()
        )

    def _argument(
        self,
        annotation: Any,
        spec: tuple[Any, tuple[Any, ...]],
        description: str,
        default_value: object,
        has_default: bool,
        kind: ArgumentKind,
    ) -> ArgumentProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            Argument,
        )

        return Argument(
            annotation=annotation,
            spec=spec,
            description=description,
            _default_value=default_value,
            _has_default=has_default,
            kind=kind,
        )

    def _returns(
        self,
        annotation: Any,
        spec: tuple[Any, tuple[Any, ...]],
        description: str,
    ) -> ReturnValueProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
        )

        return ReturnValue(
            annotation=annotation,
            spec=spec,
            description=description,
        )

    def test_call_argument_binding_pass(self) -> None:
        pass_cases: list[dict[str, Any]] = [
            {
                "function": self._function(
                    "positional only succeeds",
                    (
                        (
                            "x",
                            self._argument(
                                int,
                                (
                                    int,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                POSITIONAL_ONLY,  # type: ignore
                            ),
                        ),
                    ),
                    self._returns(None, (None, ()), ""),
                ),
                "args": (42,),
                "kwargs": {},
            },
            {
                "function": self._function(
                    "keyword-only required",
                    (
                        (
                            "x",
                            self._argument(
                                int,
                                (
                                    int,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                KEYWORD_ONLY,  # type: ignore
                            ),
                        ),
                    ),
                    self._returns(None, (None, ()), ""),
                ),
                "args": (),
                "kwargs": {"x": 42},
            },
            {
                "function": self._function(
                    "*args absorbs extras",
                    (
                        (
                            "x",
                            self._argument(
                                int,
                                (
                                    int,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                POSITIONAL_OR_KEYWORD,  # type: ignore
                            ),
                        ),
                        (
                            "args",
                            self._argument(
                                tuple,
                                (
                                    tuple,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                VAR_POSITIONAL,  # type: ignore
                            ),
                        ),
                    ),
                    self._returns(None, (None, ()), ""),
                ),
                "args": (1, 2, 3),
                "kwargs": {},
            },
            {
                "function": self._function(
                    "**kwargs absorbs unknown keywords",
                    (
                        (
                            "x",
                            self._argument(
                                int,
                                (
                                    int,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                POSITIONAL_OR_KEYWORD,  # type: ignore
                            ),
                        ),
                        (
                            "kwargs",
                            self._argument(
                                str,
                                (
                                    str,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                VAR_KEYWORD,  # type: ignore
                            ),
                        ),
                    ),
                    self._returns(None, (None, ()), ""),
                ),
                "args": (1,),
                "kwargs": {"extra": "ok"},
            },
        ]

        for case in pass_cases:
            with self.subTest(name=f"PASS: {case['function'].description}"):
                case["function"](*case["args"], **case["kwargs"])

    def test_call_argument_binding_fail(self) -> None:
        fail_cases: list[dict[str, Any]] = [
            {
                "function": self._function(
                    "positional only fails with keyword",
                    (
                        (
                            "x",
                            self._argument(
                                int,
                                (
                                    int,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                POSITIONAL_ONLY,  # type: ignore
                            ),
                        ),
                    ),
                    self._returns(None, (None, ()), ""),
                ),
                "args": (),
                "kwargs": {"x": 42},
                "exc": ValueError,
            },
            {
                "function": self._function(
                    "missing required keyword-only",
                    (
                        (
                            "x",
                            self._argument(
                                int,
                                (
                                    int,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                KEYWORD_ONLY,  # type: ignore
                            ),
                        ),
                    ),
                    self._returns(None, (None, ()), ""),
                ),
                "args": (),
                "kwargs": {},
                "exc": ValueError,
            },
            {
                "function": self._function(
                    "excess args with no *args",
                    (
                        (
                            "x",
                            self._argument(
                                int,
                                (
                                    int,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                POSITIONAL_OR_KEYWORD,  # type: ignore
                            ),
                        ),
                    ),
                    self._returns(None, (None, ()), ""),
                ),
                "args": (1, 2),
                "kwargs": {},
                "exc": ValueError,
            },
            {
                "function": self._function(
                    "type mismatch",
                    (
                        (
                            "x",
                            self._argument(
                                int,
                                (
                                    int,
                                    (),
                                ),
                                "",
                                None,
                                False,
                                POSITIONAL_ONLY,  # type: ignore
                            ),
                        ),
                    ),
                    self._returns(None, (None, ()), ""),
                ),
                "args": ("wrong-type",),
                "kwargs": {},
                "exc": TypeError,
            },
        ]

        for case in fail_cases:
            with self.subTest(name=f"FAIL: {case['function'].description}"):
                with self.assertRaises(case["exc"]):
                    case["function"](*case["args"], **case["kwargs"])


if __name__ == "__main__":
    unittest.main()
