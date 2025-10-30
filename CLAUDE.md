# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`taew-py` is a Python foundation library implementing the **Ports & Adapters (Hexagonal Architecture)** pattern. This document focuses on **how the system works** - the machinery that makes it function - and **how to evolve it**.

See [README.md](README.md) for architecture rationale and design principles. Git history captures how we evolved here.

## System Architecture: How The Machinery Works

### Core Layers

**Domain** ([taew/domain/](taew/domain/))
- Pure data structures with no behavior
- Configuration types: [configuration.py](taew/domain/configuration.py:1), [argument.py](taew/domain/argument.py:1), [function.py](taew/domain/function.py:1)

**Ports** ([taew/ports/](taew/ports/))
- Protocol-based interface definitions (no implementations)
- Named by capability: [for_binding_interfaces.py](taew/ports/for_binding_interfaces.py:1), [for_browsing_code_tree.py](taew/ports/for_browsing_code_tree.py:1), [for_building_command_parsers.py](taew/ports/for_building_command_parsers.py:1), [for_stringizing_objects.py](taew/ports/for_stringizing_objects.py:1), [for_marshalling_objects.py](taew/ports/for_marshalling_objects.py:1), etc.

**Adapters** ([taew/adapters/](taew/adapters/))
- [python/](taew/adapters/python/) - Python stdlib adapters (argparse, inspect, pprint, json, pickle, named_tuple, dataclass, typing, decimal, datetime, etc.)
- [cli/](taew/adapters/cli/) - CLI command execution framework
- [launch_time/](taew/adapters/launch_time/) - Stateless dependency injection via `bind()` and `create_instance()`

### System Flow: CLI → Bind → Main → Workflow Execution

This is the **critical system machinery** you must understand to evolve the codebase:

#### 1. Entry Point: CLI Bootstrap

```python
# Application entry point (e.g., bin/bz)
from taew.utils.cli import configure
from taew.ports.for_binding_interfaces import Bind

# Configure all ports with adapters
ports_mapping = configure(
    MyWorkflowAdapter(),
    AnotherAdapter(),
    root_path=Path("./"),
    cli_package="adapters.cli",
    variants={date: {"_variant": "isoformat", "_format": "%m/%y"}},
)

# Bind Main CLI handler
bind = Bind(ports_mapping)
main = bind(for_starting_programs.Main)

# Execute
main(sys.argv[1:])
```

**What happens:** `taew.utils.cli.configure()` builds a complete `PortsMapping` by combining:
- Infrastructure adapters (inspect, argparse, pprint, dataclass configurators, typing configurators)
- Application workflow adapters (your business logic)
- CLI adapter (configured with application ports)

#### 2. Dependency Injection: `bind()` Function

**Location:** [taew/adapters/launch_time/for_binding_interfaces/bind.py](taew/adapters/launch_time/for_binding_interfaces/bind.py:20)

```python
def bind(interface: Type[T], adapters: PortsMapping) -> T:
    """Bind an interface to its implementation using adapter configuration."""
```

**The machinery:**
1. **Root caching** - Gets or creates global singleton `Root` instance from `for_browsing_code_tree` configuration
2. **Port lookup** - Finds which port module the interface belongs to
3. **Adapter resolution** - Locates adapter implementation via `PortsMapping`
4. **Dependency injection** - Calls `create_instance()` to instantiate with automatic dependency resolution

**Critical:** `for_browsing_code_tree` **must** be configured in every CLI application's port mapping. This is required for code tree traversal.

#### 3. Instance Creation: `create_instance()` Function

**Location:** [taew/adapters/launch_time/for_binding_interfaces/create_instance.py](taew/adapters/launch_time/for_binding_interfaces/create_instance.py:1)

**Constructor argument resolution priority:**
1. **Configured kwargs** - Explicit values from `PortConfiguration.kwargs`
2. **Protocol-typed parameters** - Automatically inject adapters for `Protocol`-typed constructor parameters (including `Protocol` unions)
3. **Recursive resolution** - Walk dependency graph, instantiating nested dependencies

