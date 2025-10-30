# Gemini Development Guidelines for taew-py

This document provides guidance for the Gemini AI assistant when working on the `taew-py` repository. It outlines the project's architecture, development commands, coding conventions, and testing strategies.

## 1. Core Architecture: Ports & Adapters

This project implements the **Ports & Adapters (Hexagonal) Architecture**. The primary goal is to isolate the core business logic from external technologies and frameworks.

-   **`taew/domain/`**: Contains the central business logic and pure, behavior-less data structures (e.g., `Configuration`, `Argument`).
-   **`taew/ports/`**: Defines the interfaces (as Python `Protocol`s) that the core logic uses to communicate with the outside world. These are the "ports," named by their capability (e.g., `for_serializing_objects`, `for_binding_interfaces`).
-   **`taew/adapters/`**: Contains concrete implementations of the ports. They "adapt" external technologies to fit the requirements of the ports.
    -   Adapters are organized by the technology they wrap (e.g., `python/`, `cli/`).
    -   Key adapters include wrappers for `argparse`, `pprint`, `json`, and `inspect`.
-   **`taew/adapters/launch_time/`**: A special adapter group that provides a dependency injection (DI) mechanism. It wires the adapters to the ports at runtime based on a configuration mapping.

## 2. System Deep Dive: How It Works

Understanding the runtime flow is critical for evolving the system. The process typically flows from a CLI entry point, through configuration and dependency binding, to command execution.

### Step 1: Entry Point & Configuration

An application using this framework starts by building a `PortsMapping`. This is a dictionary that maps port protocols to their concrete adapter implementations.

The `taew.utils.configure.configure` function simplifies this by composing multiple adapter configurations into a single `PortsMapping`.

```python
# Example Application Entry Point
from taew.utils.cli import configure
from taew.adapters.launch_time.for_binding_interfaces.bind import bind as bind_function # Import the actual bind function

# 1. Configure all ports with their adapters
ports_mapping = configure(
    MyBusinessAdapter(), # Your application's adapter
    root_path=Path("./"),
    cli_package="my_app.cli",
    variants={date: {"_variant": "isoformat"}} # Disambiguate types with multiple adapters
)

# 2. Bind the main CLI handler
main = bind_function(for_starting_programs.Main, ports_mapping)

# 3. Execute
main(sys.argv[1:])
```

### Step 2: Dependency Injection (`bind` function)

The `bind` function, implemented in `taew/adapters/launch_time/for_binding_interfaces/bind.py`, is the core of the DI container. It is a stateless function with internal caching for efficiency. When called with an interface (a port `Protocol`) and the `PortsMapping`, it:

1.  **Resolves the Adapter**: Looks up the corresponding adapter implementation in the `PortsMapping`.
2.  **Creates an Instance**: Calls `create_instance` to instantiate the adapter.

### Step 3: Instance Creation (`create_instance`)

The `create_instance` function (`taew/adapters/launch_time/for_binding_interfaces/create_instance.py`) is responsible for instantiating an adapter and injecting its dependencies. It resolves constructor arguments in the following order:

1.  **Explicit `kwargs`**: Uses any values provided directly in the `PortConfiguration`.
2.  **Protocol-Typed Parameters**: If a constructor argument is typed as a port `Protocol`, it recursively calls `bind` to resolve and inject that dependency.
3.  **Recursive Resolution**: This process walks the entire dependency graph, creating instances as needed.

### Step 4: CLI Command Execution (`Main`)

The `Main` adapter (`taew/adapters/cli/for_starting_programs/main.py`) orchestrates the entire CLI flow:

1.  **Parse Command**: It interprets the command-line arguments (e.g., `my-app do-something --arg 123`) as a path to navigate.
2.  **Traverse Code Tree**: Using the `for_browsing_code_tree` port, it navigates the project's modules and classes to find a matching command (e.g., a `do_something` function or a `DoSomething` class).
3.  **Build Argument Parser**: Once the target command (function or callable class) is found, it uses the `for_building_command_parsers` port (typically the `argparse` adapter) to build a CLI parser from the target's signature.
4.  **Instantiate & Execute**: It uses `create_instance` to create the command's class (if it is a class) and then executes the command with the parsed arguments.
5.  **Serialize Output**: The return value of the command is serialized to a string for display using the `for_stringizing_objects` port (e.g., `pprint` adapter).

### Step 5: Type-Driven Adapter Discovery

For complex CLI arguments (e.g., passing a JSON string for a dataclass), the system automatically finds the correct parser:

1.  The `argparse` adapter sees a parameter of type `MyDataClass`.
2.  It calls a `find` utility which inspects the type (`MyDataClass`).
3.  The `find` utility locates the appropriate `Configure` class for that type (e.g., a dataclass-to-JSON configurator).
4.  This configurator provides the `PortsMapping` needed to bind a `Loads` adapter (from the `for_stringizing_objects` port).
5.  The `argparse` adapter then uses this specific `Loads` adapter as the `type` for the argument, which handles the string-to-object conversion.

## 3. Development Environment & Commands

The project uses `uv` for package management and `make` for task automation.

**General Workflow:**

