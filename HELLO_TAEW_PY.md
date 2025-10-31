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

## Prompt 5: Generate Initial Architecture Documentation

```
Generate CLAUDE.md file describing the hello-taew-py application architecture and critical information for further evolution. Include:
- Application purpose and structure
- The three-layer architecture (ports/workflows/adapters)
- How dependency injection works through configuration
- How CLI commands are auto-discovered
- Guidelines for adding new functionality
- Key patterns and conventions to follow
```

## Prompt 6: Add Template Repository Pattern

```
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
```

## Prompt 7: Extract Base Class and Add Logging

```
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
```

## Prompt 8: Update Architecture Documentation

```
Update CLAUDE.md to document the enhanced architecture including:
- Domain layer: GreetingTemplate type alias (string.Template) and its purpose
- Ports: Template repository and logging protocols
- Workflows: Base class pattern with shared dependencies (_common.py)  and Template Method pattern
- Adapters: RAM repository pattern and logging adapter configuration
- Configuration: Template population using string.Template and logging setup
- Template pattern benefits: Separation of message format from business logic
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
