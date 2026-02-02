#!/usr/bin/env python3
"""通过获取 SP500 数据测试 FRED API 连接。"""

import os
import requests
from pathlib import Path


def get_api_key() -> str:
    """从文件读取 FRED API 密钥。"""
    # 查找项目根目录（FRED_API_KEY 文件所在位置）
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    key_file = project_root / "secrets" / "FRED_API_KEY"
    
    if not key_file.exists():
        raise FileNotFoundError(f"FRED_API_KEY file not found at {key_file}")
    
    api_key = key_file.read_text().strip()
    if not api_key:
        raise ValueError("FRED_API_KEY file is empty. Please add your API key.")
    
    return api_key


def fetch_sp500_data(api_key: str, limit: int = 10) -> list[dict]:
    """从 FRED API 获取最近的 SP500 数据。"""
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
    """测试 FRED API 的主函数。"""
    print("Testing FRED API connection...")
    print("-" * 40)
    
    # 获取 API 密钥
    api_key = get_api_key()
    print(f"API key loaded: {api_key[:4]}...{api_key[-4:]}")
    
    # 获取数据
    print("\nFetching SP500 last 10 observations...")
    observations = fetch_sp500_data(api_key, limit=10)
    
    # 打印结果
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
