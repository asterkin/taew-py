import unittest
from datetime import date
from typing import NamedTuple, Any

from taew.domain.configuration import PortConfigurationDict
from taew.adapters.python.typing.for_building_config_ports_mapping.build import Build
from taew.ports import (
    for_configuring_adapters,
    for_stringizing_objects,
    for_streaming_objects,
)


class SampleTuple(NamedTuple):
    first: int
    second: str


class TestBuildConfigPortsMapping(unittest.TestCase):
    def test_build_ports_mapping(self) -> None:
        self.maxDiff = None
        cases: list[dict[str, Any]] = [
            {
                "name": "primitive",
                "variants": {},
                "arg": int,
                "port": for_stringizing_objects,
                "expected_base": int,
                "expected_config": PortConfigurationDict(
                    adapter="int.for_stringizing_objects",
                    kwargs={},
                ),
            },
            {
                "name": "generic_list",
                "variants": {},
                "arg": list[int],
                "port": for_streaming_objects,
                "expected_base": list,
                "expected_config": PortConfigurationDict(
                    adapter="list.for_streaming_objects",
                    kwargs={"_args": (int,)},
                ),
            },
            {
                "name": "named_tuple",
                "variants": {},
                "arg": SampleTuple,
                "port": for_stringizing_objects,
                "expected_base": SampleTuple,
                "expected_config": PortConfigurationDict(
                    adapter="named_tuple.for_stringizing_objects",
                    kwargs={"_args": (SampleTuple,)},
                ),
            },
            {
                "name": "string_variant",
                "variants": {date: "isoformat"},
                "arg": date,
                "port": for_stringizing_objects,
                "expected_base": date,
                "expected_config": PortConfigurationDict(
                    adapter="date.isoformat.for_stringizing_objects",
                    kwargs={"_variants": {date: "isoformat"}},
                ),
            },
            {
                "name": "dict_variant",
                "variants": {date: {"_variant": "isoformat", "_format": "%m/%d"}},
                "arg": date,
                "port": for_streaming_objects,
                "expected_base": date,
                "expected_config": PortConfigurationDict(
                    adapter="date.isoformat.for_streaming_objects",
                    kwargs={
                        "_format": "%m/%d",
                        "_variants": {
                            date: {"_variant": "isoformat", "_format": "%m/%d"}
                        },
                    },
                ),
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                builder = Build(_variants=case["variants"])
                base, ports = builder(case["arg"], case["port"])
                self.assertIs(base, case["expected_base"])
                self.assertEqual(len(ports), 1)
                actual_config = ports[for_configuring_adapters]
                expected_config = case["expected_config"]
                self.assertEqual(actual_config.__dict__, expected_config.__dict__)

    def test_invalid_variant_specification(self) -> None:
        builder = Build(_variants={int: 123})  # type: ignore
        with self.assertRaises(TypeError):
            builder(int, for_stringizing_objects)


if __name__ == "__main__":
    unittest.main()
