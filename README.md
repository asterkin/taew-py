# taew-py

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-linux-blue.svg)](https://www.kernel.org/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Ports & Adapters foundation library for Python applications**

`taew-py` is a Python foundation library that supports rapid development of evolvable MVPs without premature technology lock-in. By implementing the Ports & Adapters (Hexagonal Architecture) pattern, it enables you to build applications where core business logic remains independent of external technologies and frameworks.

The name **taew** comes from the Elvish word for "socket" - a [programmable port](https://www.elfdict.com/w/taew) that adapts to different needs.

## The Problem

When building MVPs, developers face a dilemma:
- **Move fast** by coupling directly to specific technologies (databases, frameworks, cloud providers)
- **Move carefully** by building extensive abstractions upfront

The first approach leads to **technology lock-in** that becomes increasingly painful to change. The second creates **upfront complexity** that slows initial development.

## The Solution

`taew-py` provides a third path: **write business logic against protocol-based ports or ABCs, then plug in adapters as needed**. This enables:

- **Rapid prototyping** with simple adapters (in-memory, standard library)
- **Gradual evolution** by swapping adapters without changing core logic
- **Technology freedom** through clean separation of concerns
- **Type safety** via Python protocols and strict type checking

Start with Python standard library adapters (this repository), then add technology-specific adapters (AWS, databases, web frameworks) from separate repositories as your needs evolve.

## Architecture Rationale

The `taew-py` library organizes code into three fundamental layers:

**Domain Data Structures**
- Pure data classes and types
- No behavior or logic - just data representation
- Foundation for all operations across the system

**Ports**
- Interfaces describing operations on domain structures
- Defined as Protocols (preferred) or ABCs when inheritance is needed
- No implementation - only contracts
- A **port** is a group of related interfaces bound to the same technology concern (e.g., read/write operations, send/receive operations)

**Adapters**
- Concrete implementations of ports built on specific technologies
- Bridge between abstract ports and real-world tools (databases, APIs, file systems, etc.)
- Each adapter targets a specific technology stack

### Core Components

**Domain Layer** (`taew/domain/`)
- Pure domain data structures
- Configuration types for port and application setup

**Ports Layer** (`taew/ports/`)
- Protocol-based or ABC-based interface definitions
- Examples: binding interfaces, browsing code trees, building parsers, serializing objects

**Adapters Layer** (`taew/adapters/`)
- Python standard library-based implementations
- CLI adapters for command-line interface support
- Launch-time adapters for dependency injection and instantiation

**Utils** (`taew/utils/`)
- Minimal common utilities - kept as small as possible

### Configuration-Driven Wiring

Adapters are selected at runtime through Python data structures (`AppConfiguration` and `PortsMapping`):

```python
from taew.domain.configuration import AppConfiguration, PortConfiguration

config = AppConfiguration(
    ports={
        ports.for_serializing_objects: PortConfiguration(
            adapter_module="taew.adapters.python.pprint.for_serializing_objects"
        ),
        ports.for_browsing_code_tree: PortConfiguration(
            adapter_module="taew.adapters.python.inspect.for_browsing_code_tree"
        ),
    }
)
```

Configuration is encoded in Python data structures for maximum flexibility. Helper `Configure` classes are provided for all `taew` adapters to enable automatic generation when needed.

This design enables:
- **Zero code changes** when swapping implementations
- **Testing flexibility** using lightweight adapters (e.g., in-memory vs. database)
- **Gradual migration** from simple to sophisticated technologies

## Key Design Principles

### Application Layer Separation

`taew-py` promotes clean architecture through strict import boundaries:

1. **Application Domain** - No `taew` imports
   - Pure domain data structures and business logic
   - Completely independent of the framework

2. **Application Ports** - No `taew` imports (only application domain)
   - Interface definitions using Protocols or ABCs
   - May reference domain data structures

3. **Application Workflows** - No specific adapters or `taew` imports
   - Orchestrates domain logic through port interfaces
   - Only depends on application domain and ports

4. **Application Adapters** - `taew` imports allowed
   - Customizations of generic `taew` adapters
   - Implements application port interfaces

5. **Application Configuration** - `taew` imports allowed
   - Wires adapters to ports
   - Python data structures for maximum flexibility
   - Helper `Configure` classes provided for all `taew` adapters

### Framework Philosophy

- **Not Opinionated** - `taew` does not enforce any specific interpretation of Ports & Adapters
- **Good Practices Made Easy** - Aims to make sound architectural patterns straightforward to apply
- **Standard Library First** - Prefers Python stdlib interfaces (collections, protocols) whenever possible; in many ways, `taew-py` extends them for Ports & Adapters development
- **Type Safety** - Python 3.14+ with full utilization of strong type annotations
- **AI-Friendly from Day One** - Once domain structures and ports are defined (can be brainstormed with AI), developing specific technology adapters becomes a straightforward process that's easy and safe to delegate completely to AI agents
- **CLI First MVP** - close to zero code conversion of application workflows to CLI commands

## Sample Application

See [bz-taew-py](https://github.com/asterkin/bz-taew-py) - a complete CLI application for parking zone payment validation demonstrating real-world usage of taew-py's ports and adapters architecture.

### Evolvable Applications

Start with simple adapters, evolve as needed:

1. **Prototype** - Use in-memory adapters for quick validation
2. **MVP** - Switch to SQLite or local file storage
3. **Scale** - Migrate to cloud databases without changing business logic
4. **Optimize** - Add caching layers or specialized storage

Each transition requires only adapter changes, not core logic rewrites.

## Technology-Specific Adapters

While this repository contains Python standard library adapters, technology-specific adapters are developed in separate repositories:

- Cloud adapters (Buckets, Functions, etc.) - e.g. `taew-adapters-aws`
- 3rd Party Database adapters (PostgreSQL, MySQL, MongoDB) - e.g.`taew-adapters-pg`
- Web framework adapters (FastAPI, Flask, Django) - `taew-adapters-flask`

This separation enables:
- **Minimal dependencies** - Only include what you need
- **Independent evolution** - Adapters update on their own schedules
- **Technology-specific testing** - Each adapter suite tests against real services

## User Guide

### Installation

taew-py requires Python 3.14+ and is currently distributed via GitHub. We recommend using `uv` for dependency management.

#### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Add taew-py to your project

```bash
# Initialize a new project
uv init my-app
cd my-app

# Add taew-py as a dependency
uv add "taew @ git+https://github.com/asterkin/taew-py.git@main"
```

#### Configure in pyproject.toml

```toml
[project]
name = "my-app"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "taew",
]

[tool.uv.sources]
taew = { git = "https://github.com/asterkin/taew-py.git", branch = "main" }
```

### Quick Start

A typical taew-py application follows this structure:

```
my-app/
├── domain/              # Pure business data structures
├── ports/               # Protocol interfaces for your capabilities
├── workflows/           # Business logic orchestrating ports
├── adapters/            # Port implementations
│   ├── cli/             # CLI commands (auto-discovered)
│   ├── ram/             # In-memory adapters (for prototyping)
│   └── <technology>/    # Technology-specific adapters
├── configuration.py     # Dependency injection wiring
├── bin/
│   └── my-app           # CLI entry point
└── pyproject.toml
```

### Basic Example

**1. Define your domain** (`domain/greeting.py`):

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Greeting:
    name: str
    message: str
```

**2. Define your ports** (`ports/for_storing_greetings.py`):

```python
from typing import Protocol
from domain.greeting import Greeting

class Save(Protocol):
    def __call__(self, greeting: Greeting) -> None: ...

class Load(Protocol):
    def __call__(self, name: str) -> Greeting | None: ...
```

**3. Create workflow** (`workflows/greet.py`):

```python
from dataclasses import dataclass
from domain.greeting import Greeting
from ports.for_storing_greetings import Save

@dataclass(frozen=True)
class Greet:
    _save: Save

    def __call__(self, name: str) -> str:
        greeting = Greeting(name=name, message=f"Hello, {name}!")
        self._save(greeting)
        return greeting.message
```

**4. Implement adapter** (`adapters/ram/for_storing_greetings/`):

```python
# adapters/ram/for_storing_greetings/save.py
from dataclasses import dataclass
from domain.greeting import Greeting

@dataclass(frozen=True)
class Save:
    _storage: dict[str, Greeting]

    def __call__(self, greeting: Greeting) -> None:
        self._storage[greeting.name] = greeting

# adapters/ram/for_storing_greetings/for_configuring_adapters.py
from taew.domain.configuration import PortConfiguration, PortConfigurationDict
from taew.ports import for_storing_greetings

class Configure:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __call__(self) -> PortConfigurationDict:
        storage: dict = {}
        return {
            for_storing_greetings: PortConfiguration(
                adapter_module="adapters.ram.for_storing_greetings",
                kwargs={"_storage": storage}
            )
        }
```

**5. Create CLI command** (`adapters/cli/greet.py`):

```python
# CLI commands are auto-discovered - just create the function/class
from workflows.greet import Greet

# This becomes: my-app greet <name>
# taew-py automatically injects Greet's dependencies
```

**6. Configure and wire** (`configuration.py`):

```python
from pathlib import Path
from taew.utils.cli import configure
from adapters.ram.for_storing_greetings.for_configuring_adapters import (
    Configure as Greetings,
)
from workflows.greet.for_configuring_adapters import Configure as GreetWorkflow

adapters = configure(
    Greetings(),
    GreetWorkflow(),
    root_path=Path("./"),
    cli_package="adapters.cli",
)
```

**7. Create entry point** (`bin/my-app`):

```python
#!/usr/bin/env python3
import sys
from taew.ports.for_starting_programs import Main
from taew.adapters.launch_time.for_binding_interfaces import bind
from configuration import adapters

def main() -> None:
    _main = bind(Main, adapters=adapters)
    _main(sys.argv)

if __name__ == "__main__":
    main()
```

**8. Run your application:**

```bash
chmod +x bin/my-app
./bin/my-app greet Alice
# Output: Hello, Alice!
```

### Real-World Example

See [bz-taew-py](https://github.com/asterkin/bz-taew-py) for a complete application demonstrating:
- Complex domain models (parking tickets, payment cards, zones)
- Multiple workflows (car drivers, parking inspectors)
- Various adapters (RAM, directory-based storage, CLI)
- Configuration with variants (date formatting)
- Full test suite with 100% coverage

### Next Steps

- Study [bz-taew-py](https://github.com/asterkin/bz-taew-py) for real-world patterns
- Read [CLAUDE.md](CLAUDE.md) for system architecture details
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for AI-native development workflow
- Explore adapter implementations in `taew/adapters/python/`

## Project Structure

```
taew-py/
├── taew/                    # Core library
│   ├── domain/              # Pure data structures
│   │   ├── configuration.py # Port and adapter configuration types
│   │   ├── argument.py      # Function argument metadata
│   │   └── function.py      # Function metadata structures
│   ├── ports/               # Protocol-based interfaces
│   │   ├── for_binding_interfaces.py
│   │   ├── for_browsing_code_tree.py
│   │   ├── for_building_command_parsers.py
│   │   ├── for_stringizing_objects.py
│   │   ├── for_marshalling_objects.py
│   │   └── ...              # Additional port definitions
│   ├── adapters/            # Concrete implementations
│   │   ├── python/          # Python stdlib adapters
│   │   │   ├── argparse/    # CLI argument parsing
│   │   │   ├── dataclass/   # Dataclass support
│   │   │   ├── json/        # JSON serialization
│   │   │   ├── pprint/      # Pretty printing
│   │   │   ├── pickle/      # Binary serialization
│   │   │   ├── inspect/     # Code introspection
│   │   │   └── ...          # 30+ stdlib adapters
│   │   ├── cli/             # CLI command framework
│   │   │   └── for_starting_programs/
│   │   └── launch_time/     # Dependency injection
│   │       └── for_binding_interfaces/
│   └── utils/               # Minimal utilities
│       ├── cli.py           # CLI bootstrap helpers
│       └── configure.py     # Configuration utilities
├── test/                    # Test suite
├── bin/                     # Sample CLI applications
├── CLAUDE.md                # System architecture (AI context)
├── GEMINI.md                # Quick reference (AI context)
├── AGENTS.md                # Cross-agent patterns (AI context)
├── CONTRIBUTING.md          # Contribution guidelines
└── README.md                # This file
```

**Key Directories:**

- **domain/** - Pure data classes with no behavior or dependencies
- **ports/** - Protocol definitions named by capability (e.g., `for_stringizing_objects`)
- **adapters/python/** - 30+ adapters built on Python standard library (argparse, json, pickle, dataclass, inspect, typing, etc.)
- **adapters/cli/** - Command-line interface framework with automatic command discovery
- **adapters/launch_time/** - Stateless dependency injection via `bind()` and `create_instance()`
- **utils/** - Minimal helper functions for configuration and bootstrapping

See [CLAUDE.md](CLAUDE.md) for detailed system architecture and [CONTRIBUTING.md](CONTRIBUTING.md) for development guidance.

## Contributing

We welcome contributions! This project is designed as an **AI-Native** codebase, optimized for development with AI assistants like Claude Code CLI.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- AI-native development workflow
- Using Claude Code CLI slash commands (`/issue-new`, `/issue-close`)
- Code quality standards and testing requirements
- Architectural patterns and the configurator system
- Pull request process

### Quick Start for Contributors

This project follows strict type checking and formatting standards:

1. **Python 3.14+** - Full utilization of modern type annotations
2. All code must pass `mypy` and `pyright` with zero errors
3. Use `ruff` for formatting (run `make ruff-format`)
4. Maintain 100% test coverage for new features
5. Write tests against protocols, not implementations

### Development Setup

This project uses `uv` for dependency management and `make` for task automation.

```bash
# Clone the repository
git clone https://github.com/asterkin/taew-py.git
cd taew-py

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
uv sync

# Run the full verification suite
make all
```

### Common Commands

- `make all` - Run complete pipeline (static analysis + tests with coverage)
- `make static` - Run ruff, mypy, and pyright
- `make coverage` - Run tests with coverage analysis
- `make test-unit` - Run unit tests only
- `make ruff-format` - Format code

### Testing Strategy

Tests are written against port protocols, not concrete implementations:

```python
from taew.ports.for_stringizing_objects import Dumps as DumpsProtocol

def _get_stringizer() -> DumpsProtocol:
    from taew.adapters.python.pprint.for_stringizing_objects import Dumps
    return Dumps()

class TestStringizing(unittest.TestCase):
    def test_stringation_dict(self):
        dumps = _get_stringizer()
        result = dumps({"key": "value"})
        self.assertIn("key", result)
```

This approach ensures adapters are truly interchangeable.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- **Ports & Adapters Pattern**: [Alistair Cockburn's original article](https://alistair.cockburn.us/hexagonal-architecture/)
- **Focus on Core Value and Keep Cloud Infrastructure Flexible**: [Asher Sterkin's article on applying Ports & Adapters in cloud environments](https://medium.com/@asher-sterkin/focus-on-core-value-and-keep-cloud-infrastructure-flexible-with-ports-adapters-af79c5fa1e56)
- **Dependency Inversion Principle**: Part of SOLID principles
- **Protocol-based programming in Python**: [PEP 544](https://peps.python.org/pep-0544/)
