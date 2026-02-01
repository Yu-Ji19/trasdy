"""Data service for managing series data and synchronization."""

from datetime import date, timedelta
from enum import Enum
from typing import Optional
import pandas as pd

from src.repositories.base import SeriesRepository, MetadataRepository
from src.adapters.fred_adapter import FREDAdapter
from config.settings import load_series_config


class RefreshMode(Enum):
    """Data refresh mode."""
    FULL = "full"
    INCREMENTAL = "incremental"


class DataService:
    """Service for managing time series data.
    
    Handles data retrieval, caching, and synchronization with external sources.
    Uses dependency injection for repositories.
    """
    
    def __init__(
        self, 
        series_repo: SeriesRepository, 
        metadata_repo: MetadataRepository,
        adapter: Optional[FREDAdapter] = None
    ):
        """Initialize the data service.
        
        Args:
            series_repo: Repository for series data storage
            metadata_repo: Repository for metadata storage
            adapter: Data source adapter (defaults to FREDAdapter)
        """
        self.series_repo = series_repo
        self.metadata_repo = metadata_repo
        self.adapter = adapter or FREDAdapter()
        self._series_config = {s["id"]: s for s in load_series_config()}
    
    def _get_fred_series_id(self, series_id: str) -> str:
        """Get the FRED series ID for a local series ID."""
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
        """Get time series data.
        
        If data exists locally, reads from CSV. Otherwise fetches from API
        and saves locally.
        
        Args:
            series_ids: List of series identifiers
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary mapping series_id to DataFrame
        """
        result = {}
        
        for series_id in series_ids:
            if self.series_repo.exists(series_id):
                # Read from local storage
                df = self.series_repo.read(series_id, start_date, end_date)
            else:
                # Fetch from API and save
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
        """Refresh data from the external source.
        
        Args:
            series_ids: List of series to refresh
            mode: FULL to replace all data, INCREMENTAL to append new data
            
        Returns:
            Dictionary mapping series_id to number of new records
        """
        result = {}
        
        for series_id in series_ids:
            fred_id = self._get_fred_series_id(series_id)
            
            if mode == RefreshMode.FULL:
                # Full refresh - fetch all and replace
                df = self.adapter.fetch(fred_id)
                if not df.empty:
                    rows_written = self.series_repo.write(series_id, df, mode="replace")
                    self._update_metadata_after_write(series_id, df)
                    result[series_id] = rows_written
                else:
                    result[series_id] = 0
            else:
                # Incremental refresh - fetch only new data
                metadata = self.metadata_repo.get(series_id)
                
                if metadata and metadata.get("data_end_date"):
                    # Parse the stored date
                    end_date_str = metadata["data_end_date"]
                    if isinstance(end_date_str, str):
                        last_date = date.fromisoformat(end_date_str)
                    else:
                        last_date = end_date_str
                    start_date = last_date + timedelta(days=1)
                else:
                    # No existing data, fetch all
                    start_date = None
                
                df = self.adapter.fetch(fred_id, start_date=start_date)
                
                if not df.empty:
                    rows_written = self.series_repo.write(series_id, df, mode="append")
                    # Re-read to get full date range for metadata
                    full_df = self.series_repo.read(series_id)
                    self._update_metadata_after_write(series_id, full_df)
                    result[series_id] = len(df)
                else:
                    result[series_id] = 0
        
        return result
    
    def _update_metadata_after_write(self, series_id: str, df: pd.DataFrame) -> None:
        """Update metadata after writing data.
        
        Args:
            series_id: The series identifier
            df: The DataFrame that was written
        """
        if df.empty:
            return
        
        # Get date range
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
        """Get all configured series IDs."""
        return list(self._series_config.keys())
