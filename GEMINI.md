# Gemini Development Guidelines for taew-adapters-py

This document provides guidance for the Gemini AI assistant when working on the `taew-adapters-py` repository. It outlines the project's architecture, development commands, coding conventions, and testing strategies.

## 1. Core Architecture: Ports & Adapters

This project implements the **Ports & Adapters (Hexagonal) Architecture**. The primary goal is to isolate the core business logic from external technologies and frameworks.

-   **`core/`**: Contains the central business logic.
    -   **`core/taew/domain/`**: Defines the core data structures and business rules.
    -   **`core/taew/ports/`**: Defines the interfaces (as Python `Protocol`s) that the core logic uses to communicate with the outside world. These are the "ports".

-   **Adapters (`python/`, `cli/`, etc.)**: These are concrete implementations of the ports. They "adapt" external technologies to fit the requirements of the ports.
    -   Adapters are organized by the technology they wrap (e.g., `python/argparse`, `python/ram`).
    -   Each adapter lives in its own sub-project with its own dependencies and tests.

-   **Configuration & Binding (`launch_time/`)**: A dependency injection system wires the adapters to the ports at runtime based on configuration (`PortsMapping`).

## 2. Development Environment & Commands

The project uses `uv` for package management and `make` for task automation within each sub-project.

**General Workflow:**

1.  Navigate to a sub-project directory (e.g., `cd core`).
2.  Activate the virtual environment: `source .venv/bin/activate`. (If it doesn't exist, create it with `uv venv`).
3.  Install dependencies: `uv sync`.
4.  Run tasks using `make`.

**Key `make` Targets (run from sub-project directories):**

-   `make all`: Run the full suite of static analysis and tests. This is the primary verification command.
-   `make static`: Run all static analysis tools (`ruff`, `mypy`, `pyright`).
-   `make coverage`: Run tests with code coverage analysis.
-   `make test-unit`: Run the unit tests.
-   `make ruff-format`: Format the code using `ruff`.

To build all sub-projects at once, use the root script: `bash scripts/build-all.sh`.

## 3. Coding Style & Conventions

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

## 4. Testing Guidelines

-   **Framework**: `unittest` is the standard test framework.
-   **Structure**: Tests mirror the source code structure within the `test/` directory of each sub-project (e.g., `cli/test/test_adapters/...`).
-   **Protocol-Driven Tests**: A key pattern is to test against the port's protocol, not the concrete implementation. Use factory functions that return the protocol type.

    ```python
    # Example Factory
    from taew.ports.for_serializing_objects import Serialize as SerializeProtocol

    def _get_serializer() -> SerializeProtocol:
        from taew.adapters.python.pprint.for_serializing_objects import PPrint
        return PPrint()
    ```

-   **Test Discovery**: Test files must be named `test_*.py` and reside in directories containing an `__init__.py` file.
-   **Dependencies**: Prefer using in-memory (`ram`) adapters for dependencies over mocking where possible.
-   **Data-driven Tests**: Use `with self.subTest(...)` to test multiple scenarios within a single test method.

## 5. Creating a New Adapter

1.  **Location**: Create a new directory under `python/<lib>/<port>/` or a similar top-level technology folder.
2.  **Bootstrap**: Copy the contents of `project-template` into the new directory: `cp -r project-template/* <location>/`.
3.  **Configure `pyproject.toml`**:
    -   Set the `[project].name` (e.g., `taew.adapters.python.logging.for_logging`).
    -   Update the relative paths in `tool.uv.sources.taew.path`, `tool.mypy.mypy_path`, and `tool.pyright.extraPaths` to point to the `core` directory.
4.  **Implement**: Create modules that implement the port protocols.
5.  **Test**: Create a parallel test structure under the adapter's `test/` directory.

## 6. Git & GitHub Workflow

-   **Automation**: The `scripts/` directory contains shell scripts for managing GitHub issues and branches. The `gh` CLI is a prerequisite.
-   **Branching**: `bash scripts/issue-assign-branch.sh <issue-number>`
-   **New Issues**: `bash scripts/issue-new.sh -t "Title" -b "Body" -l "label"`
-   **Commits**: Follow the convention: `Implement feature X for Y (#123)`. The subject should be imperative.
-   **Checkpoints**: Use `bash scripts/checkpoint.sh "WIP: message"` for work-in-progress commits.

## 7. Special Conventions

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