**Example:** When creating `Main`:
```python
@dataclass(eq=False, frozen=True)
class Main(MainBase):
    _create_instance: CreateInstance  # ← Injected from for_binding_interfaces port
    _build: Build                      # ← Injected from for_building_command_parsers port
    _dumps: Dumps                      # ← Injected from for_stringizing_objects port
```

The binder automatically resolves and injects all three protocol-typed dependencies.

#### 4. CLI Command Resolution: Main.__call__()

**Location:** [taew/adapters/cli/for_starting_programs/main.py](taew/adapters/cli/for_starting_programs/main.py:243)

**The machinery:**
1. **Parse command args** - Convert CLI args like `buy-ticket ABC123 Blue` into navigation path
2. **Traverse code tree** - Navigate `_cli_root` (defaults to `adapters.cli` package) following snake_case (`buy_ticket`) or PascalCase (`BuyTicket`) naming
3. **Resolve command target** - Find function or callable class (`__call__` method)
4. **Build argument parser** - Use `_build(Build)` to create argparse parser from function signature
5. **Create workflow instance** - Use `_create_instance(CreateInstance)` to instantiate workflow classes with their dependencies
6. **Execute command** - Run the resolved function/callable with parsed arguments
7. **Serialize result** - Use `_dumps(Dumps)` to serialize and print the result

**Example flow for `bz buy-ticket ABC123 Blue 2.50 ...`:**
- Navigate to `adapters.cli.buy_ticket` module
- Find `BuyTicket` class
- Instantiate `BuyTicket` using `create_instance()` - **this injects all workflow dependencies via the same binding system**
- Call `BuyTicket.__call__(car_plate="ABC123", zone="Blue", amount=2.50, ...)`
- Serialize result with `dumps(result)`

**Key insight:** Workflow classes are instantiated **at command execution time** using the **same binding configuration** that was used to create `Main`. This enables workflows to declare protocol-typed dependencies in their constructors and have them automatically injected.

#### 5. Custom Type Parsing: Complex CLI Arguments

**Problem:** How does CLI parse complex types like `PaymentCard` (a pure domain object) from strings?

**Example:** `--payment-card '{"number":"1234567890123456","cvv":"123","expiry":"12/25"}'`

**The parsing chain (automatic discovery):**

1. **Argparse Build adapter** ([build.py:122](taew/adapters/python/argparse/for_building_command_parsers/build.py:122)) - Detects `PaymentCard` parameter type in function signature
2. **Automatic configurator finder** ([build.py:178](taew/adapters/python/argparse/for_building_command_parsers/build.py:178)) - `self._find(annotation, stringizing_port)` inspects type and discovers appropriate adapter:
   - Detects `PaymentCard` is a `NamedTuple` (pure domain object)
   - Routes to [named_tuple/for_stringizing_objects](taew/adapters/python/named_tuple/for_stringizing_objects/for_configuring_adapters.py:10) adapter
3. **Named tuple configurator** - Inherits from JSON configurator, which bridges to `for_marshalling_objects` port
4. **Binding** ([build.py:185](taew/adapters/python/argparse/for_building_command_parsers/build.py:185)) - `self._bind(Loads, {stringizing_port: port_configuration})` creates bound `Loads` instance
5. **Argparse registers custom type** - Adds `type=_wrapped_converter` that calls the bound `Loads` adapter

**Chain:** `CLI string` → `Loads(for_stringizing_objects)` → `json.loads()` → `Restore(for_marshalling_objects)` → `PaymentCard(**dict)`

**Key insight:** The `_find()` function (**automatic configurator finder**) inspects the domain type annotation and **automatically discovers** the appropriate `Loads` adapter via configurators. The `variants` parameter in `configure()` is only needed when a type has **multiple marshalling possibilities** (e.g., date as ISO string vs timestamp vs tuple) to disambiguate which variant to use.

