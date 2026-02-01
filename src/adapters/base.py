"""Abstract base class for data source adapters."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
import pandas as pd


class DataSourceAdapter(ABC):
    """Abstract base class for external data source adapters."""
    
    @abstractmethod
    def fetch(
        self, 
        series_id: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Fetch time series data from the data source.
        
        Args:
            series_id: The identifier for the data series
            start_date: Optional start date for the data
            end_date: Optional end date for the data
            
        Returns:
            DataFrame with columns ['date', 'value']
        """
        pass
    
    @abstractmethod
    def get_metadata(self, series_id: str) -> dict:
        """Get metadata for a series.
        
        Args:
            series_id: The identifier for the data series
            
        Returns:
            Dictionary containing series metadata
        """
        pass
