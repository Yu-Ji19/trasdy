"""FRED API 适配器实现。"""

from datetime import date
from typing import Optional
import requests
import pandas as pd

from src.adapters.base import DataSourceAdapter
from config.settings import get_api_key


class FREDAdapter(DataSourceAdapter):
    """美联储经济数据 (FRED) API 适配器。"""
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化 FRED 适配器。
        
        Args:
            api_key: FRED API 密钥。如果未提供，则从 FRED_API_KEY 文件读取。
        """
        self._api_key = api_key
    
    @property
    def api_key(self) -> str:
        """获取 API 密钥，如果需要则从文件加载。"""
        if self._api_key is None:
            self._api_key = get_api_key()
        return self._api_key
    
    def fetch(
        self, 
        series_id: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """从 FRED API 获取时间序列数据。
        
        Args:
            series_id: FRED 系列 ID（例如 'SP500', 'DGS10'）
            start_date: 可选的数据起始日期（date 对象或 'YYYY-MM-DD' 字符串）
            end_date: 可选的数据结束日期（date 对象或 'YYYY-MM-DD' 字符串）
            
        Returns:
            包含 ['date', 'value'] 列的 DataFrame
        """
        url = f"{self.BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }
        
        if start_date:
            # 同时处理 date 对象和字符串输入
            params["observation_start"] = start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date
        if end_date:
            params["observation_end"] = end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        observations = data.get("observations", [])
        
        # 将观测数据解析为 DataFrame
        rows = []
        for obs in observations:
            value_str = obs.get("value", "")
            # 跳过缺失值（FRED 使用 "." 表示缺失）
            if value_str == "." or value_str == "":
                continue
            
            try:
                rows.append({
                    "date": obs["date"],
                    "value": float(value_str)
                })
            except (ValueError, KeyError):
                # 跳过无法解析的行
                continue
        
        if not rows:
            return pd.DataFrame(columns=["date", "value"])
        
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df.sort_values("date").reset_index(drop=True)
    
    def get_metadata(self, series_id: str) -> dict:
        """获取 FRED 系列的元数据。
        
        Args:
            series_id: FRED 系列 ID
            
        Returns:
            包含系列元数据的字典
        """
        url = f"{self.BASE_URL}/series"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        seriess = data.get("seriess", [])
        
        if not seriess:
            return {}
        
        series = seriess[0]
        return {
            "id": series.get("id"),
            "title": series.get("title"),
            "frequency": series.get("frequency_short"),
            "units": series.get("units_short"),
            "seasonal_adjustment": series.get("seasonal_adjustment_short"),
        }
