from types import ModuleType
from typing import Any, Iterable
from dataclasses import dataclass
from taew.ports.for_browsing_code_tree import Function


@dataclass(eq=False, frozen=True)
class Class:
    description: str
    py_module: ModuleType
    _functions: dict[str, Function]
    type_: type = type("RAMClass", (), {})

    def items(self) -> Iterable[tuple[str, Function]]:
        return self._functions.items()

    def __getitem__(self, name: str) -> Function:
        return self._functions[name]

    def get(self, name: str, default: Function | None = None) -> Function | None:
        return self._functions.get(name, default)

    def __contains__(self, name: str) -> bool:
        return name in self._functions

    def __call__(self, *args: Any, **kwargs: Any) -> object:
        # Step 1: Create a clean dynamic type
        # __call__ has to be defined at the class level
        if "__call__" in self._functions:
            methods = {  # type: ignore
                "__call__": lambda self_, *args_, **kwargs_: self._functions[  # type: ignore
                    "__call__"
                ](self_, *args_, **kwargs_)
            }
        else:
            methods = {}
        DynamicType = type("DynamicClassInstance", (object,), methods)  # type: ignore

        # Step 2: Instantiate it
        instance = DynamicType()

        # Step 3: Populate instance __dict__ with methods bound to this instance
        for name, func in self._functions.items():
            # Closure to bind instance to function
            def make_bound(f: Function) -> Any:
                return lambda *args_, **kwargs_: f(instance, *args_, **kwargs_)  # type: ignore

            setattr(instance, name, make_bound(func))

        # Step 4: Call __init__ if available
        if "__init__" in self._functions:
            self._functions["__init__"](instance, *args, **kwargs)

        return instance
