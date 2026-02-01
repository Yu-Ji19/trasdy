#!/usr/bin/env python3
"""Test FRED API connectivity by fetching SP500 data."""

import os
import requests
from pathlib import Path


def get_api_key() -> str:
    """Read FRED API key from file."""
    # Find project root (where FRED_API_KEY file is located)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    key_file = project_root / "FRED_API_KEY"
    
    if not key_file.exists():
        raise FileNotFoundError(f"FRED_API_KEY file not found at {key_file}")
    
    api_key = key_file.read_text().strip()
    if not api_key:
        raise ValueError("FRED_API_KEY file is empty. Please add your API key.")
    
    return api_key


def fetch_sp500_data(api_key: str, limit: int = 10) -> list[dict]:
    """Fetch recent SP500 data from FRED API."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "SP500",
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    observations = data.get("observations", [])
    
    return observations


def main():
    """Main function to test FRED API."""
    print("Testing FRED API connection...")
    print("-" * 40)
    
    # Get API key
    api_key = get_api_key()
    print(f"API key loaded: {api_key[:4]}...{api_key[-4:]}")
    
    # Fetch data
    print("\nFetching SP500 last 10 observations...")
    observations = fetch_sp500_data(api_key, limit=10)
    
    # Print results
    print(f"\nReceived {len(observations)} records:")
    print("-" * 40)
    for obs in observations:
        date = obs.get("date", "N/A")
        value = obs.get("value", "N/A")
        print(f"{date}: {value}")
    
    print("-" * 40)
    print("FRED API test completed successfully!")


if __name__ == "__main__":
    main()
