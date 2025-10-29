"""Unit tests for NamedTuple streaming with for_streaming_objects port."""

import unittest
from io import BytesIO
from pathlib import Path
from typing import NamedTuple

from taew.ports.for_streaming_objects import (
    Write as WriteProtocol,
    Read as ReadProtocol,
)
from taew.ports.for_configuring_adapters import Configure as ConfigureProtocol
from taew.adapters.launch_time.for_binding_interfaces.bind import bind


class BasicPerson(NamedTuple):
    """Test NamedTuple with basic types."""

    name: str
    age: int
    height: float
    active: bool


class Address(NamedTuple):
    """Simple NamedTuple for address information."""

    street: str
    city: str
    zip_code: str


class Contact(NamedTuple):
    """NamedTuple with nested Address."""

    name: str
    email: str
    address: Address


class Company(NamedTuple):
    """NamedTuple with multiple nested NamedTuple fields."""

    name: str
    headquarters: Address
    employee_count: int


class Organization(NamedTuple):
    """NamedTuple with list of nested NamedTuples."""

    name: str
    offices: list[Address]


class TestNamedTupleStreaming(unittest.TestCase):
    def tearDown(self) -> None:
        """Clear Root cache after each test for isolation."""
        from taew.adapters.launch_time.for_binding_interfaces._imp import (
            clear_root_cache,
        )

        clear_root_cache()

    """Test cases for NamedTuple streaming with for_streaming_objects port."""

    def _get_configurator(
        self, named_tuple_type: type[NamedTuple]
    ) -> ConfigureProtocol:
        """Create configurator for named tuple type."""
        from taew.adapters.python.named_tuple.for_streaming_objects.for_configuring_adapters import (
            Configure,
        )

        return Configure(_args=(named_tuple_type,))

    def _bind_adapters(
        self, named_tuple_type: type[NamedTuple]
    ) -> tuple[WriteProtocol, ReadProtocol]:
        """Bind write and read adapters for named tuple type."""
        configurator = self._get_configurator(named_tuple_type)
        ports = configurator()

        # Configure for_browsing_code_tree

        from taew.adapters.python.inspect.for_browsing_code_tree.for_configuring_adapters import (
            Configure as BrowseCodeTree,
        )

        browsing_config = BrowseCodeTree(_root_path=Path("./"))()

        ports.update(browsing_config)

        write = bind(WriteProtocol, ports)
        read = bind(ReadProtocol, ports)

        return write, read

    def test_basic_person_roundtrip(self) -> None:
        """Test basic NamedTuple with primitive types."""
        test_cases = (
            BasicPerson("Alice", 30, 5.5, True),
            BasicPerson("Bob", 25, 6.0, False),
            BasicPerson("José María", 35, 1.75, True),
            BasicPerson("", 0, 0.0, False),
        )

        write, read = self._bind_adapters(BasicPerson)

        for person in test_cases:
            with self.subTest(person=person):
                stream = BytesIO()
                write(person, stream)
                stream.seek(0)
                deserialized = read(stream)
                self.assertEqual(person, deserialized)

    def test_address_roundtrip(self) -> None:
        """Test NamedTuple with all string fields."""
        test_cases = (
            Address("123 Main St", "Springfield", "12345"),
            Address("", "", ""),
            Address("Café Street", "São Paulo", "01234-567"),
        )

        write, read = self._bind_adapters(Address)

        for address in test_cases:
            with self.subTest(address=address):
                stream = BytesIO()
                write(address, stream)
                stream.seek(0)
                deserialized = read(stream)
                self.assertEqual(address, deserialized)

    def test_nested_namedtuple_roundtrip(self) -> None:
        """Test NamedTuple with nested NamedTuple field."""
        address = Address("123 Main St", "Springfield", "12345")
        contact = Contact("John Doe", "john@example.com", address)

        write, read = self._bind_adapters(Contact)

        stream = BytesIO()
        write(contact, stream)
        stream.seek(0)
        deserialized = read(stream)
        self.assertEqual(contact, deserialized)

    def test_multiple_nested_namedtuples_roundtrip(self) -> None:
        """Test NamedTuple with multiple nested NamedTuple fields."""
        hq_address = Address("100 Corporate Blvd", "Business City", "54321")
        company = Company("Tech Corp", hq_address, 150)

        write, read = self._bind_adapters(Company)

        stream = BytesIO()
        write(company, stream)
        stream.seek(0)
        deserialized = read(stream)
        self.assertEqual(company, deserialized)

    def test_namedtuple_with_list_field_roundtrip(self) -> None:
        """Test NamedTuple with list of nested NamedTuples."""
        office1 = Address("123 First St", "City1", "11111")
        office2 = Address("456 Second St", "City2", "22222")
        office3 = Address("789 Third St", "City3", "33333")

        test_cases = (
            Organization("Big Org", [office1, office2, office3]),
            Organization("Empty Org", []),
            Organization("Single Office", [office1]),
        )

        write, read = self._bind_adapters(Organization)

        for org in test_cases:
            with self.subTest(org=org):
                stream = BytesIO()
                write(org, stream)
                stream.seek(0)
                deserialized = read(stream)
                self.assertEqual(org, deserialized)

    def test_various_numeric_values(self) -> None:
        """Test NamedTuple with various numeric edge cases."""
        test_cases = (
            BasicPerson("Zero", 0, 0.0, True),
            BasicPerson("Positive", 42, 3.14159, True),
            BasicPerson("Large", 2**31 - 1, 1e10, True),
            BasicPerson("Small Float", 25, 1e-10, False),
        )

        write, read = self._bind_adapters(BasicPerson)

        for person in test_cases:
            with self.subTest(person=person):
                stream = BytesIO()
                write(person, stream)
                stream.seek(0)
                deserialized = read(stream)
                self.assertEqual(person, deserialized)

    def test_special_string_values(self) -> None:
        """Test NamedTuple with special string values."""
        test_cases = (
            Contact(
                "José María",
                "josé@café.com",
                Address("Café Street", "São Paulo", "01234-567"),
            ),
            Contact(
                'John "Johnny" Doe',
                "john+test@example.com",
                Address("123 Main St.\nApt 4B", "City-Town", "12345-6789"),
            ),
            Contact("", "", Address("", "", "")),
        )

        write, read = self._bind_adapters(Contact)

        for contact in test_cases:
            with self.subTest(contact=contact):
                stream = BytesIO()
                write(contact, stream)
                stream.seek(0)
                deserialized = read(stream)
                self.assertEqual(contact, deserialized)

    def test_large_list_of_nested_namedtuples(self) -> None:
        """Test streaming with large list of nested structures."""
        addresses = [Address(f"Street {i}", f"City {i}", f"{i:05d}") for i in range(50)]
        org = Organization("Large Org", addresses)

        write, read = self._bind_adapters(Organization)

        stream = BytesIO()
        write(org, stream)
        stream.seek(0)
        deserialized = read(stream)
        self.assertEqual(org, deserialized)


if __name__ == "__main__":
    unittest.main()
