# AGENTS.md

## Orientation
- `taew-py` is the shared foundation library that turns annotated Python packages into runnable CLIs using a Ports & Adapters runtime. Everything funnels through three layers: domain types (pure data), protocol ports, and technology-specific adapters.
- The library follows the same separation it enables: pure domain types (`taew/domain`), abstract operations (`taew/ports`), technology implementations plus their configurators (`taew/adapters`), and shared helpers (`taew/utils`). This project ships adapters built on Python's standard library; third-party technology stacks should provide their own adapter packages.

## Core Systems Snapshot
- **Domain** – structural primitives such as adapter config (`taew/domain/configuration.py:1`), argument metadata (`taew/domain/argument.py:1`), and error helpers.
- **Ports** – capability protocols organised by concern (binding, code-tree browsing, CLI parsing, object (de)serialisation) in `taew/ports/`. The introspection API is defined in `taew/ports/for_browsing_code_tree.py:1`.
- **Adapters** – split by technology under `taew/adapters/`:
  - `launch_time` provides dependency injection (`taew/adapters/launch_time/for_binding_interfaces/bind.py:1`).
  - `python/...` wraps stdlib/runtime features (inspect, argparse, dataclasses, typing, pprint, json, etc.).
  - `cli/...` hosts the runnable command dispatcher (`taew/adapters/cli/for_starting_programs/main.py:26`).

## Configuration Flow
1. Each adapter exposes an immutable `Configure` dataclass that knows how to emit its `PortsMapping`. They inherit shared behaviour from `taew/adapters/python/dataclass/for_configuring_adapters.py:14`, which auto-detects adapter packages, computes project roots, and recursively short-circuits to other configurators based on type annotations.
2. Application wiring composes these with `taew/utils/configure.py:10`, which simply unions the dicts returned by each `Configure`.
3. `taew/utils/cli.py:1` assembles a full CLI stack: inspect-based code browsing, argparse command builder, pprint output formatting, type-aware configuration discovery, and the CLI runtime. It accepts additional configurators for business ports plus optional type-variant overrides.

## Code Tree Infrastructure
- The runtime treats the filesystem + import graph as navigable objects. `Root` adapters inherit from `taew/adapters/python/inspect/for_browsing_code_tree/_common.py:18`, which extends the generic folder walker in `taew/adapters/python/path/for_browsing_code_tree/folder.py:9`.
- Leaf wrappers use runtime inspection enriched with parsed docstrings: modules (`taew/adapters/python/inspect/for_browsing_code_tree/module.py:1`), classes (`taew/adapters/python/inspect/for_browsing_code_tree/class_.py:1`), and callables (`taew/adapters/python/inspect/for_browsing_code_tree/function.py:1`). These provide descriptions, argument metadata, and safe invocation.
- AST helpers (`taew/adapters/python/ast/...`) backfill docstrings and version fields when imports fail, letting the launcher reason about packages without executing arbitrary code.

## Binding & Dependency Injection
- `bind()` (`taew/adapters/launch_time/for_binding_interfaces/bind.py:1`) resolves any port protocol to an adapter instance using the configured `PortsMapping`. Internals in `_imp.py` cache the code-tree root, map interface types back to port modules, and walk the filesystem to find matching classes or callables (`taew/adapters/launch_time/for_binding_interfaces/_imp.py:40`).
- Class instantiation is selective: constructor parameters pull explicit kwargs from configuration, otherwise the binder recursively allocates interfaces (including mappings of type -> interface and tuple unions of alternatives).
- `create_class_instance()` lives in the same module and is also exposed via the port so adapters (notably the CLI) can spin up callable classes on demand.

## Type-Driven Adapter Discovery
- The typing adapter builds on standard annotations to locate the right configurator. `Build` analyses an annotation, chooses an adapter namespace, applies variant rules, and emits the tiny `PortsMapping` required to bind the configurator interface (`taew/adapters/python/typing/for_building_config_ports_mapping/build.py:11`).
- `Find` (`taew/adapters/python/dataclass/for_finding_configurations/find.py:11`) then binds `Configure` via `Bind`, executes it, and returns the resolved port configuration for the requested capability. This is how higher-level tooling (like the CLI argument builder) avoids hard-coded type maps.

## CLI Front Door
- `MainBase` wires a discovered CLI package to the inspected root (`taew/adapters/cli/for_starting_programs/_common.py:8`), ensuring commands are resolved relative to `adapters/cli`.
- The main adapter (`taew/adapters/cli/for_starting_programs/main.py:26`) walks CLI arguments, searches for functions or callable classes that match each token (snake-case or PascalCase), and delegates to the argparse builder.
- `Builder` (`taew/adapters/python/argparse/for_building_command_parsers/build.py:24`) inspects function signatures from the browsing port, generates argparse parsers, and for non-native types asks `Find` + `Bind` to supply a `Loads` adapter. Successful commands print via the configured stringiser.

## String & Naming Utilities
- Helper conversions like `pascal_to_snake` / `snake_to_pascal` live in `taew/utils/strings.py:4` and are reused throughout binding and CLI routing.

## Notes For Design Sessions
- Root caching currently lives in a module-level global (`taew/adapters/launch_time/for_binding_interfaces/_imp.py:40`); revisit if we need multiple isolated adapter graphs.
- Variants cascade through `_variants` dictionaries in the dataclass configurator (`taew/adapters/python/dataclass/for_configuring_adapters.py:109`) and typing builder (`taew/adapters/python/typing/for_building_config_ports_mapping/build.py:52`). Align future adapter families with this contract.
- CLI discovery assumes packages expose public functions or callable classes; extending to coroutine commands or more complex argument coercion will likely mean enhancing the code-tree wrappers and the argparse builder in tandem.
