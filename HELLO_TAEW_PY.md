# Hello taew-py - Step-by-Step Setup Guide

This document contains a series of phases to complete with Claude CLI one by one to build a "Hello World" application using the taew-py framework. Each phase is self-contained and can be copy-pasted directly into Claude CLI.

## Prerequisites

Before starting Phase 1, ensure you have `uv` installed. If not, install it using:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For other installation methods, see: https://docs.astral.sh/uv/getting-started/installation/

## Phase 1: Initial Project Setup

```
Phase 1: Initial Project Setup

Look at https://github.com/asterkin/taew-py/blob/main/README.md User Guide section and perform the following:
1. Initialize uv project titled "hello-taew-py" "Greeting application built with taew-py foundation library". Do not create git.
2. Remove the auto-generated main.py file after initialization
3. Add dependency on taew-py from GitHub as shown in Installation section
4. Create configuration.py using the Minimal Configuration example
5. Create bin/say executable using the CLI Entry Point Shim example
   NOTE: The shim's main() function must accept cmd_args parameter for testability
6. Create adapters and adapters/cli packages (both with __init__.py files)
   In adapters/cli/__init__.py replicate the program description from step 1 as a docstring
   and the version from pyproject.toml as __version__
7. Execute uv ./bin/say --help and observe you get correct help with no commands yet configured
8. Execute uv ./bin/say --version and verify it displays the correct version
9. For each subsequent phase that adds new functionality (not documentation),
   bump the minor version in both pyproject.toml and adapters/cli/__init__.py
10. Create test/test_cli.py using TestCLI base class from https://github.com/asterkin/taew-py/blob/main/taew/utils/unittest.py
    IMPORTANT: Use simplified imports (all types re-exported from taew.utils.unittest):
    - from taew.utils.unittest import TestCLI as TestCLIBase, Result, SubTest, Test
    The default TestCLI uses multiprocessing adapter for separate process execution with full coverage.
    See https://github.com/asterkin/taew-py/blob/main/test/test_utils/test_unittest.py for RAM adapter example.
    Add test for --help and --version commands
11. Create Makefile using https://github.com/asterkin/taew-py/blob/main/Makefile as example
    IMPORTANT: Set SRC_DIR=./ (not ./adapters) to include all source files in coverage
    Add development tools to pyproject.toml [tool.uv.dev-dependencies]:
    - ruff
    - mypy
    - pyright
    Add coverage configuration to pyproject.toml:
    [tool.coverage.run]
    source = ["."]
    parallel = true
    concurrency = ["multiprocessing"]
    Run: source .venv/bin/activate (or equivalent for your shell)
    Run: make to verify setup (runs static checks and tests with coverage)
```

## Phase 2: Add Hello CLI Command

```
Phase 2: Add Hello CLI Command

1. Add hello.py to adapters/cli with:
   def hello(name: str) -> str: return f'Hello {name}'
2. Provide pydoc string to it
3. Run say --help and observe new command help shows up
4. Run say hello taew-py and observe correct output
5. Update test/test_cli.py to add tests for the hello command
6. Run make to verify all tests pass
7. Bump minor version in both pyproject.toml and adapters/cli/__init__.py
```

## Phase 3: Implement Full Architecture with Ports and Workflows

```
Phase 3: Implement Full Architecture with Ports and Workflows

1. Add ports/for_greetings.py with Hello function protocol accepting name (same signature as for hello cli adapter)
2. Add workflows/for_greetings package with __init__.py, for_configuring_adapters.py, and hello.py module
3. In workflows/for_greetings/for_configuring_adapters.py use the Workflow Configurator Template from README.md User Guide section
4. In workflows/for_greetings/hello.py create Hello class implementing the greeting logic
5. Modify configuration.py to:
   from taew.utils.cli import configure
   from workflows.for_greetings.for_configuring_adapters import (
       Configure as Greetings,
   )
   adapters = configure(Greetings())
6. Modify adapters/cli/hello.py to:
   from ports.for_greetings import Hello
   __all__ = ["Hello"]
7. Run say hello taew-py and observe correct results
8. Update test/test_cli.py to verify the hello command still works with new architecture
9. Run make to verify all tests pass
10. Bump minor version in both pyproject.toml and adapters/cli/__init__.py
```

## Phase 4: Add Bye Functionality

```
Phase 4: Add Bye Functionality

1. Add Bye function protocol to ports/for_greetings.py
2. Create workflows/for_greetings/bye.py workflow implementation
3. Create adapters/cli/bye.py CLI adapter
4. Run say --help and say bye taew-py to verify
5. Update test/test_cli.py to add tests for the bye command
6. Run make to verify all tests pass
7. Bump minor version in both pyproject.toml and adapters/cli/__init__.py
```

## Phase 5: Generate Initial Architecture Documentation

```
Phase 5: Generate Initial Architecture Documentation

Generate CLAUDE.md file describing the hello-taew-py application architecture and critical information for further evolution. Include:
- Application purpose and structure
- The three-layer architecture (ports/workflows/adapters)
- How dependency injection works through configuration
- How CLI commands are auto-discovered
- Guidelines for adding new functionality
- Key patterns and conventions to follow

Note: This is a documentation phase - do not bump version.
```

