"""转换函数的测试。"""

import pytest
from datetime import date, timedelta
import pandas as pd

from src.services.transform import normalize_to_scale, filter_by_range, prepare_chart_data


class TestNormalizeToScale:
    """normalize_to_scale 函数的测试。"""
    
    def test_list_normalize(self):
        """测试列表归一化。"""
        result = normalize_to_scale([100, 110, 90], base_value=100)
        assert result == pytest.approx([100.0, 110.0, 90.0])
    
    def test_list_normalize_different_base(self):
        """测试不同起始值的归一化。"""
        result = normalize_to_scale([50, 75, 25], base_value=100)
        assert result == [100.0, 150.0, 50.0]
    
    def test_series_normalize(self):
        """测试 pandas Series 归一化。"""
        series = pd.Series([200, 220, 180])
        result = normalize_to_scale(series, base_value=100)
        assert list(result) == pytest.approx([100.0, 110.0, 90.0])
    
    def test_empty_list(self):
        """测试空列表返回空列表。"""
        result = normalize_to_scale([])
        assert result == []
    
    def test_empty_series(self):
        """测试空 Series 返回空 Series。"""
        series = pd.Series([], dtype=float)
        result = normalize_to_scale(series)
        assert len(result) == 0
    
    def test_zero_base_value(self):
        """测试第一个值为零的处理。"""
        result = normalize_to_scale([0, 10, 20], base_value=100)
        assert result == [100, 100, 100]


class TestFilterByRange:
    """filter_by_range 函数的测试。"""
    
    @pytest.fixture
    def sample_df(self):
        """创建跨越 2 年的示例 DataFrame。"""
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(730)]  # 2 years
        values = list(range(730))
        return pd.DataFrame({"date": dates, "value": values})
    
    def test_filter_6m(self, sample_df):
        """测试 6 个月过滤器返回大约 180 天。"""
        result = filter_by_range(sample_df, "6m")
        # 应该大约 180 天左右
        assert 175 <= len(result) <= 185
    
    def test_filter_1y(self, sample_df):
        """测试 1 年过滤器返回大约 365 天。"""
        result = filter_by_range(sample_df, "1y")
        assert 360 <= len(result) <= 370
    
    def test_filter_all(self, sample_df):
        """测试 'all' 过滤器返回所有数据。"""
        result = filter_by_range(sample_df, "all")
        assert len(result) == len(sample_df)
    
    def test_empty_df(self):
        """测试空 DataFrame 返回空 DataFrame。"""
        df = pd.DataFrame(columns=["date", "value"])
        result = filter_by_range(df, "6m")
        assert len(result) == 0
    
    def test_invalid_range_key(self, sample_df):
        """测试无效的范围键返回所有数据。"""
        result = filter_by_range(sample_df, "invalid")
        assert len(result) == len(sample_df)


class TestPrepareChartData:
    """prepare_chart_data 函数的测试。"""
    
    def test_normalize_and_filter(self):
        """测试组合的归一化和过滤。"""
        today = date.today()
        df = pd.DataFrame({
            "date": [today - timedelta(days=i) for i in range(100)],
            "value": [100 + i for i in range(100)]
        })
        
        data = {"test": df}
        result = prepare_chart_data(data, range_key="all", normalize=True)
        
        # 归一化后第一个值应该是 100
        assert result["test"]["value"].iloc[0] == 100.0
    
    def test_empty_data(self):
        """测试空 DataFrame 的处理。"""
        data = {"test": pd.DataFrame(columns=["date", "value"])}
        result = prepare_chart_data(data, range_key="6m", normalize=True)
        assert result["test"].empty
