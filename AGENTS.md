# Repository Guidelines

## Project Structure & Module Organization
- Core library: `core/taew/...` (ports, domain, utils).
- Adapters (by technology/capability): `python/<lib>/<capability>/taew/adapters/python/...`.
- CLI adapter: `cli/taew/...` with entry-points and tests in `cli/test/...`.
- Launch-time DI: `launch_time/for_binding_interfaces/...`.
- Example app and workflows: `bluezone-py/...` with CLI script in `bluezone-py/bin/bz` and tests in `bluezone-py/test/...`.
- Each subproject keeps its own `pyproject.toml`, `Makefile`, and `test/` folder.

## Build, Test, and Development Commands
- Root: `scripts/build-all.sh` builds every subproject with a `Makefile`.
- Per subproject (e.g., `core`, `cli`, or a `python/...` adapter):
  - Activate venv first: `source .venv/bin/activate` (required when running `make` directly).
  - `make all`: run static checks and tests.
  - `make coverage`: run unit tests with coverage (parallel combine + report).
  - `make static`: run `ruff` (check+format), `mypy`, and `pyright`.
  - Example: `cd core && source .venv/bin/activate && make coverage`.
- Environment: use `uv sync` to create/populate `.venv`; deactivate with `deactivate` when done.

## Coding Style & Naming Conventions
- Python ≥ 3.13 with strict typing (`mypy`, `pyright`).
- Imports: order by ascending line length.
- Typing rules: use `|` for unions; prefer `Optional[T]` over `T | None`; use built-in generics (`list[T]`, `dict[K, V]`, `tuple[T, ...]`, `set[T]`).
- Formatting/Linting: `ruff` (check + format via `make static`).
- Packages live under `taew`; files/modules use `snake_case`. Adapters follow `taew.adapters.python.<module>.<capability>`.

Example
```python
import json
import unittest
from pathlib import Path

from taew.ports.for_storing_data import Store as StoreProtocol

def process_data(items: list[dict[str, str | int]], config: Optional[dict[str, Any]] = None) -> tuple[str, ...]:
    ...
```

## Testing Guidelines
- Framework: `unittest`; fully type-annotate test methods/helpers.
- Structure: mirror adapter paths under `test/test_adapters/...`; keep `__init__.py` in each test folder for discovery.
- Discovery: files named `test_*.py` under `test/`.
- Protocol imports: import from ports and alias as `XProtocol` (e.g., `from taew.ports.for_storing_data import Store as StoreProtocol`).
- Factory pattern: use helpers like `_get_store_adapter() -> StoreProtocol` that build real adapters/workflows to validate protocol conformance.
- Dependencies: prefer RAM adapters over mocks when available.
- Data-driven: use `subTest` with table-driven cases for similar scenarios.
- Coverage: `make coverage` to run, combine, and report.

## New Adapter Sub-Project
- Location: `python/<lib>/<port>/` (stdlib), `python/ram/<port>/` (RAM/testing), or `<tech>/<port>/` (tech‑neutral).
- Bootstrap: `cp -r project-template/* <location>/` then customize `pyproject.toml`.
  - `[project].name`: `taew.adapters.<tech>.<lib?>.<port>` and description.
  - Point to core: set `tool.uv.sources.taew.path`, `tool.mypy.mypy_path`, `tool.pyright.extraPaths` to the core relative path:
    - Python adapters/RAM: `../../../core`; tech‑neutral: `../../core`.
- Namespaces: no `__init__.py` in `taew`, `taew.adapters`, or `taew.adapters.<tech>`; add `__init__.py` only in the final package dir.
- Implementation: modules per protocol (snake_case), classes match protocol (`Transform`, `Restore`), prefer `@dataclass(frozen=True, eq=False)`, shared bits in `_common.py`.
- Tests: mirror structure under `test/test_adapters/test_<tech>/test_<lib?>/test_<port>/`, include `__init__.py` in each test folder; use factory helpers returning `XProtocol`.
- Env & verify: `uv venv && source .venv/bin/activate && uv sync && make`.

## Commit & Pull Request Guidelines
- Commits: concise, imperative subject; optional scope; reference issues with `(#123)`.
  - Example: `Implement decimal serialization adapter with tests (#115)`.
- PRs: include a clear description, linked issues, rationale, and test evidence (coverage output or CLI logs). Keep changes scoped to one concern.

## Security & Configuration Tips
- Python/toolchain via `uv`: pin with `uv python pin <version>` or run `scripts/upgrade.sh 3.13.x` across subprojects.
- Subprojects may use `.env` to extend `PATH`/`PYTHONPATH` when running `make`.
- Avoid cross-project imports outside declared `extraPaths` in `pyproject.toml` to keep adapters modular.

## GitHub Automation (Codex CLI)
- Prereqs: authenticated `gh` CLI, `origin` remote set.
- Branch naming: `<issue-number>-<kebab-title>` (lowercase, hyphens).
- Scripts (in `./scripts`):
  - Create new issue + branch: `bash scripts/issue-new.sh -t "Feature: add logging" -b "AC..." -l feature`
  - Assign existing issue + branch: `bash scripts/issue-assign-branch.sh 123`
- Close issue (build, PR, merge): `bash scripts/issue-close.sh -i 123` (add `--skip-build` to skip checks). This runs `scripts/build-all.sh` by default.
  - Local checkpoint (no push): `bash scripts/checkpoint.sh "WIP: refactor adapter factory"`
