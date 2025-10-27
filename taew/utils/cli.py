"""Utility functions for CLI application configuration."""

from taew.domain.configuration import PortsMapping
from taew.ports.for_browsing_code_tree import Root, Package
from taew.ports.for_configuring_adapters import Configure
from taew.utils.configure import configure as configure_adapters

from taew.adapters.launch_time.for_binding_interfaces.for_configuring_adapters import (
    Configure as BindingInterfaces,
)
from taew.adapters.cli.for_starting_programs.for_configuring_adapters import (
    Configure as CLI,
)
from taew.adapters.python.pprint.for_stringizing_objects.for_configuring_adapters import (
    Configure as PPrint,
)
from taew.adapters.python.argparse.for_building_command_parsers.for_configuring_adapters import (
    Configure as Argparse,
)
from taew.adapters.python.dataclass.for_finding_configurations.for_configuring_adapters import (
    Configure as FindConfigurations,
)
from taew.adapters.python.typing.for_building_config_ports_mapping.for_configuring_adapters import (
    Configure as BuildConfigPortsMapping,
)


def configure(
    project_root: Root,
    *adapters: Configure,
    cli_root: Package | None = None,
    variants: dict[type, str | dict[str, object]] | None = None,
) -> PortsMapping:
    """Build a complete CLI application PortsMapping.

    Configures all infrastructure adapters needed for CLI operation:
    - Interface binding for dynamic port resolution
    - CLI command execution
    - Output formatting (pprint)
    - Command-line argument parsing (argparse)
    - Configuration discovery
    - Type-variant mapping for custom serialization

    Args:
        project_root: Root of the project code tree for navigation
        *adapters: Application-specific adapter configurations
        cli_root: CLI package root (defaults to project_root["adapters"]["cli"])
        variants: Type-to-adapter variant mapping for BuildConfigPortsMapping

    Returns:
        PortsMapping: Complete configuration for CLI application

    Example:
        from taew.adapters.python.inspect.for_browsing_code_tree.root import Root
        from pathlib import Path
        from datetime import date

        project_root = Root(Path("./"))
        ports = configure(
            project_root,
            MyBusinessAdapter(),
            AnotherAdapter(config="value"),
            variants={date: {"_variant": "isoformat", "_format": "%m/%y"}},
        )
    """
    if variants is None:
        variants = {}

    if cli_root is None:
        cli_root_resolved: Package = project_root["adapters"]["cli"]  # type: ignore
    else:
        cli_root_resolved = cli_root

    # Build application ports mapping (empty dict if no adapters provided)
    app_ports: PortsMapping = configure_adapters(*adapters) if adapters else {}

    return configure_adapters(
        BindingInterfaces(_root=project_root),
        CLI(
            _root=cli_root_resolved,
            _ports_mapping=app_ports,
        ),
        PPrint(),
        Argparse(),
        FindConfigurations(),
        BuildConfigPortsMapping(_variants=variants),
    )
