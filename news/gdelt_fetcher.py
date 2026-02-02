#!/usr/bin/env python3
"""
GDELT DOC 2.0 API Fetcher

Fetches news articles from GDELT API for any time window and keyword search.
Results are saved by day in JSON format.

Usage:
    python gdelt_fetcher.py --query "macro economy" --days 10
    python gdelt_fetcher.py --query "macro economy" --days 10 --lang english --country us
    python gdelt_fetcher.py --query "inflation" --start 20260120 --end 20260125
    python gdelt_fetcher.py --query "federal reserve" --days 7 --max-records 100
"""

import argparse
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import requests

# GDELT DOC 2.0 API endpoint
GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# Default output directory
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "data"


def parse_date(date_str: str) -> datetime:
    """Parse date string in YYYYMMDD or YYYYMMDDHHMMSS format."""
    if len(date_str) == 8:
        return datetime.strptime(date_str, "%Y%m%d")
    elif len(date_str) == 14:
        return datetime.strptime(date_str, "%Y%m%d%H%M%S")
    else:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYYMMDD or YYYYMMDDHHMMSS")


def format_datetime(dt: datetime) -> str:
    """Format datetime to GDELT API format (YYYYMMDDHHMMSS)."""
    return dt.strftime("%Y%m%d%H%M%S")


def fetch_gdelt_articles(
    query: str,
    start_datetime: str,
    end_datetime: str,
    max_records: int = 250,
    sort: str = "datedesc"
) -> list:
    """
    Fetch articles from GDELT DOC 2.0 API.
    
    Args:
        query: Search query (keywords, phrases, themes)
        start_datetime: Start time in YYYYMMDDHHMMSS format
        end_datetime: End time in YYYYMMDDHHMMSS format
        max_records: Maximum number of records (max 250)
        sort: Sort order (datedesc, dateasc, tonedesc, toneasc)
    
    Returns:
        List of article dictionaries
    """
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "startdatetime": start_datetime,
        "enddatetime": end_datetime,
        "maxrecords": min(max_records, 250),
        "sort": sort,
    }
    
    url = f"{GDELT_API_URL}?{urlencode(params)}"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        # GDELT returns articles in 'articles' key
        if isinstance(data, dict) and "articles" in data:
            return data["articles"]
        elif isinstance(data, list):
            return data
        else:
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from GDELT: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []


def fetch_articles_by_day(
    query: str,
    start_date: datetime,
    end_date: datetime,
    max_records_per_day: int = 250,
    output_dir: Optional[Path] = None,
    delay: float = 1.0
) -> dict:
    """
    Fetch articles for each day in the date range and save to separate files.
    
    Args:
        query: Search query
        start_date: Start date
        end_date: End date
        max_records_per_day: Max records per day
        output_dir: Output directory for JSON files
        delay: Delay between API calls in seconds
    
    Returns:
        Dictionary with date -> article count mapping
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    current_date = start_date
    
    # Create query-specific subdirectory (sanitize for filesystem)
    query_slug = query.lower().replace(" ", "_").replace('"', "").replace(":", "_")[:50]
    query_dir = output_dir / query_slug
    query_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Fetching articles for query: '{query}'")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Output directory: {query_dir}")
    print("-" * 60)
    
    while current_date <= end_date:
        day_start = current_date.replace(hour=0, minute=0, second=0)
        day_end = current_date.replace(hour=23, minute=59, second=59)
        
        # Don't fetch future dates
        now = datetime.now()
        if day_start > now:
            print(f"Skipping future date: {current_date.strftime('%Y-%m-%d')}")
            current_date += timedelta(days=1)
            continue
        
        if day_end > now:
            day_end = now
        
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Fetching {date_str}...", end=" ", flush=True)
        
        articles = fetch_gdelt_articles(
            query=query,
            start_datetime=format_datetime(day_start),
            end_datetime=format_datetime(day_end),
            max_records=max_records_per_day
        )
        
        article_count = len(articles)
        results[date_str] = article_count
        
        # Save to file
        output_file = query_dir / f"{date_str}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "query": query,
                "date": date_str,
                "fetch_time": datetime.now().isoformat(),
                "article_count": article_count,
                "articles": articles
            }, f, ensure_ascii=False, indent=2)
        
        print(f"{article_count} articles saved")
        
        current_date += timedelta(days=1)
        
        # Rate limiting - be polite to the API
        if current_date <= end_date:
            time.sleep(delay)
    
    print("-" * 60)
    total = sum(results.values())
    print(f"Total: {total} articles fetched across {len(results)} days")
    
    # Save summary
    summary_file = query_dir / "_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "query": query,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "fetch_time": datetime.now().isoformat(),
            "total_articles": total,
            "daily_counts": results
        }, f, ensure_ascii=False, indent=2)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Fetch news articles from GDELT DOC 2.0 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch last 10 days of macro economy news
  python gdelt_fetcher.py --query "macro economy" --days 10

  # Fetch only English news from US media
  python gdelt_fetcher.py --query "macro economy" --days 10 --lang english --country us

  # Fetch specific date range
  python gdelt_fetcher.py --query "inflation" --start 20260120 --end 20260125

  # Filter by specific domain
  python gdelt_fetcher.py --query "federal reserve" --days 7 --domain reuters.com

Query tips:
  - Use quotes for exact phrases: "macro economy"
  - Use OR for alternatives: (inflation OR deflation)
  - Use themes for topics: theme:ECON_INFLATION
  - Exclude with minus: economy -crypto

Language codes: english, chinese, spanish, french, german, japanese, etc.
Country codes: us, uk, china, germany, france, japan, canada, australia, etc.
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="Search query (keywords, phrases, or GDELT operators)"
    )
    
    parser.add_argument(
        "--days", "-d",
        type=int,
        help="Number of days to look back from today"
    )
    
    parser.add_argument(
        "--start", "-s",
        help="Start date (YYYYMMDD format)"
    )
    
    parser.add_argument(
        "--end", "-e",
        help="End date (YYYYMMDD format)"
    )
    
    parser.add_argument(
        "--max-records", "-m",
        type=int,
        default=250,
        help="Maximum records per day (max 250, default 250)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "--lang", "-l",
        help="Filter by source language (e.g., english, chinese, spanish)"
    )
    
    parser.add_argument(
        "--country", "-c",
        help="Filter by source country (e.g., us, uk, china, germany)"
    )
    
    parser.add_argument(
        "--domain",
        help="Filter by domain (e.g., reuters.com, bloomberg.com)"
    )
    
    args = parser.parse_args()
    
    # Determine date range
    if args.days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days - 1)
    elif args.start:
        start_date = parse_date(args.start)
        if args.end:
            end_date = parse_date(args.end)
        else:
            end_date = datetime.now()
    else:
        parser.error("Must specify either --days or --start date")
    
    # Validate date range (GDELT only has last 3 months)
    three_months_ago = datetime.now() - timedelta(days=90)
    if start_date < three_months_ago:
        print(f"Warning: GDELT API only supports last 3 months. Adjusting start date.")
        start_date = three_months_ago
    
    # Build query with filters
    query = args.query
    if args.lang:
        query += f" sourcelang:{args.lang}"
    if args.country:
        query += f" sourcecountry:{args.country}"
    if args.domain:
        query += f" domain:{args.domain}"
    
    # Fetch articles
    fetch_articles_by_day(
        query=query,
        start_date=start_date,
        end_date=end_date,
        max_records_per_day=args.max_records,
        output_dir=args.output,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
