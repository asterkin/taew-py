import pickle
import base64
from ._described_mapping import NameMapping
from taew.ports.for_browsing_code_tree import Module, Package


class Root(NameMapping[Module | Package]):
    def change_root(self, new_root: str) -> "Root":
        pickled_data = base64.b64decode(new_root.encode("utf-8"))
        return Root(pickle.loads(pickled_data))
