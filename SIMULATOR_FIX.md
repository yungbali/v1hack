# Simulator Fix Guide

## Issue
The "Country scenario simulator" section is not loading on the Overview page.

## Fixes Applied

### 1. Added Error Handling in app.py
Wrapped the simulator call in a try-except block to catch and display any errors:

```python
try:
    create_simulator_interface(filtered_df, default_country='NGA')
except Exception as e:
    st.error(f"Error loading simulator: {e}")
    # Shows error details in an expander
```

### 2. Added Data Validation in simulator.py
Added checks to ensure:
- DataFrame is not empty
- All required columns exist
- Clear error messages if data is missing

### 3. Created Diagnostic Tool
Run this to check if everything is set up correctly:

```bash
python diagnose_simulator.py
```

This will check:
- ✓ Data files exist
- ✓ Data can be loaded
- ✓ Required columns present
- ✓ Simulator imports work
- ✓ Calculation functions work
- ✓ Test with sample country data

## How to Fix

### Step 1: Run Diagnostic
```bash
python diagnose_simulator.py
```

This will tell you exactly what's wrong.

### Step 2: Common Issues and Solutions

**Issue**: "No data files found"
**Solution**:
```bash
python scripts/generate_sample_data.py
```

**Issue**: "Missing required columns"
**Solution**: Regenerate data with all columns:
```bash
python scripts/generate_sample_data.py
```

**Issue**: "Error importing simulator"
**Solution**: Check Python dependencies:
```bash
pip install -r requirements.txt
```

### Step 3: Restart Streamlit
After fixing any issues:
```bash
# Stop Streamlit (Ctrl+C)
# Start again
streamlit run app.py
```

## What the Simulator Needs

### Required Data Columns:
- `country_code` - ISO 3-letter country code
- `country_name` - Full country name
- `year` - Year of data
- `debt_to_gdp` - Debt-to-GDP ratio (%)
- `total_debt_usd` - Total external debt (USD)
- `debt_service_usd` - Annual debt service (USD)
- `gdp_usd` - GDP in current USD
- `revenue_pct_gdp` - Government revenue (% of GDP)

### Optional Columns (for better accuracy):
- `avg_interest_rate` - Average interest rate (%)
- `avg_maturity_years` - Average maturity (years)
- `creditor_multilateral_pct` - Multilateral creditor %
- `creditor_bilateral_pct` - Bilateral creditor %
- `creditor_commercial_pct` - Commercial creditor %

## Testing the Simulator

### 1. Check if it appears
- Go to Overview page
- Scroll down to "Country scenario simulator" section
- Should see country selector and sliders

### 2. Test functionality
- Select a country (default: Nigeria)
- Adjust sliders:
  - Interest rate reduction (0-5%)
  - Maturity extension (0-10 years)
  - Principal haircut (0-50%)
- Results should update in real-time

### 3. Verify calculations
- Current state should show:
  - Annual debt service
  - Debt-to-GDP ratio
  - Fiscal space available
- Reform scenario should show:
  - New annual payment
  - Debt-to-GDP (Year 5)
  - Fiscal space freed
  - Opportunity cost breakdown

## Error Messages Explained

### "No data available for simulator"
- The filtered DataFrame is empty
- Check your filters (region, year range, country)
- Try resetting filters to "All"

### "Missing required columns"
- Data file doesn't have all needed columns
- Regenerate data: `python scripts/generate_sample_data.py`

### "Country not found"
- Selected country code not in AFRICAN_COUNTRIES constant
- Check utils/constants.py for valid country codes

### "Error loading simulator"
- General error with detailed traceback
- Check the error details in the expander
- Look at Streamlit terminal for full error

## Debugging Steps

### 1. Check Streamlit Terminal
When you run `streamlit run app.py`, watch the terminal for errors:
```
Error loading simulator: [error message]
```

### 2. Check Browser Console
Open browser developer tools (F12):
- Look for JavaScript errors
- Check Network tab for failed requests

### 3. Test Components Individually
```python
# In Python console or notebook
import pandas as pd
from components.simulator import create_simulator_interface

df = pd.read_parquet('data/cached/dashboard_data.parquet')
# This should work without errors
```

### 4. Verify Calculations
```python
from utils.calculations import calculate_restructuring_impact

result = calculate_restructuring_impact(
    current_debt=1_000_000_000,
    current_rate=0.05,
    current_maturity=10,
    new_rate=0.03,
    maturity_extension=5,
    haircut_pct=20,
    gdp_usd=10_000_000_000
)
print(result)
# Should print a dictionary with results
```

## Quick Checklist

Before reporting the issue as unfixed, verify:

- [ ] Ran `python diagnose_simulator.py` - all checks pass
- [ ] Data file exists in `data/cached/`
- [ ] All required columns present in data
- [ ] Restarted Streamlit server
- [ ] Hard refreshed browser (Cmd+Shift+R / Ctrl+Shift+R)
- [ ] Checked Streamlit terminal for errors
- [ ] Checked browser console for errors
- [ ] Tried with default filters (All Regions, full year range)

## Still Not Working?

If the simulator still doesn't load after all these steps:

1. **Share the error message**:
   - From Streamlit terminal
   - From browser console
   - From the error expander in the app

2. **Share diagnostic output**:
   ```bash
   python diagnose_simulator.py > diagnostic_output.txt
   ```

3. **Check data sample**:
   ```python
   import pandas as pd
   df = pd.read_parquet('data/cached/dashboard_data.parquet')
   print(df.head())
   print(df.columns.tolist())
   ```

The simulator should now work correctly with proper error messages if something is wrong!
