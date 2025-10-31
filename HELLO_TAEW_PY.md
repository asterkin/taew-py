# Hello taew-py - Step-by-Step Setup Guide

This document contains a series of prompts to send to Claude CLI one by one to build a "Hello World" application using the taew-py framework.

## Prompt 1: Initial Project Setup

```
Look at https://github.com/asterkin/taew-py/blob/main/README.md User Guide section and perform the following:
1. Initialize uv project titled "hello-taew-py" "Hello World level application built with taew-py foundation library"
2. Add dependency on taew-py from GitHub as shown in Installation section
3. Create configuration.py using the Minimal Configuration example
4. Create bin/say executable using the CLI Entry Point Shim example
5. Create empty adapters/cli packages
6. Execute uv ./bin/say --help and observe you get correct help with no commands yet configured
```

## Prompt 2: Add Hello CLI Command

```
Add hello.py to adapters/cli with:
def hello(name: str) -> str: return f'Hello {name}'
Provide pydoc string to it.
Run say --help and observe new commands help shows up
Run say hello taew-py and observe correct output
```

## Prompt 3: Implement Full Architecture with Ports and Workflows

```
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
```

## Prompt 4: Add Bye Functionality

```
Add Bye function protocol to ports/for_greetings.py, create workflows/for_greetings/bye.py workflow implementation, and create adapters/cli/bye.py CLI adapter. Run say --help and say bye taew-py to verify.
```

## Prompt 5: Generate Architecture Documentation

```
Generate CLAUDE.md file describing the hello-taew-py application architecture and critical information for further evolution. Include:
- Application purpose and structure
- The three-layer architecture (ports/workflows/adapters)
- How dependency injection works through configuration
- How CLI commands are auto-discovered
- Guidelines for adding new functionality
- Key patterns and conventions to follow
```

## Expected Project Structure

```
hello-taew-py/
├── ports/
│   └── for_greetings.py          # Hello and Bye protocols
├── workflows/
│   └── for_greetings/
│       ├── __init__.py
│       ├── for_configuring_adapters.py
│       ├── hello.py              # Hello workflow implementation
│       └── bye.py                # Bye workflow implementation
├── adapters/
│   └── cli/
│       ├── __init__.py
│       ├── hello.py              # Hello CLI adapter
│       └── bye.py                # Bye CLI adapter
├── bin/
│   └── say                       # Executable shim file
├── configuration.py              # Dependency injection wiring
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
