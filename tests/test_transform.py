"""Tests for transform functions."""

import pytest
from datetime import date, timedelta
import pandas as pd

from src.services.transform import normalize_to_scale, filter_by_range, prepare_chart_data


class TestNormalizeToScale:
    """Tests for normalize_to_scale function."""
    
    def test_list_normalize(self):
        """Test normalizing a list."""
        result = normalize_to_scale([100, 110, 90], base_value=100)
        assert result == pytest.approx([100.0, 110.0, 90.0])
    
    def test_list_normalize_different_base(self):
        """Test normalizing with different starting value."""
        result = normalize_to_scale([50, 75, 25], base_value=100)
        assert result == [100.0, 150.0, 50.0]
    
    def test_series_normalize(self):
        """Test normalizing a pandas Series."""
        series = pd.Series([200, 220, 180])
        result = normalize_to_scale(series, base_value=100)
        assert list(result) == pytest.approx([100.0, 110.0, 90.0])
    
    def test_empty_list(self):
        """Test empty list returns empty list."""
        result = normalize_to_scale([])
        assert result == []
    
    def test_empty_series(self):
        """Test empty Series returns empty Series."""
        series = pd.Series([], dtype=float)
        result = normalize_to_scale(series)
        assert len(result) == 0
    
    def test_zero_base_value(self):
        """Test handling of zero first value."""
        result = normalize_to_scale([0, 10, 20], base_value=100)
        assert result == [100, 100, 100]


class TestFilterByRange:
    """Tests for filter_by_range function."""
    
    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame spanning 2 years."""
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(730)]  # 2 years
        values = list(range(730))
        return pd.DataFrame({"date": dates, "value": values})
    
    def test_filter_6m(self, sample_df):
        """Test 6 month filter returns approximately 180 days."""
        result = filter_by_range(sample_df, "6m")
        # Should be around 180 days, give or take
        assert 175 <= len(result) <= 185
    
    def test_filter_1y(self, sample_df):
        """Test 1 year filter returns approximately 365 days."""
        result = filter_by_range(sample_df, "1y")
        assert 360 <= len(result) <= 370
    
    def test_filter_all(self, sample_df):
        """Test 'all' filter returns all data."""
        result = filter_by_range(sample_df, "all")
        assert len(result) == len(sample_df)
    
    def test_empty_df(self):
        """Test empty DataFrame returns empty DataFrame."""
        df = pd.DataFrame(columns=["date", "value"])
        result = filter_by_range(df, "6m")
        assert len(result) == 0
    
    def test_invalid_range_key(self, sample_df):
        """Test invalid range key returns all data."""
        result = filter_by_range(sample_df, "invalid")
        assert len(result) == len(sample_df)


class TestPrepareChartData:
    """Tests for prepare_chart_data function."""
    
    def test_normalize_and_filter(self):
        """Test combined normalize and filter."""
        today = date.today()
        df = pd.DataFrame({
            "date": [today - timedelta(days=i) for i in range(100)],
            "value": [100 + i for i in range(100)]
        })
        
        data = {"test": df}
        result = prepare_chart_data(data, range_key="all", normalize=True)
        
        # First value should be 100 after normalization
        assert result["test"]["value"].iloc[0] == 100.0
    
    def test_empty_data(self):
        """Test handling of empty DataFrames."""
        data = {"test": pd.DataFrame(columns=["date", "value"])}
        result = prepare_chart_data(data, range_key="6m", normalize=True)
        assert result["test"].empty
