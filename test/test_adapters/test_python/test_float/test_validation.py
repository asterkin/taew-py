import unittest
from io import BytesIO
from pathlib import Path

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestFloatValidation(unittest.TestCase):
    def _get_configure(
        self, width: int = 8, byte_order: str = "big"
    ) -> ConfigureProtocol:
        from taew.adapters.python.float.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_width=width, _byte_order=byte_order)  # type: ignore[arg-type]

    def _bind(self, cfg: ConfigureProtocol) -> tuple[WriteProtocol, ReadProtocol]:
        from taew.adapters.python.inspect.for_browsing_code_tree.root import (
            Root as InspectRoot,
        )
        from taew.adapters.launch_time.for_binding_interfaces.main import Bind

        ports = cfg()
        root = InspectRoot(Path("."))
        bind = Bind(root)
        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)
        return write, read

    def test_write_non_float_raises_type_error(self) -> None:
        cfg = self._get_configure(8, "big")
        write, _ = self._bind(cfg)
        with self.assertRaises(TypeError):
            write("not-a-float", BytesIO())  # type: ignore[arg-type]

    def test_read_insufficient_data_raises_value_error(self) -> None:
        cfg = self._get_configure(8, "big")
        _, read = self._bind(cfg)

        # Provide fewer bytes than required (4 < 8)
        stream = BytesIO(b"\x00\x00\x00\x00")
        with self.assertRaises(ValueError):
            read(stream)


if __name__ == "__main__":
    unittest.main()
