# Contributing to taew-py

Thank you for your interest in contributing to **taew-py**! This is a foundational library for building Python applications using the Ports & Adapters (Hexagonal Architecture) pattern.

## AI-Native Development Philosophy

**This is an AI-Native project.** taew-py is designed from the ground up to be developed with AI assistance and is optimized for AI-driven workflows.

### Working with AI Actors

We strongly recommend using an **AI Actor CLI or plugin** when contributing to this project.

**Primary tool used in this project:**
- **[Claude Code CLI](https://claude.ai/code)** - Primary development tool for implementing features, refactoring, maintaining architecture, and executing the complete development workflow

**Other AI tools that can be used:**
- **[Codex CLI](https://github.com/microsoft/vscode-codex)** - Can be consulted for architectural brainstorming and design decisions
- **[Gemini](https://gemini.google.com/)** - Alternative AI assistant with context file [GEMINI.md](./GEMINI.md)
- **GitHub Copilot** - Useful for code completion and boilerplate generation

Contributors are welcome to use these or other AI assistants. We encourage contributions that evolve AI assistant configurations or update context files ([CLAUDE.md](./CLAUDE.md), [GEMINI.md](./GEMINI.md), [AGENTS.md](./AGENTS.md)) with your experiences.

These tools understand the project architecture and can help you:
- Navigate the hexagonal architecture and binding machinery
- Implement new adapters following established patterns
- Understand the configurator pattern and port-adapter relationships
- Maintain consistency with architectural principles
- Run tests and static analysis
- Follow the project's coding conventions

### Why AI-Native?

The taew framework uses:
- **Protocol-based ports** for clear interface boundaries
- **Declarative configuration** via `PortsMapping` and `AppConfiguration`
- **Convention over configuration** to minimize boilerplate
- **Comprehensive documentation** in [CLAUDE.md](./CLAUDE.md) for AI comprehension
- **Stateless dependency injection** at launch time

This design makes the codebase exceptionally well-suited for AI-assisted development. See [CLAUDE.md](./CLAUDE.md) for detailed system architecture and operational knowledge.

## How to Contribute

### 1. Types of Contributions Welcome

We welcome:
- **Bug reports** - Clear descriptions with reproduction steps
- **Bug fixes** - Pull requests that fix identified issues
- **Documentation improvements** - Clarifications, examples, corrections
- **Feature proposals** - Open an issue first to discuss
- **New adapters** - Additional implementations of existing ports (especially technology-specific adapters in separate repos)
- **Test improvements** - Enhanced coverage, better test data
- **Configurator enhancements** - Improvements to the configurator pattern

We appreciate your patience as we review contributions carefully.

### 2. Contribution Process

#### Step 1: Fork and Clone
```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/taew-py.git
cd taew-py
```

#### Step 2: Set Up Development Environment
```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Sync dependencies
make sync

# Run complete verification pipeline
make all
```

#### Step 3: Create a Feature Branch

**For Claude Code CLI users:**

You can use the `/issue-new` slash command for coordinated creation of a GitHub issue and corresponding branch:

```bash
/issue-new <label> "<title>" ["<description>"]
```

Example:
```bash
/issue-new enhancement "Add datetime marshalling adapter" "Support ISO format and timestamp variants"
```

This automatically creates the issue, creates a branch, and switches to it.

**For other users:**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

#### Step 4: Make Your Changes

- Follow the architectural patterns documented in [CLAUDE.md](./CLAUDE.md)
- Understand the binding machinery and configurator pattern
- Write tests against protocols, not implementations
- Update documentation as needed
- Run `make all` before committing to ensure quality

#### Step 5: Commit Your Changes
```bash
git add .
git commit -m "Brief description of your changes"
```

**Commit message guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues when applicable ("Fix #123: Description")

#### Step 6: Push and Create Pull Request

**For certified contributors using Claude Code CLI:**

Certified contributors can use the `/issue-close` slash command to automatically commit, push, create a pull request, merge the branch, and close the issue:

```bash
/issue-close           # Skip build, auto-bump version based on issue label
/issue-close build     # Run make all before committing
```

This streamlined workflow is available only to contributors with merge permissions.

**For other contributors:**

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Reference to related issues
- Test results (if applicable)

### 3. Pull Request Review Process

**Important: Merge Restrictions**

This repository has **branch protection rules** enabled:
- ✅ Pull requests are required for all changes to `main`
- ✅ At least 1 approval is required before merging
- ✅ Direct pushes to `main` are blocked
- ✅ Force pushes are blocked
- ✅ Only repository maintainers can merge PRs

**What this means for contributors:**
- You can fork, branch, and create pull requests
- **You cannot merge your own PRs**
- The repository owner will review and merge approved changes
- This ensures code quality and architectural consistency

### 4. Code Quality Standards

All contributions must pass:

#### Static Analysis
```bash
make static           # Runs ruff, mypy, and pyright
make ruff-check       # Linting
make ruff-format      # Code formatting
make mypy             # Type checking (mypy)
make pyright          # Type checking (pyright)
```

#### Tests
```bash
make test-unit        # Unit tests
make coverage         # Test coverage report
```

#### Complete Pipeline
```bash
make all              # Runs sync, static, and coverage
```

**Requirements:**
- Python 3.14+
- All tests must pass
- Type checking must pass (strict mode for both mypy and pyright)
- Code must be formatted with ruff
- New features require tests written against protocols
- Aim for 100% test coverage for new features

### 5. Architectural Guidelines

This project follows **Ports & Adapters (Hexagonal Architecture)**:

#### Core Concepts to Understand

Before contributing, familiarize yourself with:
1. **Three layers**: Domain (pure data), Ports (protocols), Adapters (implementations)
2. **Binding machinery**: `bind()` and `create_instance()` functions
3. **Configurator pattern**: Every adapter has `for_configuring_adapters.py`
4. **CLI execution flow**: Entry point → bind → Main → command resolution → workflow execution
5. **Root caching**: `for_browsing_code_tree` is mandatory for CLI applications

See [CLAUDE.md](./CLAUDE.md) for comprehensive system architecture documentation.

#### Adding New Ports
1. Create new port module in `taew/ports/for_<capability>.py`
2. Define Protocol-based interfaces (or ABCs if inheritance needed)
3. Document the port's purpose and usage patterns
4. Add tests that verify any adapter can implement the port

#### Adding New Adapters
1. Create adapter directory structure: `taew/adapters/<technology>/<port_name>/`
2. Implement the port protocol(s)
3. Create `for_configuring_adapters.py` with `Configure` class
4. Add comprehensive tests against the port protocol
5. Document any technology-specific requirements

#### Adding New Configurators
1. Study existing configurators in `taew/adapters/python/*/for_configuring_adapters.py`
2. Understand `_configure_item()` and `_nested_ports()` patterns
3. Test configurator discovers correct adapters for type annotations
4. Document variant disambiguation if type has multiple marshalling possibilities

#### Extending Core Binding
Changes to binding machinery require extra scrutiny:
- `taew/adapters/launch_time/for_binding_interfaces/` - Core DI system
- Must maintain backward compatibility
- Requires comprehensive test coverage
- Document changes thoroughly in [CLAUDE.md](./CLAUDE.md)

### 6. Testing Strategy

**Critical**: Tests must be written against protocols, not implementations:

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

**For launch_time tests**: Use `clear_root_cache()` for test isolation.

### 7. Documentation Standards

- Keep [CLAUDE.md](./CLAUDE.md) up-to-date with system-level changes
- Update [GEMINI.md](./GEMINI.md) and [AGENTS.md](./AGENTS.md) as needed
- Update [README.md](./README.md) for user-facing changes
- Include docstrings for public APIs
- Update type hints when modifying signatures
- Document critical constraints and known gaps

### 8. Communication

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas
- **Email**: For security concerns, email [asher.sterkin@gmail.com](mailto:asher.sterkin@gmail.com)

### 9. Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [asher.sterkin@gmail.com](mailto:asher.sterkin@gmail.com).

## Development Tips

### Using Claude Code CLI Effectively

When using Claude Code CLI:

1. **Share context**: The AI automatically reads [CLAUDE.md](./CLAUDE.md) for architectural understanding
2. **Use slash commands**: `/issue-new` and `/issue-close` for streamlined workflow
3. **Use make targets**: Run `make all` frequently to catch issues early
4. **Ask for guidance**: "Explain the binding machinery" or "Show me how configurators work"
5. **Verify patterns**: Have the AI check that new code follows existing patterns
6. **Generate tests**: AI can help create protocol-based test cases
7. **Refactor safely**: AI maintains type safety during refactoring

### Using Other AI Assistants

If using Codex, Gemini, or other AI tools:
1. Point the AI to [CLAUDE.md](./CLAUDE.md) or [GEMINI.md](./GEMINI.md)
2. Consider creating a custom context file for your AI tool
3. Share your experience by updating [AGENTS.md](./AGENTS.md)

### Project Structure Quick Reference

```
taew-py/
├── taew/
│   ├── domain/              # Pure data structures (configuration types)
│   ├── ports/               # Protocol interfaces (contracts)
│   ├── adapters/            # Implementations
│   │   ├── python/          # Python stdlib adapters
│   │   ├── cli/             # CLI framework
│   │   └── launch_time/     # Dependency injection
│   └── utils/               # Minimal utilities
├── test/                    # Test suite
├── bin/                     # Sample CLI applications
├── CLAUDE.md                # System architecture (AI context)
├── GEMINI.md                # Quick reference (AI context)
└── AGENTS.md                # Cross-agent patterns
```

### Common Tasks

```bash
# Run specific test file
python -m pytest test/test_specific.py -v

# Check types only
make mypy
make pyright

# Format code
make ruff-format

# Run tests with coverage
make coverage

# Full verification pipeline
make all
```

### Understanding the Codebase

Key files to study:
1. [taew/adapters/launch_time/for_binding_interfaces/bind.py](taew/adapters/launch_time/for_binding_interfaces/bind.py) - Dependency injection
2. [taew/adapters/cli/for_starting_programs/main.py](taew/adapters/cli/for_starting_programs/main.py) - CLI execution flow
3. [taew/adapters/python/dataclass/for_configuring_adapters.py](taew/adapters/python/dataclass/for_configuring_adapters.py) - Configurator pattern base
4. [taew/utils/cli.py](taew/utils/cli.py) - CLI bootstrap

## Questions?

If you have questions about contributing:
1. Check [CLAUDE.md](./CLAUDE.md) for architectural guidance
2. Review existing code for patterns
3. Open a GitHub discussion
4. Consult your AI coding assistant (Claude Code, Codex, Gemini, etc.)
5. Email the maintainer

Thank you for contributing to taew-py!
