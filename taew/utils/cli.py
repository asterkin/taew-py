"""Utility functions for CLI application configuration."""

from pathlib import Path
from taew.domain.configuration import PortsMapping
from taew.ports.for_configuring_adapters import Configure
from taew.utils.configure import configure as configure_adapters

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
from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
    Configure as BrowseCodeTree,
)


def configure(
    *adapters: Configure,
    root_path: Path = Path("./"),
    cli_package: str = "adapters.cli",
    variants: dict[type, str | dict[str, object]] | None = None,
) -> PortsMapping:
    """Build a complete CLI application PortsMapping.

    Configures all infrastructure adapters needed for CLI operation:
    - Code tree browsing (inspect)
    - CLI command execution
    - Output formatting (pprint)
    - Command-line argument parsing (argparse)
    - Configuration discovery
    - Type-variant mapping for custom serialization

    Args:
        *adapters: Application-specific adapter configurations
        root_path: Root directory path for code tree navigation (defaults to "./")
        cli_package: CLI package path relative to root (defaults to "adapters.cli")
        variants: Type-to-adapter variant mapping for BuildConfigPortsMapping

    Returns:
        PortsMapping: Complete configuration for CLI application

    Example:
        from pathlib import Path
        from datetime import date

        ports = configure(
            MyBusinessAdapter(),
            AnotherAdapter(config="value"),
            root_path=Path("./"),
            variants={date: {"_variant": "isoformat", "_format": "%m/%y"}},
        )
    """
    if variants is None:
        variants = {}

    # Build application ports mapping (empty dict if no adapters provided)
    app_ports: PortsMapping = configure_adapters(*adapters) if adapters else {}

    return configure_adapters(
        BrowseCodeTree(_root_path=root_path),
        CLI(
            _ports_mapping=app_ports,
            _cli_package=cli_package,
        ),
        PPrint(),
        Argparse(),
        FindConfigurations(),
        BuildConfigPortsMapping(_variants=variants),
    )
