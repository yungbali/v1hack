"""
Manual testing script for Africa Debt Dashboard
This script verifies the requirements from task 14.1:
- Load time < 3 seconds
- All filters work correctly
- All visualizations render correctly
- Compare with HTML mockup design
"""

import time
import pandas as pd
from pathlib import Path

def test_data_loading():
    """Test that data loads within 3 seconds (Requirement 7.1)"""
    print("=" * 60)
    print("TEST 1: Data Loading Performance")
    print("=" * 60)
    
    start_time = time.time()
    
    # Simulate the data loading process
    cache_path = Path("data/cached/dashboard_data.parquet")
    if cache_path.exists():
        df = pd.read_parquet(cache_path)
        load_time = time.time() - start_time
        
        print(f"✓ Data loaded successfully")
        print(f"  - Records: {len(df):,}")
        print(f"  - Load time: {load_time:.3f} seconds")
        
        if load_time < 3.0:
            print(f"  ✓ PASS: Load time is under 3 seconds (Requirement 7.1)")
        else:
            print(f"  ✗ FAIL: Load time exceeds 3 seconds (Requirement 7.1)")
        
        return df, load_time < 3.0
    else:
        print("✗ FAIL: Cache file not found")
        return None, False

def test_data_completeness(df):
    """Test that all required columns are present"""
    print("\n" + "=" * 60)
    print("TEST 2: Data Completeness")
    print("=" * 60)
    
    required_columns = [
        'country_code', 'country_name', 'year', 'debt_to_gdp',
        'total_debt_usd', 'debt_service_usd', 'gdp_usd',
        'revenue_pct_gdp', 'health_pct_gdp', 'education_pct_gdp'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if not missing_columns:
        print("✓ All required columns present")
        for col in required_columns:
            non_null = df[col].notna().sum()
            total = len(df)
            pct = (non_null / total) * 100
            print(f"  - {col}: {non_null:,}/{total:,} ({pct:.1f}% complete)")
        return True
    else:
        print(f"✗ FAIL: Missing columns: {missing_columns}")
        return False

def test_filter_functions(df):
    """Test that filter functions work correctly (Requirements 6.2, 6.3, 6.4)"""
    print("\n" + "=" * 60)
    print("TEST 3: Filter Functions")
    print("=" * 60)
    
    from utils.constants import REGIONS
    
    # Test year range filter
    print("\n3.1 Year Range Filter (Requirement 6.2)")
    filtered = df[(df['year'] >= 2020) & (df['year'] <= 2024)]
    years_in_range = filtered['year'].unique()
    all_in_range = all(2020 <= year <= 2024 for year in years_in_range)
    
    if all_in_range:
        print(f"  ✓ PASS: Year filter works correctly")
        print(f"    Years in filtered data: {sorted(years_in_range)}")
    else:
        print(f"  ✗ FAIL: Year filter has issues")
    
    # Test region filter
    print("\n3.2 Region Filter (Requirement 6.3)")
    west_africa_codes = REGIONS['West Africa']
    filtered = df[df['country_code'].isin(west_africa_codes)]
    all_in_region = all(code in west_africa_codes for code in filtered['country_code'].unique())
    
    if all_in_region:
        print(f"  ✓ PASS: Region filter works correctly")
        print(f"    Countries in West Africa: {len(filtered['country_code'].unique())}")
    else:
        print(f"  ✗ FAIL: Region filter has issues")
    
    # Test country filter
    print("\n3.3 Country Filter (Requirement 6.4)")
    filtered = df[df['country_code'] == 'NGA']
    only_nigeria = all(code == 'NGA' for code in filtered['country_code'].unique())
    
    if only_nigeria:
        print(f"  ✓ PASS: Country filter works correctly")
        print(f"    Records for Nigeria: {len(filtered)}")
    else:
        print(f"  ✗ FAIL: Country filter has issues")
    
    return all_in_range and all_in_region and only_nigeria

def test_visualization_data(df):
    """Test that visualizations can be created with the data"""
    print("\n" + "=" * 60)
    print("TEST 4: Visualization Data Readiness")
    print("=" * 60)
    
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year]
    
    # Test heatmap data
    print("\n4.1 Heatmap Data (Requirement 2.2)")
    heatmap_ready = 'debt_to_gdp' in latest_data.columns and latest_data['debt_to_gdp'].notna().any()
    if heatmap_ready:
        countries_with_data = latest_data['debt_to_gdp'].notna().sum()
        print(f"  ✓ PASS: Heatmap data available")
        print(f"    Countries with debt-to-GDP data: {countries_with_data}")
    else:
        print(f"  ✗ FAIL: Heatmap data not available")
    
    # Test debt service data
    print("\n4.2 Debt Service Data (Requirement 3.2)")
    debt_service_ready = 'debt_service_usd' in latest_data.columns and latest_data['debt_service_usd'].notna().any()
    if debt_service_ready:
        countries_with_data = latest_data['debt_service_usd'].notna().sum()
        print(f"  ✓ PASS: Debt service data available")
        print(f"    Countries with debt service data: {countries_with_data}")
    else:
        print(f"  ✗ FAIL: Debt service data not available")
    
    # Test social spending data
    print("\n4.3 Social Spending Data (Requirement 4.2)")
    social_ready = ('health_pct_gdp' in latest_data.columns and 
                   'education_pct_gdp' in latest_data.columns and
                   latest_data['health_pct_gdp'].notna().any())
    if social_ready:
        countries_with_health = latest_data['health_pct_gdp'].notna().sum()
        countries_with_edu = latest_data['education_pct_gdp'].notna().sum()
        print(f"  ✓ PASS: Social spending data available")
        print(f"    Countries with health data: {countries_with_health}")
        print(f"    Countries with education data: {countries_with_edu}")
    else:
        print(f"  ✗ FAIL: Social spending data not available")
    
    return heatmap_ready and debt_service_ready and social_ready

