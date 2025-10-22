import unittest
import sys
from typing import Protocol
from taew.ports.for_browsing_code_tree import (
    Root as RootProtocol,
    Class as ClassProtocol,
    Function as FunctionProtocol,
    Argument as ArgumentProtocol,
    Module as ModuleProtocol,
    Package as PackageProtocol,
)
from taew.domain.argument import POSITIONAL_OR_KEYWORD, ArgumentKind


class Workflow(Protocol):
    def __call__(self, x: str, y: int) -> str: ...
    def f(self, x: int) -> int: ...


class FunctionWorkflow(Protocol):
    def __call__(self, x: str, y: int) -> str: ...


class Adapter(Protocol):
    def __call__(self, x: str) -> str: ...


class TestLunchTimeAdapterBase(unittest.TestCase):
    def setUp(self) -> None:
        module_name_orig = TestLunchTimeAdapterBase.__module__
        self._module_name = module_name_orig.split(".")[-1]
        self._module = sys.modules[module_name_orig]

    def _make_argument(
        self,
        description: str,
        arg_type: type,
        make_unusable: bool = False,
        kind: ArgumentKind = POSITIONAL_OR_KEYWORD,
        default_value: object = None,
        has_default: bool = False,
    ) -> ArgumentProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            Argument,
        )

        return Argument(  # type: ignore
            description=description,
            spec=(None if make_unusable else arg_type, ()),
            annotation=arg_type,
            _default_value=default_value,
            _has_default=has_default,
            kind=kind,
        )

    def _make_function(
        self,
        description: str,
        items: tuple[tuple[str, ArgumentProtocol], ...],
        rt: type | None,
    ) -> FunctionProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.function import Function
        from taew.adapters.python.ram.for_browsing_code_tree.annotated_entity import (
            ReturnValue,
        )

        return Function(  # type: ignore
            description=description,
            items_=items,
            returns=ReturnValue(annotation=rt, spec=(rt, ()), description=""),
        )

    def _make_call_function(self, include_self: bool = True) -> FunctionProtocol:
        self_arg = (
            (
                (
                    "self",
                    self._make_argument(
                        arg_type=object,
                        description="",
                    ),
                ),
            )
            if include_self
            else ()
        )
        items = self_arg + (
            (
                "x",
                self._make_argument(
                    arg_type=str,
                    description="x argument",
                ),
            ),
            (
                "y",
                self._make_argument(
                    arg_type=int,
                    description="y argument",
                ),
            ),
        )

        return self._make_function(
            description="__call__",
            items=items,
            rt=str,
        )

    def _make_class(
        self, description: str, functions: dict[str, FunctionProtocol]
    ) -> ClassProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.class_ import Class

        return Class(  # type: ignore
            description=description, _functions=functions, py_module=self._module
        )

    def _make_workflow_class(self) -> ClassProtocol:
        init_func = self._make_function(
            description="__init__",
            items=(
                (
                    "self",
                    self._make_argument(
                        arg_type=object,
                        description="",
                    ),
                ),
                (
                    "adapter",
                    self._make_argument(
                        arg_type=Adapter,
                        description="",
                    ),
                ),
            ),
            rt=None,
        )
        call_func = self._make_call_function()
        f_func = self._make_function(
            description="f",
            items=(
                (
                    "self",
                    self._make_argument(arg_type=object, description=""),
                ),
                (
                    "x",
                    self._make_argument(
                        arg_type=int,
                        description="x argument",
                    ),
                ),
            ),
            rt=int,
        )
        return self._make_class(
            description="Workflow implementation",
            functions={"__init__": init_func, "__call__": call_func, "f": f_func},
        )

    def _make_adapter_class(self) -> ClassProtocol:
        return self._make_class(
            description="Adapter implementation",
            functions={
                "__init__": self._make_function(
                    description="__init__",
                    items=(
                        (
                            "self",
                            self._make_argument(
                                arg_type=object,
                                description="",
                            ),
                        ),
                    ),
                    rt=None,
                ),
                "__call__": self._make_function(
                    description="__call__",
                    items=(
                        (
                            "self",
                            self._make_argument(
                                arg_type=object,
                                description="",
                            ),
                        ),
                        (
                            "x",
                            self._make_argument(
                                arg_type=str,
                                description="x argument",
                            ),
                        ),
                    ),
                    rt=str,
                ),
            },
        )

    def _make_module(
        self, description: str, items: dict[str, ClassProtocol | FunctionProtocol]
    ) -> ModuleProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.module import Module

        return Module(  # type: ignore
            description=description,
            items=items,
        )

    def _make_package(
        self,
        description: str,
        items: dict[
            str, ClassProtocol | FunctionProtocol | ModuleProtocol | PackageProtocol
        ],
    ) -> PackageProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.package import Package

        return Package(  # type: ignore
            description=description, items=items, version="0.1.0"
        )

    def _make_root(
        self, items: dict[str, ModuleProtocol | PackageProtocol]
    ) -> RootProtocol:
        from taew.adapters.python.ram.for_browsing_code_tree.root import Root

        return Root(items=items)  # type: ignore
