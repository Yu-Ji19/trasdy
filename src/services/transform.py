"""数据转换函数。"""

from datetime import date, timedelta
from typing import Union
import pandas as pd


def normalize_to_scale(
    series: Union[list, pd.Series], 
    base_value: float = 100.0
) -> Union[list, pd.Series]:
    """将序列归一化，使第一个值等于 base_value。
    
    Args:
        series: 要归一化的序列（列表或 pandas Series）
        base_value: 第一个元素的目标值（默认 100.0）
        
    Returns:
        与输入类型相同的归一化序列
    """
    if isinstance(series, pd.Series):
        if series.empty:
            return series
        first_value = series.iloc[0]
        if first_value == 0:
            return series * 0 + base_value
        return (series / first_value) * base_value
    else:
        # 处理列表输入
        if not series:
            return series
        first_value = series[0]
        if first_value == 0:
            return [base_value] * len(series)
        return [(v / first_value) * base_value for v in series]


def filter_by_range(df: pd.DataFrame, range_key: str) -> pd.DataFrame:
    """按日期范围过滤 DataFrame。
    
    Args:
        df: 包含 'date' 列的 DataFrame
        range_key: '6m', '1y', '3y', '5y', 'all' 之一
        
    Returns:
        过滤后的 DataFrame
    """
    if df.empty or range_key == "all":
        return df
    
    # 将范围键映射到天数
    range_days = {
        "6m": 180,
        "1y": 365,
        "3y": 365 * 3,
        "5y": 365 * 5,
    }
    
    days = range_days.get(range_key)
    if days is None:
        return df
    
    # 获取截止日期
    today = date.today()
    cutoff = today - timedelta(days=days)
    
    # 确保日期列格式正确
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"]).dt.date
    
    # 过滤
    mask = df["date"] >= cutoff
    return df[mask].reset_index(drop=True)


def prepare_chart_data(
    data: dict[str, pd.DataFrame],
    range_key: str = "all",
    normalize: bool = False
) -> dict[str, pd.DataFrame]:
    """准备用于绘图的数据。
    
    Args:
        data: 系列 ID 到 DataFrame 的字典映射
        range_key: 日期范围过滤器（'6m', '1y', '3y', '5y', 'all'）
        normalize: 是否将值归一化到 100 的比例
        
    Returns:
        系列 ID 到处理后 DataFrame 的字典映射
    """
    result = {}
    
    for series_id, df in data.items():
        if df.empty:
            result[series_id] = df
            continue
        
        # 按范围过滤
        filtered = filter_by_range(df, range_key)
        
        if normalize and not filtered.empty:
            # 归一化值
            filtered = filtered.copy()
            filtered["value"] = normalize_to_scale(filtered["value"])
        
        result[series_id] = filtered
    
    return result
