from ._described_mapping import DescribedMapping
from taew.ports.for_browsing_code_tree import Function, Class


class Module(DescribedMapping[Function | Class]):
    pass
