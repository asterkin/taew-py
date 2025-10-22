from ._described_mapping import DescribedMapping
from taew.ports.for_browsing_code_tree import (
    Function,
    Class,
    Module,
    Package as PackageProtocol,
)


class Package(DescribedMapping[Function | Class | Module | PackageProtocol]):
    def __init__(
        self,
        description: str,
        items: dict[str, Function | Class | Module | PackageProtocol],
        version: str,
    ) -> None:
        super().__init__(description, items)
        self._version = version

    @property
    def version(self) -> str:
        return self._version
