from dataclasses import dataclass

from taew.domain.configuration import PortsMapping
from taew.ports.for_browsing_code_tree import Package


@dataclass(eq=False, frozen=True, kw_only=True)
class MainBase:
    _ports_mapping: PortsMapping
    _root: Package
