"""
Data fetching orchestrator for combining World Bank, IMF, and creditor data
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from utils.api_client import fetch_world_bank_data, fetch_imf_data
from utils.constants import AFRICAN_COUNTRIES


def merge_datasets(
    wb_data: pd.DataFrame,
    imf_data: pd.DataFrame,
    creditor_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge World Bank, IMF, and static creditor data into unified dataset.
    
    Uses outer joins to preserve all country data. Handles duplicate keys by
    preferring most recent data (World Bank over IMF when conflicts occur).
    
    Args:
        wb_data: DataFrame from World Bank API with columns:
                 country_code, country_name, year, indicator_code, indicator_name, value
        imf_data: DataFrame from IMF API with same structure
        creditor_data: DataFrame from CSV with columns:
                       country_code, creditor_multilateral_pct, creditor_bilateral_pct,
                       creditor_commercial_pct, avg_interest_rate, avg_maturity_years
    
    Returns:
        DataFrame with columns: country_code, country_name, year, debt_to_gdp,
        total_debt_usd, debt_service_usd, gdp_usd, revenue_pct_gdp, health_pct_gdp,
        education_pct_gdp, creditor_multilateral_pct, creditor_bilateral_pct,
        creditor_commercial_pct, avg_interest_rate, avg_maturity_years
    """
    # Pivot World Bank data from long to wide format
    if not wb_data.empty:
        wb_wide = wb_data.pivot_table(
            index=['country_code', 'country_name', 'year'],
            columns='indicator_name',
            values='value',
            aggfunc='first'  # Take first value if duplicates
        ).reset_index()
    else:
        # Create empty DataFrame with expected structure
        wb_wide = pd.DataFrame(columns=['country_code', 'country_name', 'year'])
    
    # Pivot IMF data from long to wide format
    if not imf_data.empty:
        imf_wide = imf_data.pivot_table(
            index=['country_code', 'country_name', 'year'],
            columns='indicator_name',
            values='value',
            aggfunc='first'
        ).reset_index()
    else:
        imf_wide = pd.DataFrame(columns=['country_code', 'country_name', 'year'])
    
    # Merge World Bank and IMF data (outer join to preserve all data)
    if not wb_wide.empty and not imf_wide.empty:
        merged = pd.merge(
            wb_wide,
            imf_wide,
            on=['country_code', 'country_name', 'year'],
            how='outer',
            suffixes=('', '_imf')
        )
    elif not wb_wide.empty:
        merged = wb_wide
    elif not imf_wide.empty:
        merged = imf_wide
    else:
        # Both empty - create minimal structure
        merged = pd.DataFrame(columns=['country_code', 'country_name', 'year'])
    
    # Merge with creditor data (left join to preserve all year data)
    if not creditor_data.empty:
        merged = pd.merge(
            merged,
            creditor_data,
            on='country_code',
            how='left'
        )
    
    # Ensure all expected columns exist (fill with NaN if missing)
    expected_columns = [
        'country_code', 'country_name', 'year',
        'debt_to_gdp', 'external_debt_stock', 'debt_service_usd',
        'gdp_usd', 'revenue_pct_gdp', 'health_pct_gdp', 'education_pct_gdp',
        'creditor_multilateral_pct', 'creditor_bilateral_pct', 'creditor_commercial_pct',
        'avg_interest_rate', 'avg_maturity_years'
    ]
    
    for col in expected_columns:
        if col not in merged.columns:
            merged[col] = None
    
    # Rename external_debt_stock to total_debt_usd for consistency
    if 'external_debt_stock' in merged.columns:
        merged['total_debt_usd'] = merged['external_debt_stock']
    
    # Select and order final columns
    final_columns = [
        'country_code', 'country_name', 'year',
        'debt_to_gdp', 'total_debt_usd', 'debt_service_usd',
        'gdp_usd', 'revenue_pct_gdp', 'health_pct_gdp', 'education_pct_gdp',
        'creditor_multilateral_pct', 'creditor_bilateral_pct', 'creditor_commercial_pct',
        'avg_interest_rate', 'avg_maturity_years'
    ]
    
    # Keep only columns that exist
    final_columns = [col for col in final_columns if col in merged.columns]
    merged = merged[final_columns]
    
    # Sort by country and year
    merged = merged.sort_values(['country_code', 'year']).reset_index(drop=True)
    
    return merged


