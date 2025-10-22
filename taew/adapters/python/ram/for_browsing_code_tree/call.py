from dataclasses import dataclass
from typing import Any
from taew.domain.argument import POSITIONAL_ONLY
from taew.ports.for_browsing_code_tree import Function, is_interface


@dataclass(eq=False, frozen=True)
class Call:
    def __call__(self, func: Function, *args: Any, **kwargs: Any) -> Any:
        current_state = 0
        current_kind = POSITIONAL_ONLY
        len_args = len(args)
        exclude_keyword = set[str]()
        args_pos = -1

        def _mandatory_positional_only(
            name: str, i: int
        ) -> tuple[int, tuple[Any, ...]]:
            if i >= len_args:
                raise ValueError(
                    f"Mandatory positional-only argument '{name}' is missing"
                )
            return i, (args[i],)

        def _mandatory_positional_or_keyword(
            name: str, i: int
        ) -> tuple[int, tuple[Any, ...]]:
            if i < len_args:
                return i, (args[i],)
            if name not in kwargs:
                raise ValueError(f"Missing required argument: '{name}'")
            exclude_keyword.add(name)
            return i, (kwargs[name],)

        def _var_positional(_: str, i: int) -> tuple[int, tuple[Any, ...]]:
            return (len_args, (args[i:],) if i < len_args else tuple[Any, ...]())

        def _mandatory_keyword_only(name: str, i: int) -> tuple[int, tuple[Any, ...]]:
            if len_args > 0 and i < len_args:
                raise ValueError(
                    f"Unexpected positional instead of keyword-only argument '{name}'"
                )
            if name not in kwargs:
                raise ValueError(f"Missing required keyword-only argument: '{name}'")
            exclude_keyword.add(name)
            return len_args, (kwargs[name],)

        def _var_keyword(name: str, i: int) -> tuple[int, tuple[Any, ...]]:
            if i < len_args:
                raise ValueError(
                    f"Unexpected positional instead of var-keyword argument '{name}'"
                )
            result = tuple(
                (k, v) for k, v in kwargs.items() if k not in exclude_keyword
            )
            exclude_keyword.update(k for k, _ in result)
            return len_args, tuple(v for _, v in result)

        def _optional_positional_only(_: str, i: int) -> tuple[int, tuple[Any, ...]]:
            return (i, (args[i],)) if i < len_args else (len_args, tuple[Any, ...]())

        def _optional_positional_or_keyword(
            name: str, i: int
        ) -> tuple[int, tuple[Any, ...]]:
            exclude_keyword.add(name)
            if i < len_args:
                return i, (args[i],)
            elif name in kwargs:
                return len_args, (kwargs[name],)
            else:
                return len_args, tuple[Any, ...]()

        def _optional_keyword_only(name: str, i: int) -> tuple[int, tuple[Any, ...]]:
            if i < len_args:
                raise ValueError(
                    f"Unexpected optional positional instead of optional keyword-only argument '{name}'"
                )
            if name in kwargs:
                exclude_keyword.add(name)
                return len_args, (kwargs[name],)
            else:
                return len_args, tuple[Any, ...]()

        state_machine = (
            (
                _mandatory_positional_only,
                _mandatory_positional_or_keyword,
                _var_positional,
                _mandatory_keyword_only,
                _var_keyword,
            ),
            (
                _optional_positional_only,
                _optional_positional_or_keyword,
                _var_positional,
                _optional_keyword_only,
                _var_keyword,
            ),
        )

        for i, (name, arg) in enumerate(func.items()):
            if current_state == 0 and not arg.default.is_empty():
                current_state += 1

            if arg.kind < current_kind:
                raise ValueError(
                    f"Unexpected argument kind: {arg.kind} for argument '{name}' (cannot be less than {current_kind})"
                )
            if arg.kind > current_kind:
                current_kind = arg.kind

            if arg.kind >= len(state_machine[current_state]):
                raise ValueError(
                    f"Unexpected argument kind: {arg.kind} for argument '{name}'"
                )

            args_pos, value = state_machine[current_state][arg.kind](name, i)

            for v in value:
                if not is_interface(arg) and not isinstance(v, arg.annotation):
                    raise TypeError(
                        f"Argument '{name}' must be of type {arg.annotation}, got {type(v)}"
                    )

        if args_pos < len_args - 1:
            raise ValueError("Too many positional arguments provided")

        remaining_keywords = set(kwargs.keys()) - exclude_keyword
        if remaining_keywords:
            raise ValueError(
                f"Too many keyword arguments provided: {remaining_keywords}"
            )

        returns = func.returns.spec[0]
        if returns is None:
            return None
        elif returns == Any:
            return object()
        else:
            return returns()
