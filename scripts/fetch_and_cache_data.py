#!/usr/bin/env python3
"""
Script to fetch data from World Bank and IMF APIs and cache it locally.

This script should be run before deploying the dashboard to ensure
data is available without requiring live API calls.

Usage:
    python scripts/fetch_and_cache_data.py
    
    # Or fetch only specific countries/years:
    python scripts/fetch_and_cache_data.py --countries KEN,NGA --years 2020-2024
"""

import argparse
from data.fetch_data import fetch_and_cache_data
from data.process_data import clean_data
from utils.constants import AFRICAN_COUNTRIES


def main():
    parser = argparse.ArgumentParser(description='Fetch and cache dashboard data')
    parser.add_argument(
        '--countries',
        type=str,
        help='Comma-separated list of country codes (default: all African countries)'
    )
    parser.add_argument(
        '--years',
        type=str,
        help='Year range in format START-END (default: 2014-2024)'
    )
    parser.add_argument(
        '--no-wb',
        action='store_true',
        help='Skip World Bank API fetch'
    )
    parser.add_argument(
        '--no-imf',
        action='store_true',
        help='Skip IMF API fetch'
    )
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Skip data cleaning (forward-fill)'
    )
    
    args = parser.parse_args()
    
    # Parse countries
    countries = None
    if args.countries:
        countries = [c.strip() for c in args.countries.split(',')]
        print(f"Fetching data for countries: {countries}")
    else:
        print(f"Fetching data for all {len(AFRICAN_COUNTRIES)} African countries")
    
    # Parse years
    years = None
    if args.years:
        start, end = args.years.split('-')
        years = range(int(start), int(end) + 1)
        print(f"Fetching data for years: {start}-{end}")
    else:
        print("Fetching data for years: 2014-2024")
    
    # Fetch and cache data
    print("\n" + "="*60)
    print("Starting data fetch process...")
    print("="*60 + "\n")
    
    data = fetch_and_cache_data(
        countries=countries,
        years=years,
        fetch_wb=not args.no_wb,
        fetch_imf=not args.no_imf
    )
    
    # Clean data if requested
    if not args.no_clean:
        print("\nApplying data cleaning (forward-fill)...")
        data = clean_data(data, apply_forward_fill=True)
        
        # Re-save cleaned data
        from data.fetch_data import save_to_cache
        save_to_cache(data)
    
    print("\n" + "="*60)
    print("Data fetch complete!")
    print("="*60)
    print(f"\nFinal dataset:")
    print(f"  - Records: {len(data)}")
    print(f"  - Countries: {data['country_code'].nunique()}")
    print(f"  - Years: {data['year'].min()}-{data['year'].max()}")
    print(f"  - Columns: {len(data.columns)}")
    print(f"\nData saved to: data/cached/dashboard_data.parquet")
    print("\nYou can now run the dashboard with: streamlit run app.py")


if __name__ == '__main__':
    main()
