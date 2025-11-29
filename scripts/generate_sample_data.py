"""
Generate realistic sample data for the Africa Debt Dashboard.

This script creates mock data for all 54 African countries covering years 2014-2024
with realistic values for debt metrics, GDP, and social spending.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path to import constants
sys.path.append(str(Path(__file__).parent.parent))
from utils.constants import AFRICAN_COUNTRIES, REGIONS, YEAR_START, YEAR_END


def get_region_for_country(country_code):
    """Get the region for a given country code."""
    for region, countries in REGIONS.items():
        if country_code in countries:
            return region
    return 'Unknown'


def generate_sample_data():
    """
    Generate realistic sample data for all 54 African countries.
    
    Returns:
        pd.DataFrame: Complete dataset with all required columns
    """
    np.random.seed(42)  # For reproducibility
    
    data = []
    years = range(YEAR_START, YEAR_END + 1)
    
    for country_code, country_name in AFRICAN_COUNTRIES.items():
        region = get_region_for_country(country_code)
        
        # Generate base characteristics for each country (consistent across years)
        # GDP base (in billions USD) - varies by country size
        gdp_base = np.random.uniform(5, 500)
        
        # Debt-to-GDP base ratio (%) - some countries have higher debt
        debt_to_gdp_base = np.random.uniform(20, 120)
        
        # Growth trend
        growth_trend = np.random.uniform(-0.5, 1.5)
        
        for year in years:
            # Year index for trends
            year_idx = year - YEAR_START
            
            # GDP grows over time with some variation
            gdp_growth = np.random.uniform(-2, 8)
            gdp_usd = gdp_base * (1 + growth_trend/100) ** year_idx * 1e9
            gdp_usd += np.random.normal(0, gdp_usd * 0.05)  # Add noise
            
            # Debt-to-GDP ratio with trend and variation
            debt_to_gdp = debt_to_gdp_base + year_idx * np.random.uniform(-2, 3)
            debt_to_gdp += np.random.normal(0, 5)  # Add noise
            debt_to_gdp = max(10, min(150, debt_to_gdp))  # Clamp to realistic range
            
            # Calculate total debt from debt-to-GDP ratio
            total_debt_usd = (debt_to_gdp / 100) * gdp_usd
            
            # Debt service (typically 5-15% of total debt annually)
            debt_service_ratio = np.random.uniform(0.05, 0.15)
            debt_service_usd = total_debt_usd * debt_service_ratio
            
            # Government revenue (typically 15-35% of GDP)
            revenue_pct_gdp = np.random.uniform(15, 35)
            
            # Health spending (typically 2-8% of GDP)
            health_pct_gdp = np.random.uniform(2, 8)
            
            # Education spending (typically 3-7% of GDP)
            education_pct_gdp = np.random.uniform(3, 7)
            
            # Add some missing data (forward-fill will handle this)
            # Randomly set some values to NaN (about 5% of data)
            if np.random.random() < 0.05:
                debt_service_usd = np.nan
            if np.random.random() < 0.05:
                health_pct_gdp = np.nan
            if np.random.random() < 0.05:
                education_pct_gdp = np.nan
            
            data.append({
                'country_code': country_code,
                'country_name': country_name,
                'region': region,
                'year': year,
                'debt_to_gdp': round(debt_to_gdp, 2),
                'total_debt_usd': round(total_debt_usd, 2),
                'debt_service_usd': round(debt_service_usd, 2) if not np.isnan(debt_service_usd) else np.nan,
                'gdp_usd': round(gdp_usd, 2),
                'gdp_growth': round(gdp_growth, 2),
                'revenue_pct_gdp': round(revenue_pct_gdp, 2),
                'health_pct_gdp': round(health_pct_gdp, 2) if not np.isnan(health_pct_gdp) else np.nan,
                'education_pct_gdp': round(education_pct_gdp, 2) if not np.isnan(education_pct_gdp) else np.nan,
            })
    
    df = pd.DataFrame(data)
    return df


def merge_with_creditor_data(df):
    """
    Merge the generated data with creditor composition data.
    
    Args:
        df: DataFrame with country-year data
        
    Returns:
        pd.DataFrame: Merged dataset with creditor information
    """
    # Load creditor data
    creditor_df = pd.read_csv('data/creditor_data.csv')
    
    # Merge on country_code
    merged_df = df.merge(creditor_df, on='country_code', how='left')
    
    return merged_df


def save_to_parquet(df, output_path):
    """
    Save DataFrame to parquet format.
    
    Args:
        df: DataFrame to save
        output_path: Path to save the parquet file
    """
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to parquet
    df.to_parquet(output_path, index=False)
    print(f"✓ Saved {len(df)} rows to {output_path}")
    
    # Save timestamp
    timestamp_path = output_path.parent / 'last_refresh.txt'
    with open(timestamp_path, 'w') as f:
        from datetime import datetime
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(f"✓ Saved refresh timestamp to {timestamp_path}")


def main():
    """Main execution function."""
    print("Generating sample data for Africa Debt Dashboard...")
    print(f"Countries: {len(AFRICAN_COUNTRIES)}")
    print(f"Years: {YEAR_START}-{YEAR_END}")
    print()
    
    # Generate base data
    print("Step 1: Generating country-year data...")
    df = generate_sample_data()
    print(f"✓ Generated {len(df)} country-year records")
    print()
    
    # Merge with creditor data
    print("Step 2: Merging with creditor composition data...")
    df = merge_with_creditor_data(df)
    print(f"✓ Merged creditor data")
    print()
    
    # Display sample
    print("Sample data (first 5 rows):")
    print(df.head())
    print()
    
    # Display summary statistics
    print("Summary statistics:")
    print(f"  Countries: {df['country_code'].nunique()}")
    print(f"  Years: {df['year'].min()} - {df['year'].max()}")
    print(f"  Avg Debt-to-GDP: {df['debt_to_gdp'].mean():.1f}%")
    print(f"  Avg Health Spending: {df['health_pct_gdp'].mean():.1f}% of GDP")
    print(f"  Avg Education Spending: {df['education_pct_gdp'].mean():.1f}% of GDP")
    print()
    
    # Save to parquet
    print("Step 3: Saving to parquet cache...")
    output_path = Path('data/cached/dashboard_data.parquet')
    save_to_parquet(df, output_path)
    print()
    
    print("✓ Sample data generation complete!")
    print(f"  Output: {output_path}")
    print(f"  Size: {len(df)} rows × {len(df.columns)} columns")
    print()
    print("You can now run the dashboard with: streamlit run app.py")


if __name__ == '__main__':
    main()
