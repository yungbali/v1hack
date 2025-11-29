# Data Fetching and Caching System

This directory contains the data fetching and processing infrastructure for the Africa Sovereign Debt Crisis Dashboard.

## Overview

The data system follows a **fetch → merge → cache** pipeline:

1. **Fetch**: Retrieve data from World Bank and IMF APIs
2. **Merge**: Combine API data with static creditor information
3. **Cache**: Save to parquet format for instant dashboard loading

## Files

- `fetch_data.py` - Main orchestrator for fetching and merging data
- `process_data.py` - Data cleaning utilities (forward-fill, etc.)
- `creditor_data.csv` - Static creditor composition data for 54 African countries
- `cached/` - Directory for cached parquet files

## Usage

### Fetch and Cache Data

```python
from data.fetch_data import fetch_and_cache_data

# Fetch all data and save to cache
data = fetch_and_cache_data()
```

### Load Cached Data

```python
from data.fetch_data import load_from_cache

# Load from cache (used by dashboard)
data = load_from_cache()
```

### Clean Data

```python
from data.process_data import clean_data

# Apply forward-fill for missing values
cleaned = clean_data(data, apply_forward_fill=True)
```

## Command Line Script

Use the provided script to fetch and cache data:

```bash
# Fetch all data
python scripts/fetch_and_cache_data.py

# Fetch specific countries
python scripts/fetch_and_cache_data.py --countries KEN,NGA,ZMB

# Fetch specific year range
python scripts/fetch_and_cache_data.py --years 2020-2024

# Skip IMF data
python scripts/fetch_and_cache_data.py --no-imf
```

## Data Schema

The cached parquet file contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| country_code | str | ISO 3-letter country code |
| country_name | str | Full country name |
| year | int | Year (2014-2024) |
| debt_to_gdp | float | Public debt as % of GDP |
| total_debt_usd | float | Total external debt stock (USD) |
| debt_service_usd | float | Annual debt service payments (USD) |
| gdp_usd | float | GDP in current USD |
| revenue_pct_gdp | float | Government revenue as % of GDP |
| health_pct_gdp | float | Health expenditure as % of GDP |
| education_pct_gdp | float | Education expenditure as % of GDP |
| creditor_multilateral_pct | float | % of debt owed to multilateral creditors |
| creditor_bilateral_pct | float | % of debt owed to bilateral creditors |
| creditor_commercial_pct | float | % of debt owed to commercial creditors |
| avg_interest_rate | float | Weighted average interest rate (%) |
| avg_maturity_years | int | Weighted average maturity (years) |

## API Sources

### World Bank API

- **Endpoint**: `https://api.worldbank.org/v2/country/{country}/indicator/{indicator}`
- **Indicators**: Debt, GDP, revenue, health, education spending
- **Coverage**: 54 African countries, 2014-2024

### IMF API

- **Endpoint**: `https://www.imf.org/external/datamapper/api/v1/{indicator}/{country}`
- **Indicators**: GDP growth, government debt, inflation
- **Coverage**: 54 African countries, 2014-2024

## Error Handling

The system includes robust error handling:

- **Retry Logic**: Exponential backoff for failed API requests (3 attempts)
- **Partial Data**: Continues with available data if some requests fail
- **Missing Values**: Forward-fill for gaps ≤2 years, larger gaps remain null
- **Logging**: Prints progress and errors to console

## Performance

- **API Calls**: ~500 requests total (with rate limiting)
- **Fetch Time**: ~5-10 minutes for full dataset
- **Cache Size**: ~1-2 MB parquet file
- **Load Time**: <1 second from cache

## Notes

- Run the fetch script **before** deploying the dashboard
- The dashboard loads from cache only (no live API calls)
- Refresh data periodically (monthly/quarterly) as needed
- Creditor data is static and may need manual updates
