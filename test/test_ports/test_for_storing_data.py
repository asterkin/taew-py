import unittest
from typing import Any, cast
from taew.ports.for_storing_data import (
    MutableDataRepository as MutableDataRepositoryProtocol,
    MutableDataSequence as MutableDataSequenceProtocol,
)


class TestMutableDataRepositoryContextManager(unittest.TestCase):
    """Test context manager functionality for MutableDataRepository."""

    def _get_repository(self) -> MutableDataRepositoryProtocol[str, str]:
        """Factory method to create test repository with context manager support."""

        # Create a simple RAM-based implementation for testing
        class TestRAMStore(MutableDataRepositoryProtocol[str, str]):
            def __init__(self) -> None:
                self._data: dict[str, str] = {}

            def __getitem__(self, key: str) -> str:
                return self._data[key]

            def __setitem__(self, key: str, value: str) -> None:
                self._data[key] = value

            def __delitem__(self, key: str) -> None:
                del self._data[key]

            def __iter__(self):  # type: ignore
                return iter(self._data)

            def __len__(self) -> int:
                return len(self._data)

        return TestRAMStore()

    def test_context_manager_enter_returns_self(self) -> None:
        """Test that __enter__ returns the repository instance."""
        repository = self._get_repository()
        with repository as context_repo:
            self.assertIs(context_repo, repository)

    def test_context_manager_exit_with_no_exception(self) -> None:
        """Test that __exit__ handles successful completion."""
        repository = self._get_repository()
        repository["key1"] = "value1"

        with repository as context_repo:
            context_repo["key2"] = "value2"

        # Should not raise any exceptions and data should be preserved
        self.assertEqual(repository["key1"], "value1")
        self.assertEqual(repository["key2"], "value2")

    def test_context_manager_exit_with_exception(self) -> None:
        """Test that __exit__ handles exceptions properly."""
        repository = self._get_repository()
        repository["key1"] = "value1"

        with self.assertRaises(ValueError):
            with repository as context_repo:
                context_repo["key2"] = "value2"
                raise ValueError("Test exception")

        # Data should still be preserved
        self.assertEqual(repository["key1"], "value1")
        self.assertEqual(repository["key2"], "value2")

    def test_query_method_works_in_context(self) -> None:
        """Test that query method works within context manager."""
        repository = self._get_repository()

        with repository as context_repo:
            context_repo["key1"] = "apple"
            context_repo["key2"] = "banana"
            context_repo["key3"] = "apricot"

            results = list(
                context_repo.query(filter_fn=lambda value: value.startswith("a"))
            )

        self.assertEqual(len(results), 2)
        self.assertIn("apple", results)
        self.assertIn("apricot", results)


class TestMutableDataSequenceContextManager(unittest.TestCase):
    """Test context manager functionality for MutableDataSequence."""

    def _get_sequence(self) -> MutableDataSequenceProtocol[str]:
        """Factory method to create test sequence with context manager support."""

        # Create a simple RAM-based implementation for testing
        class TestRAMSequence(MutableDataSequenceProtocol[str]):
            def __init__(self) -> None:
                self._data: list[str] = []

            def __getitem__(self, index: Any) -> str:  # type: ignore
                return cast(str, self._data[index])

            def __setitem__(self, index: Any, value: Any) -> None:  # type: ignore
                self._data[index] = value

            def __delitem__(self, index: Any) -> None:  # type: ignore
                del self._data[index]

            def __len__(self) -> int:
                return len(self._data)

            def insert(self, index: int, value: str) -> None:
                self._data.insert(index, value)

        return TestRAMSequence()

    def test_context_manager_enter_returns_self(self) -> None:
        """Test that __enter__ returns the sequence instance."""
        sequence = self._get_sequence()
        with sequence as context_seq:
            self.assertIs(context_seq, sequence)

    def test_context_manager_exit_with_no_exception(self) -> None:
        """Test that __exit__ handles successful completion."""
        sequence = self._get_sequence()
        sequence.append("item1")

        with sequence as context_seq:
            context_seq.append("item2")

        # Should not raise any exceptions and data should be preserved
        self.assertEqual(len(sequence), 2)
        self.assertEqual(sequence[0], "item1")
        self.assertEqual(sequence[1], "item2")

    def test_context_manager_exit_with_exception(self) -> None:
        """Test that __exit__ handles exceptions properly."""
        sequence = self._get_sequence()
        sequence.append("item1")

        with self.assertRaises(ValueError):
            with sequence as context_seq:
                context_seq.append("item2")
                raise ValueError("Test exception")

        # Data should still be preserved
        self.assertEqual(len(sequence), 2)
        self.assertEqual(sequence[0], "item1")
        self.assertEqual(sequence[1], "item2")

    def test_query_method_works_in_context(self) -> None:
        """Test that query method works within context manager."""
        sequence = self._get_sequence()

        with sequence as context_seq:
            context_seq.append("apple")
            context_seq.append("banana")
            context_seq.append("apricot")

            results = list(
                context_seq.query(filter_fn=lambda value: value.startswith("a"))
            )

        self.assertEqual(len(results), 2)
        self.assertIn("apple", results)
        self.assertIn("apricot", results)


class TestPortDefaultImplementations(unittest.TestCase):
    """Test default implementations of the port classes directly."""

    def test_mutable_repository_context_manager_defaults(self) -> None:
        """Test MutableDataRepository context manager default implementations."""

        # Create a minimal implementation to test the default context manager methods
        class TestRepository(MutableDataRepositoryProtocol[str, str]):
            def __init__(self) -> None:
                self._data: dict[str, str] = {}

            def __getitem__(self, key: str) -> str:
                return self._data[key]

            def __setitem__(self, key: str, value: str) -> None:
                self._data[key] = value

            def __delitem__(self, key: str) -> None:
                del self._data[key]

            def __iter__(self):  # type: ignore
                return iter(self._data)

            def __len__(self) -> int:
                return len(self._data)

        repo = TestRepository()

        # Test __enter__ returns self
        self.assertIs(repo.__enter__(), repo)

        # Test __exit__ (does not return a value)
        repo.__exit__(None, None, None)

        # Test __exit__ with exception info
        try:
            raise ValueError("test")
        except ValueError as e:
            repo.__exit__(type(e), e, e.__traceback__)

    def test_mutable_sequence_context_manager_defaults(self) -> None:
        """Test MutableDataSequence context manager default implementations."""

        # Create a minimal implementation to test the default context manager methods
        class TestSequence(MutableDataSequenceProtocol[str]):
            def __init__(self) -> None:
                self._data: list[str] = []

            def __getitem__(self, index: Any) -> str:  # type: ignore
                return cast(str, self._data[index])

            def __setitem__(self, index: Any, value: Any) -> None:  # type: ignore
                self._data[index] = value

            def __delitem__(self, index: Any) -> None:  # type: ignore
                del self._data[index]

            def __len__(self) -> int:
                return len(self._data)

            def insert(self, index: int, value: str) -> None:
                self._data.insert(index, value)

        seq = TestSequence()

        # Test __enter__ returns self
        self.assertIs(seq.__enter__(), seq)

        # Test __exit__ (does not return a value)
        seq.__exit__(None, None, None)

        # Test __exit__ with exception info
        try:
            raise ValueError("test")
        except ValueError as e:
            seq.__exit__(type(e), e, e.__traceback__)


if __name__ == "__main__":
    unittest.main()
