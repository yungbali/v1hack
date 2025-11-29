"""
Diagnostic script to check simulator dependencies
"""

import sys
from pathlib import Path
import pandas as pd

print("=" * 60)
print("SIMULATOR DIAGNOSTIC TOOL")
print("=" * 60)

# Check 1: Data file exists
print("\n1. Checking data files...")
cache_path = Path("data/cached/dashboard_data.parquet")
test_cache_path = Path("data/cached/test_cache.parquet")

if cache_path.exists():
    print(f"✓ Found: {cache_path}")
    data_file = cache_path
elif test_cache_path.exists():
    print(f"✓ Found: {test_cache_path}")
    data_file = test_cache_path
else:
    print("✗ No data files found!")
    print("  Run: python scripts/generate_sample_data.py")
    sys.exit(1)

# Check 2: Load data
print("\n2. Loading data...")
try:
    df = pd.read_parquet(data_file)
    print(f"✓ Loaded {len(df)} records")
    print(f"  Years: {df['year'].min()} - {df['year'].max()}")
    print(f"  Countries: {df['country_code'].nunique()}")
except Exception as e:
    print(f"✗ Error loading data: {e}")
    sys.exit(1)

# Check 3: Required columns
print("\n3. Checking required columns...")
required_columns = [
    'country_code', 'country_name', 'year', 'debt_to_gdp',
    'total_debt_usd', 'debt_service_usd', 'gdp_usd',
    'revenue_pct_gdp', 'health_pct_gdp', 'education_pct_gdp'
]

missing = []
for col in required_columns:
    if col in df.columns:
        print(f"✓ {col}")
    else:
        print(f"✗ {col} - MISSING")
        missing.append(col)

if missing:
    print(f"\n⚠️  Missing columns: {', '.join(missing)}")
    print("   Simulator may not work correctly")

# Check 4: Test simulator imports
print("\n4. Testing simulator imports...")
try:
    from components.simulator import create_simulator_interface
    print("✓ Simulator component imports successfully")
except Exception as e:
    print(f"✗ Error importing simulator: {e}")
    sys.exit(1)

try:
    from utils.calculations import calculate_restructuring_impact
    print("✓ Restructuring calculation function exists")
except Exception as e:
    print(f"✗ Error importing calculation: {e}")
    sys.exit(1)

# Check 5: Test with Nigeria data
print("\n5. Testing with Nigeria data...")
try:
    nga_data = df[df['country_code'] == 'NGA']
    if nga_data.empty:
        print("⚠️  No data for Nigeria (NGA)")
        print("   Trying first available country...")
        first_country = df['country_code'].iloc[0]
        test_data = df[df['country_code'] == first_country]
        print(f"   Using: {test_data['country_name'].iloc[0]} ({first_country})")
    else:
        test_data = nga_data
        print(f"✓ Found {len(test_data)} records for Nigeria")
    
    # Check latest year data
    latest_year = test_data['year'].max()
    latest = test_data[test_data['year'] == latest_year].iloc[0]
    
    print(f"\n   Latest data ({latest_year}):")
    print(f"   - Debt-to-GDP: {latest['debt_to_gdp']:.1f}%")
    print(f"   - Total Debt: ${latest['total_debt_usd']/1e9:.2f}B")
    print(f"   - Debt Service: ${latest['debt_service_usd']/1e9:.2f}B")
    print(f"   - GDP: ${latest['gdp_usd']/1e9:.1f}B")
    
except Exception as e:
    print(f"✗ Error testing with country data: {e}")
    import traceback
    traceback.print_exc()

# Check 6: Test restructuring calculation
print("\n6. Testing restructuring calculation...")
try:
    from utils.calculations import calculate_restructuring_impact
    
    # Test with sample values
    result = calculate_restructuring_impact(
        current_debt=1_000_000_000,
        current_rate=0.05,
        current_maturity=10,
        new_rate=0.03,
        maturity_extension=5,
        haircut_pct=20,
        gdp_usd=10_000_000_000
    )
    
    print("✓ Restructuring calculation works")
    print(f"   Current payment: ${result['current_annual_payment']/1e9:.2f}B")
    print(f"   New payment: ${result['new_annual_payment']/1e9:.2f}B")
    print(f"   Fiscal space freed: ${result['fiscal_space_freed']/1e9:.2f}B")
    
except Exception as e:
    print(f"✗ Error in restructuring calculation: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("DIAGNOSTIC SUMMARY")
print("=" * 60)

if missing:
    print("⚠️  WARNINGS:")
    print(f"   - Missing columns: {', '.join(missing)}")
    print("   - Simulator may not work correctly")
    print("\n   Solution: Regenerate data with all required columns")
    print("   Run: python scripts/generate_sample_data.py")
else:
    print("✅ All checks passed!")
    print("\n   The simulator should work correctly.")
    print("   If you still see errors, check the Streamlit terminal output.")

print("\nTo run the dashboard:")
print("  streamlit run app.py")
print("=" * 60)