## Phase 6: Add Template Repository Pattern

```
Phase 6: Add Template Repository Pattern

Reference https://github.com/asterkin/bz-taew-py for adapter patterns.

1. Import Template from string module
2. Add GreetingTemplate type alias (Template) to domain/greeting.py
3. Create ports/for_storing_templates.py with GreetingTemplatesRepository protocol implementing __getitem__(name: str) -> GreetingTemplate
4. Update workflows/for_greetings/hello.py and bye.py to accept self._templates: GreetingTemplatesRepository
5. Create adapters/ram/for_storing_templates following the pattern from https://github.com/asterkin/bz-taew-py/tree/main/adapters/ram/for_storing_rates
6. Update configuration.py to populate Templates adapter with Template instances:
   - "hello": Template("Hello $name!")
   - "bye": Template("Goodbye $name!")
   (Note: Template uses $name for substitution, formatted with template.substitute(name=name))
7. Update Hello and Bye implementations to retrieve and format templates:
   template = self._templates["hello"]
   return template.substitute(name=name)
8. Run say hello taew-py and say bye taew-py to verify template-based output
9. Update test/test_cli.py to verify template-based output format
10. Run make to verify all tests pass
11. Bump minor version in both pyproject.toml and adapters/cli/__init__.py
```

## Phase 7: Extract Base Class and Add Logging

```
Phase 7: Extract Base Class and Add Logging

Reference https://github.com/asterkin/bz-taew-py/tree/main/workflows for logging patterns.

1. Create workflows/for_greetings/_common.py with GreetingBase dataclass
2. Move self._templates: GreetingTemplatesRepository to GreetingBase
3. Import Logger from taew.ports.for_logging and add self._logger: Logger to GreetingBase
4. Add _format(self, name: str, greeting: str) -> str method to GreetingBase that:
   - Logs: self._logger.info(f"Processing {greeting} for: {name}")
   - Retrieves template: template = self._templates[greeting.lower()]
   - Substitutes and returns: return template.substitute(name=name)
5. Update Hello and Bye to inherit from GreetingBase
6. Simplify Hello.__call__ to: return self._format(name, "hello")
7. Simplify Bye.__call__ to: return self._format(name, "bye")
8. Add logging adapter to configuration.py:
   - Import: from taew.adapters.python.logging.for_logging.for_configuring_adapters import Configure as Logging
   - Import: from taew.domain.logging import INFO
   - Add to configure(): Logging(_name="hello-taew-py", _level=INFO)
9. Run say hello taew-py and say bye taew-py and observe logged output
10. Update test/test_cli.py to verify commands still work with logging (output unchanged)
11. Run make to verify all tests pass
12. Bump minor version in both pyproject.toml and adapters/cli/__init__.py
```

## Phase 8: Update Architecture Documentation

```
Phase 8: Update Architecture Documentation

Update CLAUDE.md to document the enhanced architecture including:
- Domain layer: GreetingTemplate type alias (string.Template) and its purpose
- Ports: Template repository and logging protocols
- Workflows: Base class pattern with shared dependencies (_common.py) and Template Method pattern
- Adapters: RAM repository pattern and logging adapter configuration
- Configuration: Template population using string.Template and logging setup
- Template pattern benefits: Separation of message format from business logic

Note: This is a documentation phase - do not bump version.
```

## Expected Project Structure

```
hello-taew-py/
├── domain/
│   └── greeting.py               # GreetingTemplate type alias
├── ports/
│   ├── for_greetings.py          # Hello and Bye protocols
│   └── for_storing_templates.py  # GreetingTemplatesRepository protocol
├── workflows/
│   └── for_greetings/
│       ├── __init__.py
│       ├── for_configuring_adapters.py
│       ├── _common.py            # GreetingBase with shared dependencies
│       ├── hello.py              # Hello workflow implementation
│       └── bye.py                # Bye workflow implementation
├── adapters/
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── hello.py              # Hello CLI adapter
│   │   └── bye.py                # Bye CLI adapter
│   └── ram/
│       └── for_storing_templates/ # Template repository (auto-generated)
├── test/
│   └── test_cli.py               # CLI integration tests
├── bin/
│   └── say                       # Executable shim file
├── configuration.py              # Dependency injection wiring
├── Makefile                      # Build automation (static checks + tests)
├── CLAUDE.md                     # Architecture documentation
└── pyproject.toml
```

## Key Architecture Concepts

The taew-py framework enforces clean separation of concerns:

- **Ports** (`ports/`) - Protocol interfaces defining contracts
- **Workflows** (`workflows/`) - Business logic implementations
- **Adapters** (`adapters/`) - Technology-specific implementations (CLI, storage, etc.)
- **Configuration** (`configuration.py`) - Dependency injection wiring

The framework automatically discovers CLI commands from `adapters/cli/` and wires them to workflow implementations through the configuration.
