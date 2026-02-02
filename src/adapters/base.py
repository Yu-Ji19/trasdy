"""数据源适配器的抽象基类。"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
import pandas as pd


class DataSourceAdapter(ABC):
    """外部数据源适配器的抽象基类。"""
    
    @abstractmethod
    def fetch(
        self, 
        series_id: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """从数据源获取时间序列数据。
        
        Args:
            series_id: 数据系列的标识符
            start_date: 可选的数据起始日期
            end_date: 可选的数据结束日期
            
        Returns:
            包含 ['date', 'value'] 列的 DataFrame
        """
        pass
    
    @abstractmethod
    def get_metadata(self, series_id: str) -> dict:
        """获取系列的元数据。
        
        Args:
            series_id: 数据系列的标识符
            
        Returns:
            包含系列元数据的字典
        """
        pass
