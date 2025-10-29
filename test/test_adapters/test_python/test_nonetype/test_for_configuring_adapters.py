import unittest
from io import BytesIO
from pathlib import Path

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol


class TestNoneStreamingConfigureIntegration(unittest.TestCase):
    def _get_configure(self) -> ConfigureProtocol:
        from taew.adapters.python.nonetype.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure()

    def _bind(self, cfg: ConfigureProtocol) -> tuple[WriteProtocol, ReadProtocol]:
        # Configure for_browsing_code_tree
        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import Configure as BrowseCodeTree
        browsing_config = BrowseCodeTree(_root_path=Path("./"))()
        ports.update(browsing_config)

        write: WriteProtocol = bind(WriteProtocol, ports)
        read: ReadProtocol = bind(ReadProtocol, ports)
        return write, read

    def test_round_trip_none(self) -> None:
        cfg = self._get_configure()
        write, read = self._bind(cfg)

        stream = BytesIO()
        write(None, stream)
        stream.seek(0)
        restored = read(stream)
        self.assertIs(restored, None)

    def test_write_non_none_raises(self) -> None:
        cfg = self._get_configure()
        write, _ = self._bind(cfg)
        with self.assertRaises(TypeError):
            write("not-none", BytesIO())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
