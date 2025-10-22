# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`taew-py` is a Python foundation library implementing the **Ports & Adapters (Hexagonal Architecture)** pattern. See [README.md](README.md) for architecture rationale, design principles, and usage patterns.

This document focuses on **development workflows**, **project structure**, and **Claude Code-specific commands**.

## Development Commands

This project uses `uv` for dependency management and `make` for task automation:

### Quick Start
```bash
# Setup environment
uv venv && source .venv/bin/activate

# Install dependencies and run full verification
make
```

### Common Make Targets
- `make` (or `make all`) - Run complete pipeline (sync dependencies + static analysis + tests with coverage)
- `make sync` - Install/update dependencies with uv
- `make static` - Run ruff, mypy, and pyright
- `make coverage` - Run tests with coverage analysis
- `make test-unit` - Run unit tests only
- `make ruff-check` - Check code with ruff linting
- `make ruff-format` - Format code with ruff
- `make mypy` - Run MyPy type checking
- `make pyright` - Run Pyright type checking
- `make erase-coverage` - Clean coverage data

### Project Structure
All code lives in a single `taew/` directory organized by layer:
- `taew/domain/` - Pure domain data structures and configuration types
- `taew/ports/` - Protocol-based interface definitions
- `taew/adapters/` - Technology-specific implementations
  - `taew/adapters/cli/` - CLI entry point and command execution
  - `taew/adapters/python/` - Python standard library adapters (argparse, inspect, pprint, json, etc.)
  - `taew/adapters/launch_time/` - Runtime binding and instantiation
- `taew/utils/` - Minimal shared utilities

A single top-level `Makefile` handles all verification tasks.

## Architecture Overview

See [README.md](README.md#architecture-rationale) for comprehensive architecture documentation. Key points:

### Layer Organization

**Domain** (`taew/domain/`)
- Pure data structures with no behavior
- Configuration types for port and application setup
- Examples: `argument.py`, `configuration.py`, `function.py`

**Ports** (`taew/ports/`)
- Protocol-based interface definitions (no implementations)
- Named by capability: `for_binding_interfaces.py`, `for_browsing_code_tree.py`, `for_building_command_parsers.py`, etc.
- Each port groups related operations for a specific concern

**Adapters** (`taew/adapters/`)
- Concrete implementations of ports using specific technologies
- Python stdlib adapters: argparse, inspect, pprint, json, pickle, etc.
- CLI adapter: Command execution framework
- Launch-time adapters: Runtime binding and instantiation

### Key Patterns

1. **Protocol-Based Interfaces** - Type-safe contracts without inheritance
2. **Configuration-Driven Wiring** - Select adapters via `AppConfiguration` and `PortsMapping`
3. **Import Boundaries** - Application code imports no `taew` modules; only configuration and adapters do
4. **Type Safety** - Strict mypy/pyright checking with zero errors

### CLI Command Resolution

The CLI adapter implements dynamic command resolution:
1. Parse command arguments into navigation path
2. Traverse code tree to resolve functions/classes
3. Build argument parsers from function signatures
4. Execute commands and serialize results

This enables zero-code conversion of Python functions to CLI commands.

## Claude Code Slash Commands

This repository includes custom slash commands for issue management workflows:

### `/issue-new`
Create a new GitHub issue with label, title, and optional body, then create and push a branch.

**Usage:**
```
/issue-new <label> "<title>" ["<body>"]
```

**Labels:** `bug`, `documentation`, `enhancement`

**Examples:**
- `/issue-new enhancement "Add Redis adapter" "Support pub/sub patterns"`
- `/issue-new bug "Fix serialization error"`
- `/issue-new documentation "Update API documentation"`

**Outcome:**
- Creates GitHub issue assigned to @me
- Creates branch: `<issue-number>-<slugified-title>`
- Pushes branch to origin
- Switches to new branch

### `/issue-close`
Close current issue by committing changes, creating PR, merging, and closing the issue.

**Usage:**
```
/issue-close                              # Skip build, auto-generate commit message
/issue-close build                        # Run make (static + tests) before committing
/issue-close "Custom commit message"      # Skip build, custom message
/issue-close build "Custom message"       # Run make with custom message
```

**Behavior:**
- Extracts issue number from branch name (format: `<num>-slug`)
- Commits all changes (auto-generated or custom message)
- Creates and merges PR
- Closes issue
- Switches to main branch
- Deletes feature branch

**Default:** Skips build for speed. Use `build` flag to run full verification (assumes venv is activated, runs `make`).

## Testing Guidelines

Write tests against port protocols, not implementations:

```python
from taew.ports.for_serializing_objects import Dumps as DumpsProtocol

def _get_serializer() -> DumpsProtocol:
    from taew.adapters.python.pprint.for_serializing_objects import Dumps
    return Dumps()

class TestSerialization(unittest.TestCase):
    def test_serialize_dict(self):
        dumps = _get_serializer()
        result = dumps({"key": "value"})
        self.assertIn("key", result)
```

This ensures adapters are truly interchangeable.

## Code Quality Standards

- **Python 3.14+** with full type annotation coverage
- **Zero errors** from mypy and pyright
- **100% test coverage** for new features
- **Ruff formatting** for consistent style
- Tests written against protocols, not implementations