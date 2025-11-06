from typing import Any
from dataclasses import dataclass
from taew.utils.strings import snake_to_pascal
from collections.abc import Sequence, Callable
from taew.ports.for_binding_interfaces import CreateInstance
from taew.ports.for_stringizing_objects import Dumps
from taew.ports.for_building_command_parsers import Build, Builder
from taew.ports.for_browsing_code_tree import (
    Package,
    Module,
    Class,
    Function,
    is_class,
    is_function,
    is_package,
    is_module,
)

from ._common import MainBase

InstanceType = Callable[..., Any]
ItemType = Package | Module | Class | Function
ResultType = tuple[InstanceType | None, ItemType]


@dataclass(eq=False, frozen=True)
class Main(MainBase):
    _create_instance: CreateInstance
    _build: Build
    _dumps: Dumps

    def _try_as_function(
        self,
        item: ItemType,
        cmd_arg: str,
        cmd_arg_snake: str,
        builder: Builder,
    ) -> ResultType:
        """
        Try to add function that has the same name as its module
        e.g. function_name in function_name.py
        Raise an error otherwise.
        """
        if is_function(item):
            builder.add_command(cmd_arg, item.description, item)
            # Function object is callable, and in this case, item is also a command
            return item, item
        else:
            builder.error(
                f"Module {cmd_arg_snake} has {cmd_arg_snake} element, which is not a function"
            )
        return None, item

    def _create_class_instance(
        self, item: Class, cmd_arg_snake: str, cmd_arg_pascal: str, builder: Builder
    ) -> InstanceType | None:
        """
        Create an instance of the class.
        """
        try:
            instance = self._create_instance(item, self._ports_mapping)
            if callable(instance):
                return instance  # type: ignore
            builder.error(
                f"Class {cmd_arg_snake}.{cmd_arg_pascal} instance is not callable."
            )
        except Exception as e:
            builder.error(
                f"Class {cmd_arg_snake}.{cmd_arg_pascal} instance creation failed with {e}."
            )
        return None

    def _try_as_callable_class(
        self,
        item: ItemType,
        cmd_arg: str,
        cmd_arg_snake: str,
        cmd_arg_pascal: str,
        builder: Builder,
    ) -> ResultType:
        """
        Try to add a callable class that has a __call_method__.
        Could come from a module with corresponding snake_name or the same PascalName
        e.g. ClassName in class_name.py or in ClassName.py
        Raise an error otherwise.
        """
        if not is_class(item):
            builder.error(f"Element {cmd_arg_snake}.{cmd_arg_pascal} is not a class.")
        elif call_func := item.get("__call__"):
            instance = self._create_class_instance(
                item, cmd_arg_snake, cmd_arg_pascal, builder
            )
            builder.add_command(
                cmd_arg,
                call_func.description,
                call_func,
            )
            return instance, call_func
        else:
            builder.error(
                f"Class {cmd_arg_snake}.{cmd_arg_pascal} does not have a __call__ method."
            )
        return None, item

    def _try_snake_name(
        self,
        item: ItemType,
        cmd_arg: str,
        cmd_arg_snake: str,
        cmd_arg_pascal: str,
        builder: Builder,
    ) -> ResultType:
        if is_function(item):
            builder.add_command(cmd_arg, item.description, item)
            return item, item
        elif is_package(item) or is_module(item):
            if snake_item := item.get(cmd_arg_snake):
                return self._try_as_function(
                    snake_item,  # e.g. function_name in function_name.py
                    cmd_arg,
                    cmd_arg_snake,
                    builder,
                )
            elif pascal_item := item.get(cmd_arg_pascal):
                return self._try_as_callable_class(
                    pascal_item,  # e.g. ClassName in class_name.py
                    cmd_arg,
                    cmd_arg_snake,
                    cmd_arg_pascal,
                    builder,
                )
            else:
                builder.add_subcommand(  # e.g. package_name or module_name.py
                    cmd_arg, item.description
                )
        else:
            builder.error(
                f"Element {cmd_arg_snake}: {item} is not a function, package, or module."
            )
        return None, item

    def _try_pascal_name(
        self,
        item: ItemType,
        cmd_arg: str,
        cmd_arg_snake: str,
        cmd_arg_pascal: str,
        builder: Builder,
    ) -> ResultType:
        if is_class(item):
            return self._try_as_callable_class(
                item,  # e.g. ClassName in current.py or current_package
                cmd_arg,
                cmd_arg_snake,
                cmd_arg_pascal,
                builder,
            )
        elif is_module(item) or is_package(item):
            if pascal_item := item.get(cmd_arg_pascal):
                return self._try_as_callable_class(
                    pascal_item,  # e.g. ClassName in ClassName.py
                    cmd_arg,
                    cmd_arg_snake,
                    cmd_arg_pascal,
                    builder,
                )
            else:
                builder.error(
                    f"Element {cmd_arg_pascal}: No {cmd_arg_pascal} found in {item}."
                )
        else:
            builder.error(
                f"Element {cmd_arg_pascal}: {item} is not a class, package, or module."
            )
        return None, item

    def _find_command(self, builder: Builder) -> ResultType:
        current: Package | Module = self._cli_root
        for cmd_arg in builder:
            cmd_arg_snake = cmd_arg.replace("-", "_")
            cmd_arg_pascal = snake_to_pascal(cmd_arg_snake)
            if snake_item := current.get(cmd_arg_snake):
                command, next = self._try_snake_name(
                    snake_item,
                    cmd_arg,
                    cmd_arg_snake,
                    cmd_arg_pascal,
                    builder,
                )
                if not (is_package(next) or is_module(next)):
                    return command, next
                current = next
            elif pascal_item := current.get(cmd_arg_pascal):
                return self._try_pascal_name(
                    pascal_item,
                    cmd_arg,
                    cmd_arg_snake,
                    cmd_arg_pascal,
                    builder,
                )
            else:
                break
        return None, current

    def _try_function_description(
        self, name: str, item: Package | Module
    ) -> str | None:
        if func := item.get(name):
            return func.description
        return None

    def _try_class_description(self, name: str, item: Package | Module) -> str | None:
        if cls := item.get(name):
            if is_class(cls) and (call_func := cls.get("__call__")):
                return call_func.description
        return None

    def _try_function_or_class_description(
        self, name_snake: str, item: Package | Module
    ) -> str:
        """
        Try to get description of a function or callable class with the same name as parent package/module
        """
        name_pascal = snake_to_pascal(name_snake)
        if (
            description := self._try_function_description(name_snake, item)
        ) is not None:
            return description
        if (description := self._try_class_description(name_pascal, item)) is not None:
            return description
        return ""

    def _add_usage(self, current: Package | Module, builder: Builder) -> None:
        for name, item in current.items():
            if is_package(item) or is_module(item):
                if (description := item.description) == "":
                    description = self._try_function_or_class_description(name, item)
            else:
                description = item.description
            name_kebab = name.replace("_", "-")
            builder.add_item_description(name_kebab, description)

    def __call__(self, cmd_args: Sequence[str]) -> None:
        builder = self._build(
            self._cli_root.description, self._cli_root.version, cmd_args
        )
        command, current = self._find_command(builder)
        if is_package(current) or is_module(current):
            self._add_usage(current, builder)
        result = builder.execute(command, cmd_args)
        if result is not None:
            print(self._dumps(result))
