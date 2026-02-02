"""数据仓储的抽象基类。"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Any
import pandas as pd


class SeriesRepository(ABC):
    """时间序列数据存储的抽象基类。"""
    
    @abstractmethod
    def read(
        self, 
        series_id: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """读取时间序列数据。
        
        Args:
            series_id: 系列的标识符
            start_date: 可选的起始日期过滤器
            end_date: 可选的结束日期过滤器
            
        Returns:
            包含 ['date', 'value'] 列的 DataFrame
        """
        pass
    
    @abstractmethod
    def write(
        self, 
        series_id: str, 
        data: pd.DataFrame, 
        mode: str = "replace"
    ) -> int:
        """写入时间序列数据。
        
        Args:
            series_id: 系列的标识符
            data: 包含 ['date', 'value'] 列的 DataFrame
            mode: 'replace' 覆盖，'append' 追加新数据
            
        Returns:
            写入的行数
        """
        pass
    
    @abstractmethod
    def exists(self, series_id: str) -> bool:
        """检查系列数据是否存在。
        
        Args:
            series_id: 系列的标识符
            
        Returns:
            如果数据存在则返回 True
        """
        pass
    
    @abstractmethod
    def get_date_range(self, series_id: str) -> tuple[Optional[date], Optional[date]]:
        """获取存储数据的日期范围。
        
        Args:
            series_id: 系列的标识符
            
        Returns:
            (start_date, end_date) 元组，如果没有数据则返回 (None, None)
        """
        pass


class MetadataRepository(ABC):
    """元数据存储的抽象基类。"""
    
    @abstractmethod
    def get(self, series_id: str) -> Optional[dict]:
        """获取系列的元数据。
        
        Args:
            series_id: 系列的标识符
            
        Returns:
            元数据字典，如果未找到则返回 None
        """
        pass
    
    @abstractmethod
    def update(self, series_id: str, updates: dict) -> None:
        """更新系列的元数据。
        
        Args:
            series_id: 系列的标识符
            updates: 要更新的字段字典
        """
        pass
    
    @abstractmethod
    def get_all(self) -> dict[str, dict]:
        """获取所有元数据。
        
        Returns:
            系列 ID 到元数据的字典映射
        """
        pass
