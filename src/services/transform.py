"""Data transformation functions."""

from datetime import date, timedelta
from typing import Union
import pandas as pd


def normalize_to_scale(
    series: Union[list, pd.Series], 
    base_value: float = 100.0
) -> Union[list, pd.Series]:
    """Normalize a series to a scale where the first value equals base_value.
    
    Args:
        series: The series to normalize (list or pandas Series)
        base_value: The target value for the first element (default 100.0)
        
    Returns:
        Normalized series of the same type as input
    """
    if isinstance(series, pd.Series):
        if series.empty:
            return series
        first_value = series.iloc[0]
        if first_value == 0:
            return series * 0 + base_value
        return (series / first_value) * base_value
    else:
        # Handle list input
        if not series:
            return series
        first_value = series[0]
        if first_value == 0:
            return [base_value] * len(series)
        return [(v / first_value) * base_value for v in series]


def filter_by_range(df: pd.DataFrame, range_key: str) -> pd.DataFrame:
    """Filter DataFrame by date range.
    
    Args:
        df: DataFrame with a 'date' column
        range_key: One of '6m', '1y', '3y', '5y', 'all'
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or range_key == "all":
        return df
    
    # Map range keys to number of days
    range_days = {
        "6m": 180,
        "1y": 365,
        "3y": 365 * 3,
        "5y": 365 * 5,
    }
    
    days = range_days.get(range_key)
    if days is None:
        return df
    
    # Get cutoff date
    today = date.today()
    cutoff = today - timedelta(days=days)
    
    # Ensure date column is in proper format
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"]).dt.date
    
    # Filter
    mask = df["date"] >= cutoff
    return df[mask].reset_index(drop=True)


def prepare_chart_data(
    data: dict[str, pd.DataFrame],
    range_key: str = "all",
    normalize: bool = False
) -> dict[str, pd.DataFrame]:
    """Prepare data for charting.
    
    Args:
        data: Dictionary mapping series_id to DataFrame
        range_key: Date range filter ('6m', '1y', '3y', '5y', 'all')
        normalize: Whether to normalize values to scale of 100
        
    Returns:
        Dictionary mapping series_id to prepared DataFrame
    """
    result = {}
    
    for series_id, df in data.items():
        if df.empty:
            result[series_id] = df
            continue
        
        # Filter by range
        filtered = filter_by_range(df, range_key)
        
        if normalize and not filtered.empty:
            # Normalize values
            filtered = filtered.copy()
            filtered["value"] = normalize_to_scale(filtered["value"])
        
        result[series_id] = filtered
    
    return result