1.  Navigate to the root project directory.
2.  Activate the virtual environment: `source .venv/bin/activate`. (If it doesn't exist, create it with `uv venv`).
3.  Install dependencies: `uv sync`.
4.  Run tasks using `make`.

**Key `make` Targets:**

-   `make all`: Run the full suite of static analysis and tests. **This is the primary verification command.**
-   `make static`: Run all static analysis tools (`ruff`, `mypy`, `pyright`).
-   `make coverage`: Run tests with code coverage analysis.
-   `make test-unit`: Run only the unit tests.
-   `make ruff-format`: Format the code using `ruff`.

## 4. Coding Style & Conventions

-   **Python Version**: Python 3.13+ with strict type annotations.
-   **Formatting/Linting**: `ruff` is used for both. Adhere to its rules (`make ruff-format`).
-   **Typing**:
    -   Use `|` for union types (e.g., `str | int`).
    -   Use `Optional[T]` for values that can be `None`.
    -   Use built-in generics (`list[str]`, `dict[int, str]`).
-   **Imports**: Order imports by ascending line length.
-   **Naming**:
    -   Modules and files use `snake_case`.
    -   Adapter packages follow the pattern `taew.adapters.<tech>.<library>.<capability>`.

## 5. Testing Guidelines

-   **Framework**: `unittest` is the standard test framework.
-   **Structure**: Tests mirror the source code structure within the `test/` directory (e.g., `test/test_adapters/test_python/...`).
-   **Protocol-Driven Tests**: This is a critical pattern. Tests should be written against the port's protocol, not the concrete adapter implementation. This ensures adapters are interchangeable. Use factory functions that return the protocol type.

    ```python
    # Example: Testing a Serializer
    from taew.ports.for_serializing_objects import Serialize as SerializeProtocol

    def _get_serializer() -> SerializeProtocol:
        # This factory can be swapped to test a different adapter
        from taew.adapters.python.pprint.for_serializing_objects import PPrint
        return PPrint()

    class MyTest(unittest.TestCase):
        def test_serialization(self):
            serializer = _get_serializer()
            # ... write test logic using the serializer protocol
    ```

-   **Test Discovery**: Test files must be named `test_*.py` and reside in directories containing an `__init__.py` file.
-   **Isolation**: For tests involving the `launch_time` binder, import and call `clear_root_cache()` in your `tearDown` method to ensure test isolation.

## 6. Creating a New Adapter

1.  **Location**: Create a new directory under `taew/adapters/python/<library>/<port_capability>/` or a similar top-level technology folder.
2.  **Bootstrap**: Create the necessary files: `pyproject.toml`, `__init__.py`, the implementation module, and a `for_configuring_adapters.py` module containing a `Configure` class.
3.  **Configure `pyproject.toml`**:
    -   Set the `[project].name` (e.g., `taew.adapters.python.yaml.for_serializing_objects`).
    -   Update relative paths for `tool.uv.sources`, `tool.mypy.mypy_path`, and `tool.pyright.extraPaths` to point to the `taew` directory.
4.  **Implement**: Create a module that implements the desired port protocol.
5.  **Test**: Create a parallel test structure under the `test/test_adapters/` directory. Write tests against the protocol as described above.

## 7. Git & GitHub Workflow

-   **Automation**: The `scripts/` directory contains shell scripts for managing GitHub issues and branches. The `gh` CLI is a prerequisite.
-   **Branching**: `bash scripts/issue-assign-branch.sh <issue-number>`
-   **New Issues**: `bash scripts/issue-new.sh -t "Title" -b "Body" -l "label"`
-   **Commits**: Follow the convention: `Implement feature X for Y (#123)`. The subject should be imperative.
-   **Checkpoints**: Use `bash scripts/checkpoint.sh "WIP: message"` for work-in-progress commits.

## 8. Special Conventions

### Promise-Style Queries (Mandatory)

-   **Purpose**: To align with Promise Theory, ensure clarity, and prevent incorrect actions.
-   **Workflow**: All imperative requests will be rephrased by me into a "desired state" or "promise." I will present this promise to you for approval **before** proceeding with any execution.
-   **Example**: If you say "Add a linter to the Makefile", I must respond with "Okay, I will proceed with the promise: 'The Makefile will contain a new 'lint' target that runs ruff.' Is this correct?" before I make any changes.

### `ask-all:` Prefix

-   **Purpose**: To query Claude and Codex with the same prompt, and have Gemini synthesize the results with its own response.
-   **Workflow**:
    1.  Start your prompt with the prefix `ask-all:`.
    2.  I will execute the `scripts/ask-all.sh` script, which calls the external Claude and Codex CLIs.
    3.  Simultaneously, I will process the prompt internally to form my own (Gemini's) response.
    4.  I will then provide a single, synthesized response, combining my internal analysis with the output from the script and noting any significant disagreements between the models.
-   **Example**: `ask-all: What are the pros and cons of using asyncio vs. threading in Python?`

### GitHub Workflow Triggers

-   **Purpose**: To automate common GitHub issue and branch management tasks directly from the chat.
-   **Prerequisite**: The `gh` CLI must be installed and authenticated.

#### `issue-new:`
-   **Syntax**: `issue-new: <type>, "Title", ["details"]`
-   **Action**: I will parse the arguments and execute the `scripts/issue-new.sh` script.
    -   `<type>` will be passed to the `-l` (label) flag.
    -   `"Title"` will be passed to the `-t` (title) flag.
    -   `"details"` (optional) will be passed to the `-b` (body) flag.
-   **Example**: `issue-new: feature, "Implement new serialization adapter", "This adapter should handle msgpack format."`

#### `issue-close:`
-   **Syntax**: `issue-close:`
-   **Action**: I will determine the current issue number by parsing the current git branch name (e.g., `123-some-feature`). I will then execute the `scripts/issue-close.sh` script with the extracted issue number.
-   **Example**: `issue-close:` (when on branch `123-some-feature`, this will run `bash scripts/issue-close.sh -i 123`).