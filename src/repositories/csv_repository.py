"""仓储接口的 CSV 和 JSON 实现。"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional
import pandas as pd

from src.repositories.base import SeriesRepository, MetadataRepository
from config.settings import get_project_root


class CSVSeriesRepository(SeriesRepository):
    """基于 CSV 的 SeriesRepository 实现。"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """初始化仓储。
        
        Args:
            data_dir: CSV 文件目录。默认为 data/index_data/
        """
        if data_dir is None:
            data_dir = get_project_root() / "data" / "index_data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, series_id: str) -> Path:
        """获取系列的 CSV 文件路径。"""
        return self.data_dir / f"{series_id}.csv"
    
    def read(
        self, 
        series_id: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """从 CSV 读取时间序列数据。"""
        file_path = self._get_file_path(series_id)
        
        if not file_path.exists():
            return pd.DataFrame(columns=["date", "value"])
        
        df = pd.read_csv(file_path, parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"]).dt.date
        
        # 应用日期过滤器
        if start_date is not None:
            df = df[df["date"] >= start_date]
        if end_date is not None:
            df = df[df["date"] <= end_date]
        
        return df.sort_values("date").reset_index(drop=True)
    
    def write(
        self, 
        series_id: str, 
        data: pd.DataFrame, 
        mode: str = "replace"
    ) -> int:
        """将时间序列数据写入 CSV。"""
        file_path = self._get_file_path(series_id)
        
        if data.empty:
            return 0
        
        # 确保列正确
        if "date" not in data.columns or "value" not in data.columns:
            raise ValueError("DataFrame must have 'date' and 'value' columns")
        
        # 标准化日期列
        df = data.copy()
        df["date"] = pd.to_datetime(df["date"]).dt.date
        
        if mode == "append" and file_path.exists():
            existing = self.read(series_id)
            # 合并并去重（保留新数据）
            combined = pd.concat([existing, df], ignore_index=True)
            combined = combined.drop_duplicates(subset=["date"], keep="last")
            df = combined.sort_values("date").reset_index(drop=True)
        
        df.to_csv(file_path, index=False)
        return len(df)
    
    def exists(self, series_id: str) -> bool:
        """检查系列 CSV 文件是否存在。"""
        return self._get_file_path(series_id).exists()
    
    def get_date_range(self, series_id: str) -> tuple[Optional[date], Optional[date]]:
        """获取存储数据的日期范围。"""
        if not self.exists(series_id):
            return (None, None)
        
        df = self.read(series_id)
        if df.empty:
            return (None, None)
        
        return (df["date"].min(), df["date"].max())


class JSONMetadataRepository(MetadataRepository):
    """基于 JSON 文件的 MetadataRepository 实现。"""
    
    def __init__(self, metadata_file: Optional[Path] = None):
        """初始化仓储。
        
        Args:
            metadata_file: 元数据 JSON 文件路径。默认为 data/metadata.json
        """
        if metadata_file is None:
            metadata_file = get_project_root() / "data" / "metadata.json"
        self.metadata_file = metadata_file
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> dict[str, dict]:
        """从文件加载元数据。"""
        if not self.metadata_file.exists():
            return {}
        
        with open(self.metadata_file, "r") as f:
            return json.load(f)
    
    def _save(self, data: dict[str, dict]) -> None:
        """将元数据保存到文件。"""
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def get(self, series_id: str) -> Optional[dict]:
        """获取系列的元数据。"""
        all_metadata = self._load()
        return all_metadata.get(series_id)
    
    def update(self, series_id: str, updates: dict) -> None:
        """更新系列的元数据。"""
        all_metadata = self._load()
        
        if series_id not in all_metadata:
            all_metadata[series_id] = {}
        
        all_metadata[series_id].update(updates)
        self._save(all_metadata)
    
    def get_all(self) -> dict[str, dict]:
        """获取所有元数据。"""
        return self._load()
