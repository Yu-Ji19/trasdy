"""Abstract base classes for data repositories."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Any
import pandas as pd


class SeriesRepository(ABC):
    """Abstract base class for time series data storage."""
    
    @abstractmethod
    def read(
        self, 
        series_id: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Read time series data.
        
        Args:
            series_id: Identifier for the series
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            DataFrame with columns ['date', 'value']
        """
        pass
    
    @abstractmethod
    def write(
        self, 
        series_id: str, 
        data: pd.DataFrame, 
        mode: str = "replace"
    ) -> int:
        """Write time series data.
        
        Args:
            series_id: Identifier for the series
            data: DataFrame with columns ['date', 'value']
            mode: 'replace' to overwrite, 'append' to add new data
            
        Returns:
            Number of rows written
        """
        pass
    
    @abstractmethod
    def exists(self, series_id: str) -> bool:
        """Check if series data exists.
        
        Args:
            series_id: Identifier for the series
            
        Returns:
            True if data exists
        """
        pass
    
    @abstractmethod
    def get_date_range(self, series_id: str) -> tuple[Optional[date], Optional[date]]:
        """Get the date range of stored data.
        
        Args:
            series_id: Identifier for the series
            
        Returns:
            Tuple of (start_date, end_date) or (None, None) if no data
        """
        pass


class MetadataRepository(ABC):
    """Abstract base class for metadata storage."""
    
    @abstractmethod
    def get(self, series_id: str) -> Optional[dict]:
        """Get metadata for a series.
        
        Args:
            series_id: Identifier for the series
            
        Returns:
            Metadata dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def update(self, series_id: str, updates: dict) -> None:
        """Update metadata for a series.
        
        Args:
            series_id: Identifier for the series
            updates: Dictionary of fields to update
        """
        pass
    
    @abstractmethod
    def get_all(self) -> dict[str, dict]:
        """Get all metadata.
        
        Returns:
            Dictionary mapping series_id to metadata
        """
        pass