def fetch_all_data(
    countries: Optional[list] = None,
    years: Optional[range] = None,
    fetch_wb: bool = True,
    fetch_imf: bool = True
) -> pd.DataFrame:
    """
    Main orchestrator: fetch all data from APIs, merge, and return unified dataset.
    
    Args:
        countries: List of country codes to fetch (defaults to all African countries)
        years: Range of years to fetch (defaults to 2014-2024)
        fetch_wb: Whether to fetch World Bank data
        fetch_imf: Whether to fetch IMF data
    
    Returns:
        Merged DataFrame ready for caching
    """
    print("Starting data fetch process...")
    
    # Fetch World Bank data
    if fetch_wb:
        print("Fetching World Bank data...")
        wb_data = fetch_world_bank_data(countries=countries, years=years)
        print(f"Fetched {len(wb_data)} World Bank records")
    else:
        wb_data = pd.DataFrame()
    
    # Fetch IMF data
    if fetch_imf:
        print("Fetching IMF data...")
        imf_data = fetch_imf_data(countries=countries, years=years)
        print(f"Fetched {len(imf_data)} IMF records")
    else:
        imf_data = pd.DataFrame()
    
    # Load creditor data from CSV
    print("Loading creditor data...")
    creditor_file = Path("data/creditor_data.csv")
    if creditor_file.exists():
        creditor_data = pd.read_csv(creditor_file)
        print(f"Loaded creditor data for {len(creditor_data)} countries")
    else:
        print("Warning: creditor_data.csv not found")
        creditor_data = pd.DataFrame()
    
    # Merge all datasets
    print("Merging datasets...")
    merged_data = merge_datasets(wb_data, imf_data, creditor_data)
    print(f"Merged dataset contains {len(merged_data)} records")
    
    return merged_data



def save_to_cache(
    data: pd.DataFrame,
    cache_path: str = "data/cached/dashboard_data.parquet"
) -> None:
    """
    Save merged dataset to parquet cache with timestamp metadata.
    
    Args:
        data: DataFrame to cache
        cache_path: Path to save parquet file
    """
    from datetime import datetime
    
    # Ensure cache directory exists
    cache_file = Path(cache_path)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Add timestamp as metadata
    # Note: Parquet metadata is stored at the file level
    print(f"Saving data to {cache_path}...")
    data.to_parquet(
        cache_path,
        index=False,
        engine='pyarrow'
    )
    
    # Save timestamp in a separate metadata file
    timestamp_file = cache_file.parent / "last_refresh.txt"
    with open(timestamp_file, 'w') as f:
        f.write(datetime.now().isoformat())
    
    print(f"Data cached successfully. Records: {len(data)}")
    print(f"Timestamp saved to {timestamp_file}")


def load_from_cache(
    cache_path: str = "data/cached/dashboard_data.parquet"
) -> pd.DataFrame:
    """
    Load data from parquet cache.
    
    Args:
        cache_path: Path to parquet file
    
    Returns:
        Cached DataFrame
    """
    cache_file = Path(cache_path)
    
    if not cache_file.exists():
        raise FileNotFoundError(f"Cache file not found: {cache_path}")
    
    print(f"Loading data from {cache_path}...")
    data = pd.read_parquet(cache_path)
    print(f"Loaded {len(data)} records from cache")
    
    # Try to load timestamp
    timestamp_file = cache_file.parent / "last_refresh.txt"
    if timestamp_file.exists():
        with open(timestamp_file, 'r') as f:
            timestamp = f.read().strip()
        print(f"Data last refreshed: {timestamp}")
    
    return data


def fetch_and_cache_data(
    countries: Optional[list] = None,
    years: Optional[range] = None,
    cache_path: str = "data/cached/dashboard_data.parquet",
    fetch_wb: bool = True,
    fetch_imf: bool = True
) -> pd.DataFrame:
    """
    Fetch all data and save to cache in one operation.
    
    Args:
        countries: List of country codes to fetch
        years: Range of years to fetch
        cache_path: Path to save parquet file
        fetch_wb: Whether to fetch World Bank data
        fetch_imf: Whether to fetch IMF data
    
    Returns:
        Merged and cached DataFrame
    """
    # Fetch all data
    data = fetch_all_data(
        countries=countries,
        years=years,
        fetch_wb=fetch_wb,
        fetch_imf=fetch_imf
    )
    
    # Save to cache
    save_to_cache(data, cache_path)
    
    return data
