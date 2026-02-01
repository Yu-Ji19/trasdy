"""Tests for CSV repository implementation."""

import pytest
import tempfile
from pathlib import Path
from datetime import date
import pandas as pd

from src.repositories.csv_repository import CSVSeriesRepository, JSONMetadataRepository


class TestCSVSeriesRepository:
    """Tests for CSVSeriesRepository."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def repo(self, temp_dir):
        """Create a repository instance."""
        return CSVSeriesRepository(data_dir=temp_dir)
    
    def test_write_and_read_roundtrip(self, repo):
        """Test that data can be written and read back."""
        # Create test data
        data = pd.DataFrame({
            "date": [date(2025, 1, 1), date(2025, 1, 2), date(2025, 1, 3)],
            "value": [100.0, 101.5, 99.0]
        })
        
        # Write
        rows_written = repo.write("test_series", data)
        assert rows_written == 3
        
        # Read back
        result = repo.read("test_series")
        assert len(result) == 3
        assert list(result["value"]) == [100.0, 101.5, 99.0]
    
    def test_append_mode(self, repo):
        """Test append mode adds new data."""
        # Initial data
        data1 = pd.DataFrame({
            "date": [date(2025, 1, 1), date(2025, 1, 2)],
            "value": [100.0, 101.0]
        })
        repo.write("test_series", data1)
        
        # Append new data
        data2 = pd.DataFrame({
            "date": [date(2025, 1, 3), date(2025, 1, 4)],
            "value": [102.0, 103.0]
        })
        repo.write("test_series", data2, mode="append")
        
        # Verify combined
        result = repo.read("test_series")
        assert len(result) == 4
        assert list(result["value"]) == [100.0, 101.0, 102.0, 103.0]
    
    def test_append_mode_deduplicates(self, repo):
        """Test that append mode removes duplicate dates."""
        # Initial data
        data1 = pd.DataFrame({
            "date": [date(2025, 1, 1), date(2025, 1, 2)],
            "value": [100.0, 101.0]
        })
        repo.write("test_series", data1)
        
        # Append with overlapping date
        data2 = pd.DataFrame({
            "date": [date(2025, 1, 2), date(2025, 1, 3)],
            "value": [999.0, 102.0]  # 999 should replace 101
        })
        repo.write("test_series", data2, mode="append")
        
        # Verify deduplication (new value wins)
        result = repo.read("test_series")
        assert len(result) == 3
        assert result[result["date"] == date(2025, 1, 2)]["value"].iloc[0] == 999.0
    
    def test_get_date_range(self, repo):
        """Test get_date_range returns correct dates."""
        # No data
        start, end = repo.get_date_range("nonexistent")
        assert start is None
        assert end is None
        
        # With data
        data = pd.DataFrame({
            "date": [date(2025, 1, 5), date(2025, 1, 1), date(2025, 1, 10)],
            "value": [100.0, 101.0, 102.0]
        })
        repo.write("test_series", data)
        
        start, end = repo.get_date_range("test_series")
        assert start == date(2025, 1, 1)
        assert end == date(2025, 1, 10)
    
    def test_exists(self, repo):
        """Test exists check."""
        assert not repo.exists("nonexistent")
        
        data = pd.DataFrame({
            "date": [date(2025, 1, 1)],
            "value": [100.0]
        })
        repo.write("test_series", data)
        
        assert repo.exists("test_series")
    
    def test_read_with_date_filter(self, repo):
        """Test reading with date range filters."""
        data = pd.DataFrame({
            "date": [date(2025, 1, 1), date(2025, 1, 5), date(2025, 1, 10)],
            "value": [100.0, 105.0, 110.0]
        })
        repo.write("test_series", data)
        
        # Filter by start date
        result = repo.read("test_series", start_date=date(2025, 1, 5))
        assert len(result) == 2
        
        # Filter by end date
        result = repo.read("test_series", end_date=date(2025, 1, 5))
        assert len(result) == 2
        
        # Filter by both
        result = repo.read("test_series", 
                          start_date=date(2025, 1, 3), 
                          end_date=date(2025, 1, 7))
        assert len(result) == 1
        assert result["date"].iloc[0] == date(2025, 1, 5)


class TestJSONMetadataRepository:
    """Tests for JSONMetadataRepository."""
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file path for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "metadata.json"
    
    @pytest.fixture
    def repo(self, temp_file):
        """Create a repository instance."""
        return JSONMetadataRepository(metadata_file=temp_file)
    
    def test_get_nonexistent(self, repo):
        """Test getting metadata for nonexistent series."""
        result = repo.get("nonexistent")
        assert result is None
    
    def test_update_and_get(self, repo):
        """Test updating and retrieving metadata."""
        repo.update("series1", {"last_updated": "2025-01-01", "count": 100})
        
        result = repo.get("series1")
        assert result["last_updated"] == "2025-01-01"
        assert result["count"] == 100
    
    def test_update_merges(self, repo):
        """Test that update merges with existing data."""
        repo.update("series1", {"field1": "value1"})
        repo.update("series1", {"field2": "value2"})
        
        result = repo.get("series1")
        assert result["field1"] == "value1"
        assert result["field2"] == "value2"
    
    def test_get_all(self, repo):
        """Test getting all metadata."""
        repo.update("series1", {"name": "Series 1"})
        repo.update("series2", {"name": "Series 2"})
        
        all_metadata = repo.get_all()
        assert len(all_metadata) == 2
        assert "series1" in all_metadata
        assert "series2" in all_metadata
