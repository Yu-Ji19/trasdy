"""Trasdy MVP 的配置设置。"""

from pathlib import Path
import yaml


def get_project_root() -> Path:
    """获取项目根目录。"""
    return Path(__file__).parent.parent


def get_api_key() -> str:
    """从文件读取 FRED API 密钥。
    
    Returns:
        str: FRED API 密钥
        
    Raises:
        FileNotFoundError: 如果 FRED_API_KEY 文件不存在
        ValueError: 如果 FRED_API_KEY 文件为空
    """
    key_file = get_project_root() / "secrets" / "FRED_API_KEY"
    
    if not key_file.exists():
        raise FileNotFoundError(f"FRED_API_KEY file not found at {key_file}")
    
    api_key = key_file.read_text().strip()
    if not api_key:
        raise ValueError("FRED_API_KEY file is empty. Please add your API key.")
    
    return api_key


def load_series_config() -> list[dict]:
    """从 YAML 文件加载系列配置。
    
    Returns:
        list[dict]: 系列配置列表
    """
    config_file = get_project_root() / "config" / "series_config.yaml"
    
    if not config_file.exists():
        raise FileNotFoundError(f"Series config file not found at {config_file}")
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    return config.get("series", [])
