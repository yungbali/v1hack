"""
API client for fetching data from World Bank and IMF APIs
"""

import requests
import pandas as pd
import time
from typing import List, Dict, Optional
from utils.constants import AFRICAN_COUNTRIES, WB_INDICATORS, IMF_INDICATORS


def fetch_world_bank_data(
    countries: Optional[List[str]] = None,
    indicators: Optional[List[str]] = None,
    years: Optional[range] = None,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> pd.DataFrame:
    """
    Fetch indicators from World Bank API for specified countries and years.
    
    Args:
        countries: List of ISO 3-letter country codes (defaults to all African countries)
        indicators: List of World Bank indicator codes (defaults to all WB_INDICATORS)
        years: Range of years to fetch (defaults to 2014-2024)
        max_retries: Maximum number of retry attempts for failed requests
        backoff_factor: Exponential backoff multiplier for retries
    
    Returns:
        DataFrame with columns: country_code, country_name, year, indicator_code, 
        indicator_name, value
    """
    # Set defaults
    if countries is None:
        countries = list(AFRICAN_COUNTRIES.keys())
    if indicators is None:
        indicators = list(WB_INDICATORS.keys())
    if years is None:
        years = range(2014, 2025)  # 2014-2024 inclusive
    
    year_start = min(years)
    year_end = max(years)
    
    all_data = []
    
    # Fetch data for each country and indicator combination
    for country_code in countries:
        for indicator_code in indicators:
            url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
            params = {
                'date': f'{year_start}:{year_end}',
                'format': 'json',
                'per_page': 500
            }
            
            # Retry logic with exponential backoff
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    # Parse JSON response
                    data = response.json()
                    
                    # World Bank API returns array with metadata in first element
                    if isinstance(data, list) and len(data) > 1 and data[1]:
                        for record in data[1]:
                            if record.get('value') is not None:
                                all_data.append({
                                    'country_code': country_code,
                                    'country_name': AFRICAN_COUNTRIES.get(country_code, country_code),
                                    'year': int(record['date']),
                                    'indicator_code': indicator_code,
                                    'indicator_name': WB_INDICATORS.get(indicator_code, indicator_code),
                                    'value': float(record['value'])
                                })
                    
                    # Success - break retry loop
                    break
                    
                except (requests.RequestException, ValueError, KeyError) as e:
                    if attempt < max_retries - 1:
                        # Calculate backoff time
                        wait_time = backoff_factor ** attempt
                        print(f"Error fetching {country_code}/{indicator_code} (attempt {attempt + 1}/{max_retries}): {e}")
                        print(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        # Final attempt failed - log and continue
                        print(f"Failed to fetch {country_code}/{indicator_code} after {max_retries} attempts: {e}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
    
    # Convert to DataFrame
    if all_data:
        df = pd.DataFrame(all_data)
        return df
    else:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            'country_code', 'country_name', 'year', 'indicator_code', 
            'indicator_name', 'value'
        ])


def fetch_imf_data(
    countries: Optional[List[str]] = None,
    indicators: Optional[List[str]] = None,
    years: Optional[range] = None,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> pd.DataFrame:
    """
    Fetch indicators from IMF API for specified countries and years.
    
    Note: IMF API has a different structure than World Bank API.
    The endpoint format is: /api/v1/{indicator}/{country}
    
    Args:
        countries: List of ISO 3-letter country codes (defaults to all African countries)
        indicators: List of IMF indicator codes (defaults to all IMF_INDICATORS)
        years: Range of years to fetch (defaults to 2014-2024)
        max_retries: Maximum number of retry attempts for failed requests
        backoff_factor: Exponential backoff multiplier for retries
    
    Returns:
        DataFrame with columns: country_code, country_name, year, indicator_code,
        indicator_name, value
    """
    # Set defaults
    if countries is None:
        countries = list(AFRICAN_COUNTRIES.keys())
    if indicators is None:
        indicators = list(IMF_INDICATORS.keys())
    if years is None:
        years = range(2014, 2025)  # 2014-2024 inclusive
    
    year_set = set(years)
    all_data = []
    
    # Fetch data for each indicator
    for indicator_code in indicators:
        # IMF API accepts multiple countries in one request
        country_list = ','.join(countries)
        url = f"https://www.imf.org/external/datamapper/api/v1/{indicator_code}/{country_list}"
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                
                # IMF API structure: {"values": {"INDICATOR": {"COUNTRY": {"YEAR": value}}}}
                if 'values' in data and indicator_code in data['values']:
                    indicator_data = data['values'][indicator_code]
                    
                    for country_code, year_values in indicator_data.items():
                        if country_code in AFRICAN_COUNTRIES:
                            for year_str, value in year_values.items():
                                try:
                                    year = int(year_str)
                                    if year in year_set and value is not None:
                                        all_data.append({
                                            'country_code': country_code,
                                            'country_name': AFRICAN_COUNTRIES[country_code],
                                            'year': year,
                                            'indicator_code': indicator_code,
                                            'indicator_name': IMF_INDICATORS.get(indicator_code, indicator_code),
                                            'value': float(value)
                                        })
                                except (ValueError, TypeError):
                                    # Skip invalid year or value
                                    continue
                
                # Success - break retry loop
                break
                
            except (requests.RequestException, ValueError, KeyError) as e:
                if attempt < max_retries - 1:
                    # Calculate backoff time
                    wait_time = backoff_factor ** attempt
                    print(f"Error fetching IMF indicator {indicator_code} (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed - log and continue
                    print(f"Failed to fetch IMF indicator {indicator_code} after {max_retries} attempts: {e}")
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    # Convert to DataFrame
    if all_data:
        df = pd.DataFrame(all_data)
        return df
    else:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            'country_code', 'country_name', 'year', 'indicator_code',
            'indicator_name', 'value'
        ])
