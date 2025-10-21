# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses UV for dependency management and Makefiles for task automation. Each subpackage has its own Makefile with consistent targets:

### Testing and Coverage
- `make test-unit` - Run unit tests using unittest discovery
- `make coverage` - Run full test suite with coverage analysis
- `make erase-coverage` - Clean coverage data

### Static Analysis
- `make static` - Run all static analysis tools (ruff, mypy, pyright)
- `make ruff-check` - Run ruff linting (use `uvx ruff check`)
- `make ruff-format` - Run ruff formatting (use `uvx ruff format`)
- `make mypy` - Run MyPy type checking
- `make pyright` - Run Pyright type checking

### Development Workflow
Run `make all` from any subpackage directory to execute the complete pipeline (static analysis + testing with coverage).

Key directories with Makefiles:
- `core/` - Core taew library
- `cli/` - CLI adapters
- `python/argparse/for_building_command_parsers/`
- `python/inspect/for_browsing_code_tree/`
- `python/pprint/for_serializing_objects/`
- `python/ram/for_browsing_code_tree/`
- `launch_time/for_binding_interfaces/`

## Architecture

This codebase implements the **Ports & Adapters (Hexagonal Architecture)** pattern for the taew-py library. The architecture separates core business logic from external dependencies through well-defined interfaces.

### Core Components

**Domain Layer** (`core/taew/domain/`):
- `function.py` - Function invocation error handling
- `argument.py` - Argument type definitions and metadata
- `configuration.py` - Port configuration and application configuration types

**Ports Layer** (`core/taew/ports/`):
- Defines interfaces that adapters must implement
- `for_binding_interfaces.py` - Interface binding protocols
- `for_browsing_code_tree.py` - Code structure navigation protocols
- `for_building_command_parsers.py` - Command parser construction protocols
- `for_creating_class_instances.py` - Class instantiation protocols
- `for_serializing_objects.py` - Object serialization protocols
- `for_starting_programs.py` - Program execution protocols

### Adapter Structure

Adapters are organized by technology and purpose:

**CLI Adapters** (`cli/taew/adapters/cli/`):
- `for_starting_programs.py` - Main CLI entry point implementing command discovery and execution

**Python Standard Library Adapters**:
- `python/argparse/` - Command parser construction using argparse
- `python/inspect/` - Code tree browsing using Python's inspect module
- `python/pprint/` - Object serialization using pprint
- `python/ram/` - In-memory code tree representation

**Launch-time Adapters** (`launch_time/`):
- `for_binding_interfaces/` - Runtime interface binding
- `for_creating_class_instances/` - Dynamic class instantiation

### Key Design Patterns

1. **Protocol-Based Interfaces**: All ports use Python protocols for type safety
2. **Dependency Injection**: Configuration-driven adapter selection via `PortsMapping`
3. **Command Pattern**: CLI commands map to functions/classes through code tree navigation
4. **Type Safety**: Strict MyPy and Pyright configurations ensure type correctness

### Configuration System

The system uses `AppConfiguration` and `PortConfiguration` types to wire adapters:
- `PortsMapping` associates port modules with their adapter implementations
- Supports nested port configurations for composite adapters
- Optional keyword arguments for adapter customization

### CLI Command Resolution

The CLI adapter (`cli/taew/adapters/cli/for_starting_programs.py`) implements a sophisticated command resolution system:
1. Parses command arguments into a navigation path
2. Traverses the code tree using the browsing port
3. Resolves functions, classes, and callable instances
4. Builds argument parsers dynamically based on function signatures
5. Executes commands and serializes results

This architecture enables adding new technologies (databases, web frameworks, etc.) by implementing the corresponding port interfaces without modifying core logic.