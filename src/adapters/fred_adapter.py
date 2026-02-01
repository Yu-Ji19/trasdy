"""FRED API adapter implementation."""

from datetime import date
from typing import Optional
import requests
import pandas as pd

from src.adapters.base import DataSourceAdapter
from config.settings import get_api_key


class FREDAdapter(DataSourceAdapter):
    """Adapter for Federal Reserve Economic Data (FRED) API."""
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the FRED adapter.
        
        Args:
            api_key: FRED API key. If not provided, reads from FRED_API_KEY file.
        """
        self._api_key = api_key
    
    @property
    def api_key(self) -> str:
        """Get the API key, loading from file if needed."""
        if self._api_key is None:
            self._api_key = get_api_key()
        return self._api_key
    
    def fetch(
        self, 
        series_id: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Fetch time series data from FRED API.
        
        Args:
            series_id: FRED series ID (e.g., 'SP500', 'DGS10')
            start_date: Optional start date for the data (date object or 'YYYY-MM-DD' string)
            end_date: Optional end date for the data (date object or 'YYYY-MM-DD' string)
            
        Returns:
            DataFrame with columns ['date', 'value']
        """
        url = f"{self.BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }
        
        if start_date:
            # Handle both date objects and string inputs
            params["observation_start"] = start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date
        if end_date:
            params["observation_end"] = end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        observations = data.get("observations", [])
        
        # Parse observations into DataFrame
        rows = []
        for obs in observations:
            value_str = obs.get("value", "")
            # Skip missing values (FRED uses "." for missing)
            if value_str == "." or value_str == "":
                continue
            
            try:
                rows.append({
                    "date": obs["date"],
                    "value": float(value_str)
                })
            except (ValueError, KeyError):
                # Skip rows that can't be parsed
                continue
        
        if not rows:
            return pd.DataFrame(columns=["date", "value"])
        
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df.sort_values("date").reset_index(drop=True)
    
    def get_metadata(self, series_id: str) -> dict:
        """Get metadata for a FRED series.
        
        Args:
            series_id: FRED series ID
            
        Returns:
            Dictionary containing series metadata
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