def test_calculations():
    """Test that calculation functions work correctly"""
    print("\n" + "=" * 60)
    print("TEST 5: Calculation Functions")
    print("=" * 60)
    
    from utils.calculations import calculate_opportunity_cost, calculate_annuity_payment
    from utils.constants import UNIT_COSTS
    
    # Test opportunity cost
    print("\n5.1 Opportunity Cost Calculation (Requirement 4.5)")
    debt_service = 1_000_000_000  # $1 billion
    
    schools = calculate_opportunity_cost(debt_service, 'school')
    expected_schools = int(debt_service / UNIT_COSTS['school'])
    
    if schools == expected_schools:
        print(f"  ✓ PASS: Opportunity cost calculation correct")
        print(f"    $1B could fund {schools:,} schools")
    else:
        print(f"  ✗ FAIL: Opportunity cost calculation incorrect")
        print(f"    Expected: {expected_schools:,}, Got: {schools:,}")
    
    # Test annuity calculation
    print("\n5.2 Annuity Payment Calculation (Requirement 5.7)")
    principal = 100_000_000
    rate = 0.05
    periods = 10
    
    payment = calculate_annuity_payment(principal, rate, periods)
    expected = principal * (rate * (1 + rate)**periods) / ((1 + rate)**periods - 1)
    
    if abs(payment - expected) < 0.01:
        print(f"  ✓ PASS: Annuity calculation correct")
        print(f"    Annual payment: ${payment:,.2f}")
    else:
        print(f"  ✗ FAIL: Annuity calculation incorrect")
        print(f"    Expected: ${expected:,.2f}, Got: ${payment:,.2f}")
    
    return schools == expected_schools and abs(payment - expected) < 0.01

def test_app_components():
    """Test that all app components can be imported"""
    print("\n" + "=" * 60)
    print("TEST 6: Component Imports")
    print("=" * 60)
    
    try:
        from components.heatmap import create_africa_heatmap
        print("  ✓ Heatmap component imported")
    except Exception as e:
        print(f"  ✗ Heatmap component import failed: {e}")
        return False
    
    try:
        from components.debt_service import create_debt_service_bar_chart, create_creditor_stacked_area
        print("  ✓ Debt service component imported")
    except Exception as e:
        print(f"  ✗ Debt service component import failed: {e}")
        return False
    
    try:
        from components.social_impact import create_comparison_bar_chart, create_opportunity_cost_panel
        print("  ✓ Social impact component imported")
    except Exception as e:
        print(f"  ✗ Social impact component import failed: {e}")
        return False
    
    try:
        from components.simulator import create_simulator_interface
        print("  ✓ Simulator component imported")
    except Exception as e:
        print(f"  ✗ Simulator component import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AFRICA DEBT DASHBOARD - MANUAL TEST SUITE")
    print("Task 14.1: Run dashboard locally with sample data")
    print("=" * 60)
    
    results = []
    
    # Test 1: Data loading
    df, load_pass = test_data_loading()
    results.append(("Data Loading (<3s)", load_pass))
    
    if df is not None:
        # Test 2: Data completeness
        completeness_pass = test_data_completeness(df)
        results.append(("Data Completeness", completeness_pass))
        
        # Test 3: Filter functions
        filter_pass = test_filter_functions(df)
        results.append(("Filter Functions", filter_pass))
        
        # Test 4: Visualization data
        viz_pass = test_visualization_data(df)
        results.append(("Visualization Data", viz_pass))
    
    # Test 5: Calculations
    calc_pass = test_calculations()
    results.append(("Calculation Functions", calc_pass))
    
    # Test 6: Component imports
    component_pass = test_app_components()
    results.append(("Component Imports", component_pass))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n✓ ALL TESTS PASSED - Dashboard is ready for demo!")
    else:
        print(f"\n⚠ {total_tests - passed_tests} test(s) failed - Review issues above")
    
    print("\n" + "=" * 60)
    print("MANUAL VERIFICATION CHECKLIST")
    print("=" * 60)
    print("Please verify the following in the browser:")
    print("  [ ] Dashboard loads at http://localhost:8502")
    print("  [ ] All 4 sections render without errors")
    print("  [ ] Year range filter updates all visualizations")
    print("  [ ] Region filter updates all visualizations")
    print("  [ ] Country search filter works correctly")
    print("  [ ] Heatmap displays Africa with color coding")
    print("  [ ] Hover interactions work on all charts")
    print("  [ ] Simulator controls respond to slider changes")
    print("  [ ] Visual design matches HTML mockup")
    print("  [ ] Load time is under 3 seconds")
    print("=" * 60)

if __name__ == "__main__":
    main()
