"""CSV 仓储实现的测试。"""

import pytest
import tempfile
from pathlib import Path
from datetime import date
import pandas as pd

from src.repositories.csv_repository import CSVSeriesRepository, JSONMetadataRepository


class TestCSVSeriesRepository:
    """CSVSeriesRepository 的测试。"""
    
    @pytest.fixture
    def temp_dir(self):
        """为测试创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def repo(self, temp_dir):
        """创建仓储实例。"""
        return CSVSeriesRepository(data_dir=temp_dir)
    
    def test_write_and_read_roundtrip(self, repo):
        """测试数据可以写入并读回。"""
        # 创建测试数据
        data = pd.DataFrame({
            "date": [date(2025, 1, 1), date(2025, 1, 2), date(2025, 1, 3)],
            "value": [100.0, 101.5, 99.0]
        })
        
        # 写入
        rows_written = repo.write("test_series", data)
        assert rows_written == 3
        
        # 读回
        result = repo.read("test_series")
        assert len(result) == 3
        assert list(result["value"]) == [100.0, 101.5, 99.0]
    
    def test_append_mode(self, repo):
        """测试追加模式添加新数据。"""
        # 初始数据
        data1 = pd.DataFrame({
            "date": [date(2025, 1, 1), date(2025, 1, 2)],
            "value": [100.0, 101.0]
        })
        repo.write("test_series", data1)
        
        # 追加新数据
        data2 = pd.DataFrame({
            "date": [date(2025, 1, 3), date(2025, 1, 4)],
            "value": [102.0, 103.0]
        })
        repo.write("test_series", data2, mode="append")
        
        # 验证合并结果
        result = repo.read("test_series")
        assert len(result) == 4
        assert list(result["value"]) == [100.0, 101.0, 102.0, 103.0]
    
    def test_append_mode_deduplicates(self, repo):
        """测试追加模式去除重复日期。"""
        # 初始数据
        data1 = pd.DataFrame({
            "date": [date(2025, 1, 1), date(2025, 1, 2)],
            "value": [100.0, 101.0]
        })
        repo.write("test_series", data1)
        
        # 追加有重叠日期的数据
        data2 = pd.DataFrame({
            "date": [date(2025, 1, 2), date(2025, 1, 3)],
            "value": [999.0, 102.0]  # 999 应该替换 101
        })
        repo.write("test_series", data2, mode="append")
        
        # 验证去重（新值优先）
        result = repo.read("test_series")
        assert len(result) == 3
        assert result[result["date"] == date(2025, 1, 2)]["value"].iloc[0] == 999.0
    
    def test_get_date_range(self, repo):
        """测试 get_date_range 返回正确的日期。"""
        # 无数据
        start, end = repo.get_date_range("nonexistent")
        assert start is None
        assert end is None
        
        # 有数据
        data = pd.DataFrame({
            "date": [date(2025, 1, 5), date(2025, 1, 1), date(2025, 1, 10)],
            "value": [100.0, 101.0, 102.0]
        })
        repo.write("test_series", data)
        
        start, end = repo.get_date_range("test_series")
        assert start == date(2025, 1, 1)
        assert end == date(2025, 1, 10)
    
    def test_exists(self, repo):
        """测试 exists 检查。"""
        assert not repo.exists("nonexistent")
        
        data = pd.DataFrame({
            "date": [date(2025, 1, 1)],
            "value": [100.0]
        })
        repo.write("test_series", data)
        
        assert repo.exists("test_series")
    
    def test_read_with_date_filter(self, repo):
        """测试带日期范围过滤的读取。"""
        data = pd.DataFrame({
            "date": [date(2025, 1, 1), date(2025, 1, 5), date(2025, 1, 10)],
            "value": [100.0, 105.0, 110.0]
        })
        repo.write("test_series", data)
        
        # 按起始日期过滤
        result = repo.read("test_series", start_date=date(2025, 1, 5))
        assert len(result) == 2
        
        # 按结束日期过滤
        result = repo.read("test_series", end_date=date(2025, 1, 5))
        assert len(result) == 2
        
        # 同时按起始和结束日期过滤
        result = repo.read("test_series", 
                          start_date=date(2025, 1, 3), 
                          end_date=date(2025, 1, 7))
        assert len(result) == 1
        assert result["date"].iloc[0] == date(2025, 1, 5)


class TestJSONMetadataRepository:
    """JSONMetadataRepository 的测试。"""
    
    @pytest.fixture
    def temp_file(self):
        """为测试创建临时文件路径。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "metadata.json"
    
    @pytest.fixture
    def repo(self, temp_file):
        """创建仓储实例。"""
        return JSONMetadataRepository(metadata_file=temp_file)
    
    def test_get_nonexistent(self, repo):
        """测试获取不存在的系列的元数据。"""
        result = repo.get("nonexistent")
        assert result is None
    
    def test_update_and_get(self, repo):
        """测试更新和获取元数据。"""
        repo.update("series1", {"last_updated": "2025-01-01", "count": 100})
        
        result = repo.get("series1")
        assert result["last_updated"] == "2025-01-01"
        assert result["count"] == 100
    
    def test_update_merges(self, repo):
        """测试更新与现有数据合并。"""
        repo.update("series1", {"field1": "value1"})
        repo.update("series1", {"field2": "value2"})
        
        result = repo.get("series1")
        assert result["field1"] == "value1"
        assert result["field2"] == "value2"
    
    def test_get_all(self, repo):
        """测试获取所有元数据。"""
        repo.update("series1", {"name": "Series 1"})
        repo.update("series2", {"name": "Series 2"})
        
        all_metadata = repo.get_all()
        assert len(all_metadata) == 2
        assert "series1" in all_metadata
        assert "series2" in all_metadata
