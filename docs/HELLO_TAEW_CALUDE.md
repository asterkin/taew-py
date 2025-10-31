# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the hello-taew-py application.

## Overview

**hello-taew-py** is a Hello World level demonstration application built with the [taew-py](https://github.com/asterkin/taew-py) foundation library. It showcases the **Ports & Adapters (Hexagonal Architecture)** pattern for building evolvable CLI applications.

The application implements simple greeting functionality (`hello` and `bye` commands) using a clean three-layer architecture that separates business logic from infrastructure concerns.

## Application Purpose

This is a learning and reference application that demonstrates:
- How to structure a taew-py application following Ports & Adapters principles
- Configuration-driven dependency injection
- Automatic CLI command discovery
- Clean separation between domain logic, ports, and adapters
- Repository pattern for data storage (RAM-based templates)
- Base class pattern with shared dependencies
- Template Method pattern for code reuse
- Cross-cutting concerns (logging) via dependency injection
- Python's `string.Template` for safe string substitution
- How to extend the application with new functionality

## Project Structure

```
hello-taew-py/
├── domain/                             # Pure data types (no behavior)
│   └── greeting.py                     # GreetingTemplate type alias
├── ports/                              # Protocol definitions (interfaces)
│   ├── for_greetings.py               # Greeting protocols (Hello, Bye)
│   └── for_storing_templates.py       # Template repository protocol
├── workflows/                          # Business logic layer
│   └── for_greetings/
│       ├── __init__.py
│       ├── for_configuring_adapters.py # Workflow configurator
│       ├── _common.py                  # Base class with shared dependencies
│       ├── hello.py                    # Hello workflow implementation
│       └── bye.py                      # Bye workflow implementation
├── adapters/                           # Infrastructure layer
│   ├── cli/                            # CLI command adapters
│   │   ├── __init__.py
│   │   ├── hello.py                    # Exposes Hello protocol
│   │   └── bye.py                      # Exposes Bye protocol
│   └── ram/                            # In-memory storage adapters
│       └── for_storing_templates/      # RAM template repository
│           ├── __init__.py
│           ├── greeting_templates_repository.py  # Type alias
│           └── for_configuring_adapters.py       # Configurator
├── configuration.py                    # Dependency injection wiring
├── bin/
│   └── say                             # CLI entry point executable
└── pyproject.toml                      # Project metadata and dependencies
```

## Four-Layer Architecture

### Layer 0: Domain (domain/)

**Purpose:** Define pure data types and type aliases without any behavior or logic.

**Example:** [domain/greeting.py](domain/greeting.py:1)

```python
from string import Template
from typing import TypeAlias

GreetingTemplate: TypeAlias = Template
"""A template string for formatting greetings."""
```

**Key characteristics:**
- Pure data structures - no behavior, no methods
- Type aliases for clarity and maintainability
- NO imports from taew, ports, workflows, or adapters
- Foundation types used across all layers
- In this app: Uses Python's `string.Template` for safe string substitution with `$variable` syntax

**Why string.Template?**
- Safe substitution - no code execution risks
- Clear syntax: `$name` for variables
- Handles missing variables gracefully
- Part of Python standard library
- Better than format strings for user-controlled templates

### Layer 1: Ports (ports/)

**Purpose:** Define protocol-based interfaces that describe *what* the application can do, without specifying *how*.

**Example:** [ports/for_greetings.py](ports/for_greetings.py:1)

```python
from typing import Protocol

class Hello(Protocol):
    """Protocol for greeting someone by name."""

    def __call__(self, name: str) -> str:
        """Greet someone by name."""
        ...

class Bye(Protocol):
    """Protocol for saying goodbye to someone by name."""

    def __call__(self, name: str) -> str:
        """Say goodbye to someone by name."""
        ...
```

**Template Repository Port:** [ports/for_storing_templates.py](ports/for_storing_templates.py:1)

```python
from typing import Protocol
from domain.greeting import GreetingTemplate

class GreetingTemplatesRepository(Protocol):
    """Port for storing and retrieving greeting templates."""

    def __getitem__(self, key: str, /) -> GreetingTemplate:
        """Retrieve a greeting template by its identifier."""
        ...
```

**Key characteristics:**
- Pure protocol definitions using `typing.Protocol`
- No implementation details
- CAN import from domain layer (for type definitions)
- NO imports from taew, workflows, or adapters
- Defines the contract between workflows and adapters
- Repository protocols enable swappable storage implementations

### Layer 2: Workflows (workflows/)

**Purpose:** Implement business logic by providing concrete implementations of port protocols.

**Base Class Pattern:** [workflows/for_greetings/_common.py](workflows/for_greetings/_common.py:1)

```python
from dataclasses import dataclass
from ports.for_storing_templates import GreetingTemplatesRepository
from taew.ports.for_logging import Logger

@dataclass(eq=False, frozen=True)
class GreetingBase:
    """Base class for greeting workflows with shared dependencies."""

    _templates: GreetingTemplatesRepository
    _logger: Logger

    def _format(self, name: str, greeting: str) -> str:
        """Template Method - shared formatting logic."""
        self._logger.info(f"Processing {greeting} for: {name}")
        template = self._templates[greeting.lower()]
        return template.substitute(name=name)
```

**Concrete Workflow:** [workflows/for_greetings/hello.py](workflows/for_greetings/hello.py:1)

```python
from dataclasses import dataclass
from workflows.for_greetings._common import GreetingBase

@dataclass(eq=False, frozen=True)
class Hello(GreetingBase):
    """Workflow for greeting someone by name."""

    def __call__(self, name: str) -> str:
        return self._format(name, "hello")
```

**Key characteristics:**
- Implemented as frozen dataclasses
- Can inherit from base classes to share dependencies and logic
- Base classes use **Template Method pattern** - define algorithm skeleton, subclasses provide details
- Contains actual business logic
- Dependencies declared via protocol-typed constructor parameters (auto-injected)
- No knowledge of infrastructure (CLI, databases, etc.)
- Logging is a cross-cutting concern injected as a dependency

**Configurator pattern:** [workflows/for_greetings/for_configuring_adapters.py](workflows/for_greetings/for_configuring_adapters.py:1)

```python
from dataclasses import dataclass
from taew.adapters.python.dataclass.for_configuring_adapters import (
    Configure as ConfigureBase,
)

@dataclass(eq=False, frozen=True)
class Configure(ConfigureBase):
    _root_marker: str = "workflows"
    _ports: str = "ports"

    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)
```

This configurator enables automatic discovery and binding of workflow implementations to their corresponding ports.

### Layer 3: Adapters (adapters/)

**Purpose:** Bridge between the outside world and the application's internal ports.

**CLI Adapter Example:** [adapters/cli/hello.py](adapters/cli/hello.py:1)

```python
from ports.for_greetings import Hello

__all__ = ["Hello"]
```

**RAM Repository Adapter:** [adapters/ram/for_storing_templates/greeting_templates_repository.py](adapters/ram/for_storing_templates/greeting_templates_repository.py:1)

```python
from typing import TypeAlias
from domain.greeting import GreetingTemplate
from taew.adapters.python.ram.for_storing_data.data_repository import DataRepository

GreetingTemplatesRepository: TypeAlias = DataRepository[str, GreetingTemplate]
```

**RAM Repository Configurator:** [adapters/ram/for_storing_templates/for_configuring_adapters.py](adapters/ram/for_storing_templates/for_configuring_adapters.py:1)

```python
from dataclasses import dataclass
from taew.adapters.python.ram.for_storing_data.for_configuring_adapters import (
    Configure as ConfigureBase,
)
from domain.greeting import GreetingTemplate

@dataclass(eq=False, frozen=True)
class _Configure(ConfigureBase[str, GreetingTemplate]):
    def __post_init__(self) -> None:
        object.__setattr__(self, "_package", __package__)
        object.__setattr__(self, "_file", __file__)

def Configure(**kwargs: GreetingTemplate) -> _Configure:
    """Create configurator with template data."""
    return _Configure(_values=kwargs)
```

**Key characteristics:**
- **CLI adapters:** Simply expose protocols - framework handles binding
- **RAM adapters:** In-memory storage using taew's generic `DataRepository`
- **Repository pattern:** Type aliases specialize generic repositories
- **Configurators:** Enable population of repositories at configuration time
- Adapters are technology-specific (CLI, RAM, file system, database, etc.)
- Keep adapters thin - logic belongs in workflows

## How It Works: The Complete Flow

### 1. Application Startup

**Entry point:** [bin/say](bin/say:1)

```python
#!/usr/bin/env python3

import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from taew.ports.for_starting_programs import Main
from taew.adapters.launch_time.for_binding_interfaces import bind
from configuration import adapters

def main() -> None:
    try:
        # Dynamically bind the Main interface
        _main = bind(Main, adapters=adapters)

        # Run with command line arguments
        _main(sys.argv)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Flow:**
1. Import the `adapters` configuration from configuration.py
2. Use `bind()` to resolve the `Main` CLI handler
3. Execute `main(sys.argv)` which processes command-line arguments

### 2. Dependency Injection via Configuration

**Configuration file:** [configuration.py](configuration.py:1)

```python
from taew.utils.cli import configure
from workflows.for_greetings.for_configuring_adapters import (
    Configure as Greetings,
)
from adapters.ram.for_storing_templates.for_configuring_adapters import (
    Configure as Templates,
)
from domain.greeting import GreetingTemplate
from taew.adapters.python.logging.for_logging.for_configuring_adapters import (
    Configure as Logging,
)
from taew.domain.logging import INFO

adapters = configure(
    Greetings(),
    Templates(
        hello=GreetingTemplate("Hello $name!"),
        bye=GreetingTemplate("Goodbye $name!"),
    ),
    Logging(_name="hello-taew-py", _level=INFO),
)
```

**What `configure()` does:**
1. Creates a complete `PortsMapping` by combining:
   - Infrastructure adapters (argparse, inspect, pprint, dataclass support)
   - Application workflow adapters (Greetings configurator)
   - Data storage adapters (Templates with populated data)
   - Logging adapter (configured logger)
   - CLI adapter (configured to scan `adapters.cli` package)
2. Returns a mapping that the `bind()` function uses for dependency injection

**Configuration Details:**

**Greetings() configurator:**
- Scans the `workflows/for_greetings/` package
- Discovers `hello.py` and `bye.py` implementations
- Maps them to corresponding protocols in `ports/for_greetings.py`

**Templates() configurator:**
- Populates RAM repository with greeting templates
- Uses Python's `string.Template` with `$variable` syntax
- Templates populated at configuration time (before any workflow runs)
- Key-value pairs: `hello` and `bye` map to Template objects

**Logging() configurator:**
- Configures Python's logging system
- `_name`: Logger name (appears in log output)
- `_level`: Log level (INFO, DEBUG, WARNING, ERROR)
- Injected into all workflows that declare `_logger: Logger` dependency

### 3. CLI Command Auto-Discovery

When you run `./bin/say hello taew-py`:

1. **Command parsing:** The `Main` adapter parses `["hello", "taew-py"]`
2. **Module navigation:** Navigates to `adapters.cli.hello` module
3. **Protocol discovery:** Finds `Hello` protocol exported via `__all__`
4. **Workflow binding:** Uses `bind(Hello, adapters=adapters)` to get the workflow implementation
   - Looks up `Hello` protocol in the ports mapping
   - Finds it maps to `workflows.for_greetings.hello.Hello`
   - Instantiates the workflow class using `create_instance()`
5. **Argument parsing:** Uses argparse adapter to parse `name="taew-py"`
6. **Execution:** Calls `hello_instance(name="taew-py")`
7. **Serialization:** Serializes the result `'Hello taew-py'` using the configured stringizer (pprint)

**Key insight:** The CLI adapter doesn't know or care about the implementation. It only knows about the protocol. The framework handles all the binding automatically.

### 4. The Binding Magic

The `bind()` function (from taew-py) performs stateless dependency injection:

```python
hello_workflow = bind(Hello, adapters=adapters)
# Returns an instance of workflows.for_greetings.hello.Hello
```

**How it works:**
1. Determines which port module `Hello` belongs to (`ports.for_greetings`)
2. Looks up the adapter configuration for that port in `adapters`
3. Finds `workflows.for_greetings.hello` as the implementation
4. Uses `create_instance()` to instantiate the workflow class
5. Automatically injects any protocol-typed dependencies the workflow declares

**In this app:** Workflows declare dependencies on `GreetingTemplatesRepository` and `Logger` protocols. The `bind()` function recursively resolves these dependencies:
1. Detects `Hello` workflow needs `_templates` and `_logger`
2. Binds `_templates` to RAM repository adapter (populated with templates)
3. Binds `_logger` to Python logging adapter (configured with name and level)
4. Instantiates `Hello` with both dependencies injected

## Architectural Patterns Demonstrated

### Repository Pattern

**Purpose:** Abstract data storage/retrieval behind an interface.

**Implementation:**
- **Port:** `GreetingTemplatesRepository` protocol defines `__getitem__(key: str) -> GreetingTemplate`
- **Adapter:** RAM-based implementation using taew's generic `DataRepository`
- **Configuration:** Templates populated at startup via configurator

**Benefits:**
- Business logic doesn't know WHERE templates are stored
- Easy to swap implementations (RAM → file system → database)
- Testable - use different repositories for testing vs production
- Data separation - templates live outside workflow code

**Example workflow usage:**
```python
template = self._templates["hello"]  # Could be RAM, file, or database
return template.substitute(name=name)
```

### Template Method Pattern

**Purpose:** Define algorithm skeleton in base class, let subclasses provide specific steps.

**Implementation:**
- **Base class:** `GreetingBase` defines `_format()` method with shared algorithm:
  1. Log the operation
  2. Retrieve template from repository
  3. Substitute variables and return result
- **Subclasses:** `Hello` and `Bye` just call `self._format(name, "hello")` with different parameters

**Benefits:**
- **DRY principle** - shared logic written once
- **Consistency** - all greetings follow same algorithm
- **Maintainability** - change logging/formatting in one place
- **Extensibility** - new greetings are trivial to add

**Code comparison:**

Before (duplicated logic):
```python
class Hello:
    def __call__(self, name: str) -> str:
        template = self._templates["hello"]
        return template.substitute(name=name)

class Bye:
    def __call__(self, name: str) -> str:
        template = self._templates["bye"]
        return template.substitute(name=name)
```

After (shared via Template Method):
```python
class GreetingBase:
    def _format(self, name: str, greeting: str) -> str:
        self._logger.info(f"Processing {greeting} for: {name}")
        template = self._templates[greeting.lower()]
        return template.substitute(name=name)

class Hello(GreetingBase):
    def __call__(self, name: str) -> str:
        return self._format(name, "hello")

class Bye(GreetingBase):
    def __call__(self, name: str) -> str:
        return self._format(name, "bye")
```

### Base Class Pattern with Shared Dependencies

**Purpose:** Multiple workflows need the same dependencies - declare them once.

**Implementation:**
- Base class declares shared protocol-typed dependencies
- Subclasses inherit these dependencies automatically
- Framework injects dependencies into base class fields

**Benefits:**
- No repetition of dependency declarations
- Consistent dependency access across related workflows
- Easy to add new cross-cutting concerns (just add to base class)

### Cross-Cutting Concerns via Dependency Injection

**Purpose:** Add functionality (like logging) across multiple workflows without modifying their core logic.

**Implementation:**
- Logging declared as protocol-typed dependency: `_logger: Logger`
- Framework injects configured logger at instantiation
- All workflows that need logging simply inherit from base class

**Benefits:**
- **Separation of concerns** - logging separate from business logic
- **Configurable** - change log level, format, destination at configuration time
- **Testable** - inject mock logger for testing
- **No magic** - explicit dependency declaration

### Safe String Templating

**Purpose:** Separate message format from business logic, enable safe user-controlled templates.

**Implementation:**
- Use Python's `string.Template` with `$variable` syntax
- Templates stored in repository, not hardcoded in workflows
- Safe substitution via `template.substitute(name=name)`

**Benefits:**
- **Security** - no code execution risks (vs f-strings or eval)
- **Flexibility** - templates can be changed without code changes
- **Localization-ready** - easy to add multiple language templates
- **User-controlled** - templates could come from config files or database

**Comparison:**

Hardcoded (not flexible):
```python
return f"Hello {name}!"
```

Template-based (flexible, safe):
```python
template = self._templates["hello"]  # "Hello $name!"
return template.substitute(name=name)
```

## Guidelines for Adding New Functionality

### Adding a New Command to an Existing Port

**Example:** Add a `greet` command to the greetings port

1. **Add protocol to ports/for_greetings.py:**
   ```python
   class Greet(Protocol):
       """Protocol for formal greeting."""

       def __call__(self, title: str, name: str) -> str:
           """Formally greet someone with their title."""
           ...
   ```

2. **Create workflow implementation workflows/for_greetings/greet.py:**
   ```python
   from dataclasses import dataclass

   @dataclass(eq=False, frozen=True)
   class Greet:
       """Workflow for formal greeting."""

       def __call__(self, title: str, name: str) -> str:
           return f'Good day, {title} {name}'
   ```

3. **Create CLI adapter adapters/cli/greet.py:**
   ```python
   from ports.for_greetings import Greet

   __all__ = ["Greet"]
   ```

4. **No configuration changes needed!** The existing `Greetings()` configurator automatically discovers the new workflow.

5. **Test:**
   ```bash
   ./bin/say greet --help
   ./bin/say greet Dr. Smith
   # Output: 'Good day, Dr. Smith'
   ```

### Adding a New Port/Workflow Package

**Example:** Add a `for_calculations` port for math operations

1. **Create port module ports/for_calculations.py:**
   ```python
   from typing import Protocol

   class Add(Protocol):
       """Protocol for adding two numbers."""

       def __call__(self, a: float, b: float) -> float:
           """Add two numbers."""
           ...
   ```

2. **Create workflow package structure:**
   ```
   workflows/for_calculations/
   ├── __init__.py
   ├── for_configuring_adapters.py  # Copy from for_greetings
   └── add.py
   ```

3. **Implement workflow workflows/for_calculations/add.py:**
   ```python
   from dataclasses import dataclass

   @dataclass(eq=False, frozen=True)
   class Add:
       """Workflow for adding numbers."""

       def __call__(self, a: float, b: float) -> float:
           return a + b
   ```

4. **Create CLI adapter adapters/cli/add.py:**
   ```python
   from ports.for_calculations import Add

   __all__ = ["Add"]
   ```

5. **Update configuration.py:**
   ```python
   from taew.utils.cli import configure
   from workflows.for_greetings.for_configuring_adapters import (
       Configure as Greetings,
   )
   from workflows.for_calculations.for_configuring_adapters import (
       Configure as Calculations,
   )

   adapters = configure(Greetings(), Calculations())
   ```

6. **Test:**
   ```bash
   ./bin/say add 5.0 3.0
   # Output: 8.0
   ```

### Adding Workflows with Dependencies

**Example:** A workflow that depends on another port

1. **Define dependent protocol in ports/for_formatting.py:**
   ```python
   from typing import Protocol

   class Uppercase(Protocol):
       """Protocol for converting text to uppercase."""

       def __call__(self, text: str) -> str:
           """Convert text to uppercase."""
           ...
   ```

2. **Create workflow that uses it workflows/for_greetings/shout_hello.py:**
   ```python
   from dataclasses import dataclass
   from ports.for_formatting import Uppercase

   @dataclass(eq=False, frozen=True)
   class ShoutHello:
       """Workflow that shouts a greeting."""

       _uppercase: Uppercase  # Dependency injected automatically!

       def __call__(self, name: str) -> str:
           greeting = f'Hello {name}'
           return self._uppercase(greeting)
   ```

3. **Implement the dependency workflows/for_formatting/uppercase.py:**
   ```python
   from dataclasses import dataclass

   @dataclass(eq=False, frozen=True)
   class Uppercase:
       """Workflow for uppercasing text."""

       def __call__(self, text: str) -> str:
           return text.upper()
   ```

4. **Configure both ports and create CLI adapter:**
   - Add `Formatting()` configurator to configuration.py
   - Create adapters/cli/shout_hello.py exposing the protocol

The `bind()` function will automatically:
- Detect that `ShoutHello` needs an `Uppercase` dependency
- Recursively bind and instantiate the `Uppercase` workflow
- Inject it into `ShoutHello` constructor

## Key Patterns and Conventions

### Naming Conventions

1. **Port modules:** `ports/for_<capability>.py` (e.g., `for_greetings.py`, `for_calculations.py`)
2. **Workflow packages:** `workflows/for_<capability>/` (matches port module name)
3. **Protocol names:** PascalCase, usually verbs or nouns (e.g., `Hello`, `Add`, `Format`)
4. **Workflow classes:** Same name as protocol (e.g., protocol `Hello` → class `Hello`)
5. **CLI adapters:** `adapters/cli/<command>.py` where `<command>` is snake_case of protocol name

### Architecture Rules

1. **Domain layer:**
   - Pure data types - no behavior, no methods
   - NO imports from taew, ports, workflows, or adapters
   - Only type aliases and data classes
   - Foundation types used across all layers

2. **Ports layer:**
   - NO imports from taew, workflows, or adapters
   - CAN import from domain (for type definitions)
   - Only use typing.Protocol
   - Define contracts only, no implementation

3. **Workflows layer:**
   - NO imports from adapters
   - CAN import from domain (for data types)
   - CAN import from ports (for dependency declarations)
   - CAN import from taew.ports (for framework protocols like Logger)
   - Use `@dataclass(eq=False, frozen=True)` for all workflow classes
   - Dependencies declared as protocol-typed constructor parameters
   - Can use base classes to share dependencies and logic

4. **Adapters layer:**
   - CAN import from taew, domain, and ports
   - CLI adapters: just import and export protocols
   - RAM adapters: use taew's generic `DataRepository`
   - Keep adapters thin - logic belongs in workflows

5. **Configuration:**
   - CAN import from all layers
   - One configurator per workflow package
   - One configurator per adapter that needs configuration
   - Import all configurators in configuration.py
   - Pass them to `configure()` function

### Dataclass Conventions

All workflow classes follow this pattern:

```python
from dataclasses import dataclass

@dataclass(eq=False, frozen=True)
class MyWorkflow:
    """Docstring describing the workflow."""

    # Dependencies (protocol-typed, prefixed with _)
    _dependency: SomeProtocol

    # Configuration (non-protocol types, prefixed with _)
    _setting: str = "default"

    def __call__(self, arg1: str, arg2: int) -> str:
        """The workflow's main operation."""
        # Implementation here
        ...
```

**Key points:**
- Use `eq=False, frozen=True` for all workflow dataclasses
- Prefix dependencies and internal fields with `_`
- Main operation is typically `__call__` for callable workflows
- Can have multiple methods for complex workflows

### Testing Strategy

When testing workflows with dependencies:

```python
import unittest
from string import Template
from ports.for_greetings import Hello as HelloProtocol

class MockTemplateRepository:
    """Mock template repository for testing."""
    def __getitem__(self, key: str) -> Template:
        templates = {
            "hello": Template("Hello $name!"),
            "bye": Template("Goodbye $name!")
        }
        return templates[key]

class MockLogger:
    """Mock logger for testing."""
    def info(self, msg: str) -> None:
        pass  # Or collect messages for verification

def _get_hello() -> HelloProtocol:
    from workflows.for_greetings.hello import Hello
    return Hello(
        _templates=MockTemplateRepository(),
        _logger=MockLogger()
    )

class TestGreetings(unittest.TestCase):
    def test_hello(self):
        hello = _get_hello()
        result = hello(name="World")
        self.assertEqual(result, "Hello World!")
```

**Benefits:**
- Tests against protocol interface, not implementation
- Uses mock dependencies for isolation
- No need for actual database, file system, or external services
- Easy to swap implementations later
- Follows same pattern as production code (depends on protocols)

## Common Development Tasks

### Running the Application

```bash
# Show all commands
./bin/say --help

# Get help for specific command
./bin/say hello --help

# Run a command
./bin/say hello taew-py
# Output:
# 'Hello taew-py!'
# INFO:Processing hello for: taew-py

./bin/say bye "cruel world"
# Output:
# 'Goodbye cruel world!'
# INFO:Processing bye for: cruel world
```

**Note:** Log messages are written to stderr, so they won't interfere with the actual command output (stdout).

### Using uv for Development

```bash
# Run via uv (automatically uses virtual environment)
uv run ./bin/say hello taew-py

# Install dependencies
uv sync

# Add new dependency
uv add <package-name>
```

### Debugging Tips

1. **Import errors:** Ensure `sys.path.insert(0, ...)` is correct in bin/say
2. **Command not found:** Check that CLI adapter exports protocol in `__all__`
3. **Binding errors:** Verify configurator is added to `configure()` in configuration.py
4. **Wrong implementation called:** Check workflow class name matches protocol name

### Project Evolution Checklist

When extending this application:

- [ ] Define protocol in appropriate `ports/for_*.py` module
- [ ] Create workflow implementation in `workflows/for_*/` package
- [ ] Create workflow configurator (copy from existing package)
- [ ] Create CLI adapter in `adapters/cli/` (if needed)
- [ ] Add configurator to `configuration.py`
- [ ] Test with `--help` and actual execution
- [ ] Update this CLAUDE.md if you introduce new architectural patterns

## Critical Constraints

1. **Python 3.14+ required** - Uses modern type annotations and protocols
2. **taew-py dependency** - Must be available from GitHub (see pyproject.toml)
3. **Configurator per workflow package** - Every workflow package needs `for_configuring_adapters.py`
4. **Protocol-workflow name matching** - Workflow class must have same name as protocol for auto-discovery
5. **CLI package location** - Commands must be in `adapters.cli` package (configurable but currently hardcoded)

## References

- **taew-py documentation:** [README.md](https://github.com/asterkin/taew-py/blob/main/README.md)
- **taew-py architecture:** [CLAUDE.md](https://github.com/asterkin/taew-py/blob/main/CLAUDE.md)
- **Real-world example:** [bz-taew-py](https://github.com/asterkin/bz-taew-py) - Parking zone payment validation app
- **Ports & Adapters pattern:** [Alistair Cockburn's article](https://alistair.cockburn.us/hexagonal-architecture/)

## Next Steps

This application is intentionally simple to demonstrate core concepts. To learn more:

1. **Study the taew-py library** - Understand the framework's full capabilities
2. **Explore bz-taew-py** - See a real-world application with complex domain logic
3. **Add complexity** - Try implementing workflows with dependencies, data persistence, or external integrations
4. **Experiment with adapters** - Create alternative implementations (e.g., web API instead of CLI)

The beauty of Ports & Adapters is that your business logic (workflows) remains unchanged regardless of how you expose it or what infrastructure you use.
