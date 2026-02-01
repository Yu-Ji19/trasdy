"""CSV and JSON implementations of repository interfaces."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional
import pandas as pd

from src.repositories.base import SeriesRepository, MetadataRepository
from config.settings import get_project_root


class CSVSeriesRepository(SeriesRepository):
    """CSV-based implementation of SeriesRepository."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the repository.
        
        Args:
            data_dir: Directory for CSV files. Defaults to data/raw/
        """
        if data_dir is None:
            data_dir = get_project_root() / "data" / "raw"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, series_id: str) -> Path:
        """Get the CSV file path for a series."""
        return self.data_dir / f"{series_id}.csv"
    
    def read(
        self, 
        series_id: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Read time series data from CSV."""
        file_path = self._get_file_path(series_id)
        
        if not file_path.exists():
            return pd.DataFrame(columns=["date", "value"])
        
        df = pd.read_csv(file_path, parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"]).dt.date
        
        # Apply date filters
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
        """Write time series data to CSV."""
        file_path = self._get_file_path(series_id)
        
        if data.empty:
            return 0
        
        # Ensure proper columns
        if "date" not in data.columns or "value" not in data.columns:
            raise ValueError("DataFrame must have 'date' and 'value' columns")
        
        # Normalize date column
        df = data.copy()
        df["date"] = pd.to_datetime(df["date"]).dt.date
        
        if mode == "append" and file_path.exists():
            existing = self.read(series_id)
            # Combine and remove duplicates (keep new data)
            combined = pd.concat([existing, df], ignore_index=True)
            combined = combined.drop_duplicates(subset=["date"], keep="last")
            df = combined.sort_values("date").reset_index(drop=True)
        
        df.to_csv(file_path, index=False)
        return len(df)
    
    def exists(self, series_id: str) -> bool:
        """Check if series CSV file exists."""
        return self._get_file_path(series_id).exists()
    
    def get_date_range(self, series_id: str) -> tuple[Optional[date], Optional[date]]:
        """Get the date range of stored data."""
        if not self.exists(series_id):
            return (None, None)
        
        df = self.read(series_id)
        if df.empty:
            return (None, None)
        
        return (df["date"].min(), df["date"].max())


class JSONMetadataRepository(MetadataRepository):
    """JSON file-based implementation of MetadataRepository."""
    
    def __init__(self, metadata_file: Optional[Path] = None):
        """Initialize the repository.
        
        Args:
            metadata_file: Path to metadata JSON file. Defaults to data/metadata.json
        """
        if metadata_file is None:
            metadata_file = get_project_root() / "data" / "metadata.json"
        self.metadata_file = metadata_file
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> dict[str, dict]:
        """Load metadata from file."""
        if not self.metadata_file.exists():
            return {}
        
        with open(self.metadata_file, "r") as f:
            return json.load(f)
    
    def _save(self, data: dict[str, dict]) -> None:
        """Save metadata to file."""
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def get(self, series_id: str) -> Optional[dict]:
        """Get metadata for a series."""
        all_metadata = self._load()
        return all_metadata.get(series_id)
    
    def update(self, series_id: str, updates: dict) -> None:
        """Update metadata for a series."""
        all_metadata = self._load()
        
        if series_id not in all_metadata:
            all_metadata[series_id] = {}
        
        all_metadata[series_id].update(updates)
        self._save(all_metadata)
    
    def get_all(self) -> dict[str, dict]:
        """Get all metadata."""
        return self._load()
