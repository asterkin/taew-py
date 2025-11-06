import sys
import argparse
from typing import Any
from pathlib import Path
from dataclasses import dataclass, field
from collections.abc import Sequence, Iterator, Callable

from taew.domain.argument import (
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    KEYWORD_ONLY,
    VAR_POSITIONAL,
)
from taew.ports.for_browsing_code_tree import (
    Function,
    Argument,
)
from taew.ports import for_stringizing_objects as stringizing_port
from taew.ports.for_stringizing_objects import Loads
from taew.ports.for_binding_interfaces import Bind as BindProtocol
from taew.ports.for_finding_configurations import Find as FindProtocol


@dataclass(eq=False)
class Builder:
    _find: FindProtocol
    _bind: BindProtocol
    description: str
    version: str
    cmd_args: Sequence[str]
    _root_parser: argparse.ArgumentParser = field(init=False)
    _parser: argparse.ArgumentParser = field(init=False)
    _current_subparsers: Any = field(default=None, init=False)
    _cmd_args: Sequence[str] = field(default_factory=tuple, init=False)
    _argparse_native_types: set[type] = field(
        default_factory=lambda: {str, int, float}, init=False
    )

    def __post_init__(self) -> None:
        self._root_parser = self._get_root_parser(
            self.description, self.version, self.cmd_args
        )
        self._parser = self._root_parser
        self._current_subparsers = self._root_parser.add_subparsers()
        self._cmd_args = self.cmd_args[1:]

    def __iter__(self) -> Iterator[str]:
        for cmd_arg in self._cmd_args:
            if cmd_arg not in {"-h", "--help", "-v", "--version"}:
                yield cmd_arg

    def add_subcommand(self, name: str, description: str) -> None:
        self._parser = self._current_subparsers.add_parser(
            name=name, description=description
        )
        self._current_subparsers = self._parser.add_subparsers()

    def add_command(self, name: str, description: str, func: Function) -> None:
        self._parser = self._current_subparsers.add_parser(
            name=name, description=description, help=description
        )
        self._add_command_arguments(func)

    def add_item_description(self, name: str, description: str) -> None:
        self._current_subparsers.add_parser(
            name=name, description=description, help=description
        )

    def error(self, msg: str) -> None:
        self._parser.error(msg)

    def execute(self, command: Callable[..., Any] | None, args: Sequence[str]) -> Any:
        # Skip program name (args[0]) when passing to argparse
        arg_values = vars(self._root_parser.parse_args(args[1:]))
        if "pos_args" in arg_values:
            pos_args = arg_values["pos_args"]
            del arg_values["pos_args"]
        else:
            pos_args = ()
        kw_args = arg_values
        if not command:
            self._root_parser.print_usage()
            sys.exit(1)
        return command(*pos_args, **kw_args)

    @staticmethod
    def _get_root_parser(
        description: str, version: str, args: Sequence[str]
    ) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=Path(args[0]).stem, description=description
        )
        parser.add_argument(
            "--version", action="version", version="%(prog)s - v" + version
        )
        return parser

    def _add_command_arguments(self, func: Function) -> None:
        for arg_name, param in func.items():
            if arg_name != "self":
                self._add_command_arg(arg_name, param)

    def _add_command_arg(self, func_arg_name: str, func_arg: Argument) -> None:
        func_arg_kind = func_arg.kind
        func_arg_type = func_arg.annotation

        def _str_to_bool(value: str) -> bool:
            v_l = value.lower()
            if v_l in {"true", "yes", "1"}:
                return True
            elif v_l not in {"false", "no", "0"}:
                self._parser.error(
                    f"Invalid boolean `{func_arg_name}` argument value `{value}`."
                )
            return False

        def _get_type_converter(arg_type: type) -> Any:
            if arg_type is bool:
                return _str_to_bool
            if arg_type in self._argparse_native_types:
                return arg_type

            loads = self._resolve_loads(func_arg_name, arg_type)

            def _wrapped_converter(value: str) -> Any:
                try:
                    return loads(value)
                except Exception as e:
                    self._parser.error(
                        f"Invalid {getattr(arg_type, '__name__', repr(arg_type))} "
                        f"`{func_arg_name}` argument value `{value}`: {e}"
                    )

            return _wrapped_converter

        if func_arg_kind in {POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD}:
            self._parser.add_argument(
                dest="pos_args",
                action="append",
                # positional_only and positional_or_keyword arguments will
                # be treated as mandatory regardless of whether default is defined or not
                type=_get_type_converter(func_arg_type),
                help=func_arg.description,
                metavar=func_arg_name,
            )
        elif func_arg_kind == VAR_POSITIONAL:
            self._parser.add_argument(
                dest="pos_args",
                action="extend",
                nargs="*",
                type=_get_type_converter(func_arg_type),
                help=func_arg.description,
                metavar=func_arg_name,
            )
        elif func_arg_kind == KEYWORD_ONLY:
            props: dict[str, Any] = {
                "dest": func_arg_name,
                "help": func_arg.description,
            }
            if func_arg_type is bool:
                props["action"] = argparse.BooleanOptionalAction
                self._parser.add_argument(
                    f"--{func_arg_name.replace('_', '-')}", **props
                )
            else:
                props["type"] = _get_type_converter(func_arg_type)
                self._parser.add_argument(**props)
        else:
            # VAR_KEYWORD (**kwargs) is not supported because:
            # 1. It's rarely useful in CLI contexts
            # 2. argparse doesn't have native support for arbitrary --key=value pairs
            # 3. Would require parse_known_args() which complicates the implementation
            self._parser.error(
                f"Unsupported argument type {func_arg_kind} of {func_arg_name}"
            )

    def _resolve_loads(self, func_arg_name: str, annotation: type) -> Loads:
        try:
            _, port_configuration = self._find(annotation, stringizing_port)
        except Exception as exc:  # pragma: no cover - parser.error exits
            self._parser.error(
                f"Unsupported argument type {annotation} of {func_arg_name}: {exc}"
            )

        try:
            return self._bind(Loads, {stringizing_port: port_configuration})
        except Exception as exc:  # pragma: no cover - parser.error exits
            self._parser.error(
                f"Failed to bind string parser for {annotation} "
                f"of {func_arg_name}: {exc}"
            )
        raise AssertionError("unreachable")


@dataclass(eq=False, frozen=True)
class Build:
    _find: FindProtocol
    _bind: BindProtocol

    def __call__(
        self, description: str, version: str, cmd_args: Sequence[str]
    ) -> Builder:
        return Builder(
            _find=self._find,
            _bind=self._bind,
            description=description,
            version=version,
            cmd_args=cmd_args,
        )
