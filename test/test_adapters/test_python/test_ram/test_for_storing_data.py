import unittest
from typing import TypeAlias
from dataclasses import dataclass

from taew.adapters.python.ram.for_storing_data import DataRepository
from taew.adapters.python.ram.for_storing_data import MutableDataRepository


@dataclass(frozen=True)
class SampleRecord:
    """Sample record for testing data repositories."""

    id: str
    name: str
    score: int


SampleRecordRepository: TypeAlias = DataRepository[str, SampleRecord]
MutableSampleRecordRepository: TypeAlias = MutableDataRepository[str, SampleRecord]


class TestDataRepository(unittest.TestCase):
    """Test cases for RAM-based data repositories."""

    def create_data_repository(self) -> SampleRecordRepository:
        """Factory method to create a DataRepository adapter."""

        return SampleRecordRepository()

    def create_mutable_data_repository(self) -> MutableSampleRecordRepository:
        """Factory method to create a MutableDataRepository adapter."""

        return MutableSampleRecordRepository()

    def create_data_repository_from_mutable(self) -> SampleRecordRepository:
        """Factory method to create DataRepository from MutableDataRepository with sample data."""
        mutable_repo = self.create_mutable_data_repository()

        # Add sample data
        mutable_repo["rec1"] = SampleRecord(id="rec1", name="Alice", score=95)
        mutable_repo["rec2"] = SampleRecord(id="rec2", name="Bob", score=87)
        mutable_repo["rec3"] = SampleRecord(id="rec3", name="Charlie", score=92)

        # Create read-only repository and copy data
        from taew.adapters.python.ram.for_storing_data import DataRepository

        read_only_repo = DataRepository[str, SampleRecord](mutable_repo)
        return read_only_repo

    def test_basic_storage_and_retrieval(self) -> None:
        """Test basic storage and retrieval operations."""
        # Given
        mutable_repo = self.create_mutable_data_repository()
        record = SampleRecord(id="test1", name="Test User", score=85)

        # When
        mutable_repo["test1"] = record

        # Then
        retrieved_record = mutable_repo["test1"]
        self.assertEqual(retrieved_record, record)
        self.assertEqual(retrieved_record.name, "Test User")
        self.assertEqual(retrieved_record.score, 85)

    def test_query_with_filter(self) -> None:
        """Test query functionality with filtering."""
        # Given
        repo = self.create_data_repository_from_mutable()

        # When - query for records with score >= 90
        high_scorers = list(repo.query(filter_fn=lambda r: r.score >= 90))

        # Then
        self.assertEqual(len(high_scorers), 2)
        high_scorer_names = {record.name for record in high_scorers}
        self.assertEqual(high_scorer_names, {"Alice", "Charlie"})

    def test_query_with_sorting(self) -> None:
        """Test query functionality with sorting."""
        # Given
        repo = self.create_data_repository_from_mutable()

        # When - query all records sorted by score descending
        sorted_records = list(
            repo.query(
                filter_fn=lambda r: True,  # Include all records
                sort_key=lambda r: r.score,
                reverse=True,
            )
        )

        # Then
        self.assertEqual(len(sorted_records), 3)
        expected_order = ["Alice", "Charlie", "Bob"]  # 95, 92, 87
        actual_order = [record.name for record in sorted_records]
        self.assertEqual(actual_order, expected_order)

    def test_empty_query_results(self) -> None:
        """Test query with filter that matches no records."""
        # Given
        repo = self.create_data_repository_from_mutable()

        # When - query for records with score > 100 (none exist)
        perfect_scorers = list(repo.query(filter_fn=lambda r: r.score > 100))

        # Then
        self.assertEqual(len(perfect_scorers), 0)


if __name__ == "__main__":
    unittest.main()
