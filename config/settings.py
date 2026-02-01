"""Configuration settings for Trasdy MVP."""

from pathlib import Path
import yaml


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_api_key() -> str:
    """Read FRED API key from file.
    
    Returns:
        str: The FRED API key
        
    Raises:
        FileNotFoundError: If FRED_API_KEY file doesn't exist
        ValueError: If FRED_API_KEY file is empty
    """
    key_file = get_project_root() / "secrets" / "FRED_API_KEY"
    
    if not key_file.exists():
        raise FileNotFoundError(f"FRED_API_KEY file not found at {key_file}")
    
    api_key = key_file.read_text().strip()
    if not api_key:
        raise ValueError("FRED_API_KEY file is empty. Please add your API key.")
    
    return api_key


def load_series_config() -> list[dict]:
    """Load series configuration from YAML file.
    
    Returns:
        list[dict]: List of series configurations
    """
    config_file = get_project_root() / "config" / "series_config.yaml"
    
    if not config_file.exists():
        raise FileNotFoundError(f"Series config file not found at {config_file}")
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    return config.get("series", [])