### Configurator Pattern: Default Adapter Configuration

**Every adapter package** (except `launch_time`) provides a `for_configuring_adapters.py` module with a `Configure` class.

**Purpose:** Convert high-level type information into `PortConfigurationDict` for binding.

**Key configurators:**

- **Base:** [dataclass/for_configuring_adapters.py](taew/adapters/python/dataclass/for_configuring_adapters.py:1) - Provides `_configure_item()` method that inspects type annotations and discovers appropriate adapters
- **JSON:** [json/for_stringizing_objects/for_configuring_adapters.py](taew/adapters/python/json/for_stringizing_objects/for_configuring_adapters.py:14) - Bridges stringizing to marshalling via `_nested_ports()`
- **Named tuple:** [named_tuple/for_stringizing_objects/for_configuring_adapters.py](taew/adapters/python/named_tuple/for_stringizing_objects/for_configuring_adapters.py:10) - Inherits JSON configurator for automatic JSON→NamedTuple parsing
- **Argparse:** [argparse/for_building_command_parsers/for_configuring_adapters.py](taew/adapters/python/argparse/for_building_command_parsers/for_configuring_adapters.py:9) - Simple passthrough (complex type discovery happens at parse time)

**Usage:**
```python
from taew.utils.configure import configure

ports = configure(
    PPrint(),           # Uses Configure() → default pprint configuration
    Argparse(),         # Uses Configure() → default argparse configuration
    MyAdapter(x=123),   # Uses Configure(x=123) → custom configuration
)
```

Configurators enable **reasonable defaults** while allowing **manual configuration** when needed.

## Development Workflows

### Setup Environment

```bash
# Create and activate virtual environment
uv venv && source .venv/bin/activate

# Install dependencies and run full verification
make
```

### Make Targets

- `make` (or `make all`) - Complete pipeline: sync dependencies + static analysis + tests with coverage
- `make sync` - Install/update dependencies with uv
- `make static` - Run ruff, mypy, and pyright
- `make coverage` - Run tests with coverage analysis
- `make test-unit` - Run unit tests only
- `make ruff-check` - Ruff linting
- `make ruff-format` - Ruff formatting
- `make mypy` - MyPy type checking
- `make pyright` - Pyright type checking

### Slash Commands for Issue Management

#### `/issue-new <label> "<title>" ["<body>"]`

Create GitHub issue with branch.

**Labels:** `bug`, `documentation`, `enhancement`

**Example:** `/issue-new enhancement "Add dataclass marshalling adapter" "Support nested dataclass serialization"`

**Creates:**
- GitHub issue assigned to @me
- Branch: `<issue-number>-<slugified-title>`
- Pushes and switches to new branch

#### `/issue-close [build] ["Custom commit message"]`

Close issue workflow.

**Usage:**
- `/issue-close` - Skip build, auto-generate commit, auto-bump version
- `/issue-close build` - Run `make` before committing
- `/issue-close "Custom message"` - Skip build, custom commit
- `/issue-close --major` - Bump major version (breaking changes)
- `/issue-close --no-bump` - Skip version bump

**Version bumping (automatic from issue label):**
- `enhancement` → **minor** bump (2.1.1 → 2.2.0)
- `bug` → **patch** bump (2.1.1 → 2.1.2)
- `documentation` → **no bump**

**Updates:** `pyproject.toml` and `taew/__init__.py`

**When to update CLAUDE.md during `/issue-close`:**
- ✅ **DO update** if change introduces new architectural patterns affecting future development
- ✅ **DO update** if change alters developer workflows or system machinery
- ✅ **DO update** if change introduces new critical constraints or requirements
- ❌ **SKIP update** for routine bug fixes or implementation details
- ❌ **SKIP update** for documentation-only changes (update AGENTS.md instead if needed)

