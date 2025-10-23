"""Utility functions for working with ports configuration."""

from functools import reduce
from operator import or_

from taew.domain.configuration import PortsMapping
from taew.ports.for_configuring_adapters import Configure


def build(*configs: Configure) -> PortsMapping:
    """Build a PortsMapping by calling and merging multiple Configure instances.

    Takes Configure instances as arguments, calls each one to get its PortsMapping,
    and merges them using the | operator (dict union).

    Args:
        *configs: Configure instances to call and merge

    Returns:
        PortsMapping: Merged configuration from all Configure instances

    Example:
        from taew.utils.ports import build
        from taew.adapters.python.logging.for_logging.for_configuring_adapters import Configure as ConfigureLogging
        from taew.adapters.python.ram.for_obtaining_current_datetime.for_configuring_adapters import Configure as ConfigureDateTime
        from taew.domain.logging import INFO

        ports = build(
            ConfigureLogging(_name="MyApp", _level=INFO),
            ConfigureDateTime(),
        )
    """
    return reduce(or_, (config() for config in configs))
