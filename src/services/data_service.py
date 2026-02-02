"""数据服务，用于管理系列数据和同步。"""

from datetime import date, timedelta
from enum import Enum
from typing import Optional
import pandas as pd

from src.repositories.base import SeriesRepository, MetadataRepository
from src.adapters.fred_adapter import FREDAdapter
from config.settings import load_series_config


class RefreshMode(Enum):
    """数据刷新模式。"""
    FULL = "full"
    INCREMENTAL = "incremental"


class DataService:
    """时间序列数据管理服务。
    
    处理数据检索、缓存和与外部数据源的同步。
    使用依赖注入获取仓储。
    """
    
    def __init__(
        self, 
        series_repo: SeriesRepository, 
        metadata_repo: MetadataRepository,
        adapter: Optional[FREDAdapter] = None
    ):
        """初始化数据服务。
        
        Args:
            series_repo: 系列数据存储仓储
            metadata_repo: 元数据存储仓储
            adapter: 数据源适配器（默认为 FREDAdapter）
        """
        self.series_repo = series_repo
        self.metadata_repo = metadata_repo
        self.adapter = adapter or FREDAdapter()
        self._series_config = {s["id"]: s for s in load_series_config()}
    
    def _get_fred_series_id(self, series_id: str) -> str:
        """获取本地系列 ID 对应的 FRED 系列 ID。"""
        config = self._series_config.get(series_id)
        if config:
            return config.get("fred_series_id", series_id)
        return series_id
    
    def get_series(
        self, 
        series_ids: list[str], 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> dict[str, pd.DataFrame]:
        """获取时间序列数据。
        
        如果本地存在数据，则从 CSV 读取。否则从 API 获取并保存到本地。
        
        Args:
            series_ids: 系列标识符列表
            start_date: 可选的起始日期过滤器
            end_date: 可选的结束日期过滤器
            
        Returns:
            系列 ID 到 DataFrame 的字典映射
        """
        result = {}
        
        for series_id in series_ids:
            if self.series_repo.exists(series_id):
                # 从本地存储读取
                df = self.series_repo.read(series_id, start_date, end_date)
            else:
                # 从 API 获取并保存
                fred_id = self._get_fred_series_id(series_id)
                df = self.adapter.fetch(fred_id, start_date, end_date)
                
                if not df.empty:
                    self.series_repo.write(series_id, df)
                    self._update_metadata_after_write(series_id, df)
            
            result[series_id] = df
        
        return result
    
    def refresh_data(
        self, 
        series_ids: list[str], 
        mode: RefreshMode = RefreshMode.INCREMENTAL
    ) -> dict[str, int]:
        """从外部数据源刷新数据。
        
        Args:
            series_ids: 要刷新的系列列表
            mode: FULL 替换所有数据，INCREMENTAL 追加新数据
            
        Returns:
            系列 ID 到新记录数的字典映射
        """
        result = {}
        
        for series_id in series_ids:
            fred_id = self._get_fred_series_id(series_id)
            
            if mode == RefreshMode.FULL:
                # 全量刷新 - 获取所有数据并替换
                df = self.adapter.fetch(fred_id)
                if not df.empty:
                    rows_written = self.series_repo.write(series_id, df, mode="replace")
                    self._update_metadata_after_write(series_id, df)
                    result[series_id] = rows_written
                else:
                    result[series_id] = 0
            else:
                # 增量刷新 - 仅获取新数据
                metadata = self.metadata_repo.get(series_id)
                
                if metadata and metadata.get("data_end_date"):
                    # 解析存储的日期
                    end_date_str = metadata["data_end_date"]
                    if isinstance(end_date_str, str):
                        last_date = date.fromisoformat(end_date_str)
                    else:
                        last_date = end_date_str
                    start_date = last_date + timedelta(days=1)
                else:
                    # 没有现有数据，获取所有数据
                    start_date = None
                
                df = self.adapter.fetch(fred_id, start_date=start_date)
                
                if not df.empty:
                    rows_written = self.series_repo.write(series_id, df, mode="append")
                    # 重新读取以获取完整的日期范围用于元数据
                    full_df = self.series_repo.read(series_id)
                    self._update_metadata_after_write(series_id, full_df)
                    result[series_id] = len(df)
                else:
                    result[series_id] = 0
        
        return result
    
    def _update_metadata_after_write(self, series_id: str, df: pd.DataFrame) -> None:
        """写入数据后更新元数据。
        
        Args:
            series_id: 系列标识符
            df: 已写入的 DataFrame
        """
        if df.empty:
            return
        
        # 获取日期范围
        dates = pd.to_datetime(df["date"])
        data_start = dates.min().date()
        data_end = dates.max().date()
        
        self.metadata_repo.update(series_id, {
            "last_updated": date.today().isoformat(),
            "data_start_date": data_start.isoformat(),
            "data_end_date": data_end.isoformat(),
            "record_count": len(df),
        })
    
    def get_all_configured_series_ids(self) -> list[str]:
        """获取所有已配置的系列 ID。"""
        return list(self._series_config.keys())