**Workflow:**
1. Extracts issue number from branch (`<num>-slug`)
2. Bumps version (if applicable)
3. Commits all changes
4. Pushes and creates PR
5. Merges PR and deletes branch
6. Switches to main
7. Closes issue

## Testing Guidelines

**Write tests against port protocols, not implementations:**

```python
from taew.ports.for_stringizing_objects import Dumps as DumpsProtocol

def _get_serializer() -> DumpsProtocol:
    from taew.adapters.python.pprint.for_stringizing_objects import Dumps
    return Dumps()

class TestSerialization(unittest.TestCase):
    def test_serialize_dict(self):
        dumps = _get_serializer()
        result = dumps({"key": "value"})
        self.assertIn("key", result)
```

This ensures adapters are truly interchangeable.

**For launch_time tests:** Use `clear_root_cache()` for test isolation:

```python
from taew.adapters.launch_time.for_binding_interfaces._imp import clear_root_cache

def tearDown(self):
    clear_root_cache()
```

## Code Quality Standards

- **Python 3.14+** with full type annotation coverage
- **Zero errors** from mypy and pyright
- **100% test coverage** for new features (where feasible)
- **Ruff formatting** for consistent style
- Tests written against protocols, not implementations

## Critical Constraints & Known Issues

### Requirements

1. **`for_browsing_code_tree` is mandatory** - All CLI applications must configure this port in their `PortsMapping`. Without it, `bind()` cannot create the `Root` singleton for code tree navigation.

2. **Root singleton caching** - `Root` instance is cached globally for performance. Use `clear_root_cache()` between tests for isolation.

3. **CLI package structure** - CLI commands must live under `adapters.cli` (or custom package specified in `cli_package` parameter). Naming conventions:
   - snake_case for modules/functions: `buy_ticket.py` or `buy_ticket` function
   - PascalCase for classes: `BuyTicket` class with `__call__` method

### Known Gaps

1. **Type variant disambiguation** - When a datatype has multiple marshalling possibilities (variants), explicit `variants` parameter in `configure()` is required. For example:
   - `date`/`datetime` can marshal as ISO string (with format), timestamp (float), or tuple
   - `variants={date: {"_variant": "isoformat", "_format": "%m/%y"}}` specifies which variant to use
   - Without variants mapping, system cannot resolve ambiguity between multiple valid adapters

2. **Configurator evolution** - Issue #23 explored improvements to configurator-based adapter discovery, but implementation is still evolving.

## Key Files for System Evolution

**Core binding machinery:**
- [taew/adapters/launch_time/for_binding_interfaces/bind.py](taew/adapters/launch_time/for_binding_interfaces/bind.py:1)
- [taew/adapters/launch_time/for_binding_interfaces/create_instance.py](taew/adapters/launch_time/for_binding_interfaces/create_instance.py:1)
- [taew/adapters/launch_time/for_binding_interfaces/_imp.py](taew/adapters/launch_time/for_binding_interfaces/_imp.py:1)

**CLI execution:**
- [taew/adapters/cli/for_starting_programs/main.py](taew/adapters/cli/for_starting_programs/main.py:1)
- [taew/adapters/cli/for_starting_programs/_common.py](taew/adapters/cli/for_starting_programs/_common.py:1)

**Configuration:**
- [taew/utils/cli.py](taew/utils/cli.py:1) - CLI application bootstrap
- [taew/utils/configure.py](taew/utils/configure.py:1) - Adapter configuration utilities
- [taew/domain/configuration.py](taew/domain/configuration.py:1) - Configuration data structures

**Configurator pattern:**
- [taew/adapters/python/dataclass/for_configuring_adapters.py](taew/adapters/python/dataclass/for_configuring_adapters.py:1) - Base configurator with type inspection
- [taew/adapters/python/json/for_stringizing_objects/for_configuring_adapters.py](taew/adapters/python/json/for_stringizing_objects/for_configuring_adapters.py:1) - JSON with marshalling bridge
