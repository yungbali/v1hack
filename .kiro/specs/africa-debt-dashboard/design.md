# Design Document

## Overview

The Africa Sovereign Debt Crisis Dashboard is a single-page Streamlit application that visualizes sovereign debt data across 54 African countries and enables interactive policy scenario modeling. The system prioritizes rapid development (48-hour timeline), demo reliability (pre-cached data), and storytelling impact (compelling visualizations with human context).

The architecture follows a simple data pipeline → visualization pattern: data is pre-fetched from World Bank and IMF APIs, cached locally as parquet files, and loaded instantly when the Streamlit app starts. All visualizations are built with Plotly for interactivity, and the entire application runs as a single Python script with modular component functions.

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Application                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Overview  │  │   Debt     │  │   Social   │            │
│  │  Section   │  │  Service   │  │   Impact   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│  ┌────────────┐  ┌────────────┐                            │
│  │ Simulator  │  │  Filters   │                            │
│  └────────────┘  └────────────┘                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer (Pandas)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Cached Parquet Files (Pre-fetched)           │  │
│  │  - dashboard_data.parquet (World Bank + IMF)         │  │
│  │  - creditor_data.csv (Static supplement)             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼ (One-time fetch before demo)
┌─────────────────────────────────────────────────────────────┐
│                    External Data Sources                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ World Bank   │  │  IMF API     │  │   Static     │     │
│  │     API      │  │              │  │   CSV Data   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend/Backend**: Streamlit 1.28+ (unified framework)
- **Data Processing**: Pandas 2.0+, NumPy 1.24+
- **Visualization**: Plotly 5.17+ (interactive charts)
- **Data Fetching**: requests library for API calls
- **Deployment**: Streamlit Cloud (free tier)
- **Version Control**: Git/GitHub

### Project Structure

```
debt-dashboard/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── data/
│   ├── fetch_data.py          # API client and data fetching orchestrator
│   ├── process_data.py        # Data cleaning and transformation
│   ├── creditor_data.csv      # Static creditor composition data
│   └── cached/
│       └── dashboard_data.parquet  # Pre-fetched merged dataset
├── components/
│   ├── heatmap.py             # Africa choropleth map component
│   ├── debt_service.py        # Debt service pressure charts
│   ├── social_impact.py       # Social spending comparison
│   └── simulator.py           # Scenario modeling component
├── utils/
│   ├── api_client.py          # World Bank/IMF API wrapper functions
│   ├── calculations.py        # Debt metrics and scenario calculations
│   └── constants.py           # Country codes, colors, unit costs
└── assets/
    └── style.css              # Custom CSS styling
```

## Components and Interfaces

### 1. Data Fetching Module (`data/fetch_data.py`)

**Purpose**: Fetch data from external APIs and cache locally

**Key Functions**:

```python
def fetch_world_bank_data(countries: List[str], 
                         indicators: List[str], 
                         years: range) -> pd.DataFrame:
    """
    Fetch indicators from World Bank API for specified countries and years.
    
    Args:
        countries: List of ISO 3-letter country codes
        indicators: List of World Bank indicator codes
        years: Range of years to fetch
    
    Returns:
        DataFrame with columns: country_code, year, indicator_code, value
    """
    pass

def fetch_imf_data(countries: List[str], 
                  indicators: List[str], 
                  years: range) -> pd.DataFrame:
    """
    Fetch indicators from IMF API for specified countries and years.
    
    Returns:
        DataFrame with columns: country_code, year, indicator_code, value
    """
    pass

def merge_datasets(wb_data: pd.DataFrame, 
                  imf_data: pd.DataFrame, 
                  creditor_data: pd.DataFrame) -> pd.DataFrame:
    """
    Merge World Bank, IMF, and static creditor data into unified dataset.
    
    Returns:
        DataFrame with columns: country_code, country_name, year, 
        debt_to_gdp, total_debt_usd, debt_service_usd, gdp_usd, 
        revenue_pct_gdp, health_pct_gdp, education_pct_gdp,
        creditor_multilateral_pct, creditor_bilateral_pct, 
        creditor_commercial_pct
    """
    pass

def fetch_all_data() -> pd.DataFrame:
    """
    Main orchestrator: fetch all data, merge, and cache to parquet.
    """
    pass
```

**API Endpoints**:
- World Bank: `https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?date={start}:{end}&format=json`
- IMF: `https://www.imf.org/external/datamapper/api/v1/{indicator}/{country}`

### 2. Calculation Utilities (`utils/calculations.py`)

**Purpose**: Perform debt metrics and scenario modeling calculations

**Key Functions**:

```python
def calculate_debt_service_pressure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate debt service as percentage of government revenue.
    
    Formula: (debt_service_usd / (gdp_usd * revenue_pct_gdp / 100)) * 100
    """
    pass

def calculate_opportunity_cost(debt_service_usd: float, 
                              unit_type: str) -> int:
    """
    Convert debt payment to tangible social spending units.
    
    Args:
        debt_service_usd: Annual debt service in USD
        unit_type: One of 'school', 'hospital', 'vaccine_dose', 'teacher'
    
    Returns:
        Number of units that could be funded
    """
    pass

def calculate_restructuring_impact(current_debt: float,
                                  current_rate: float,
                                  current_maturity: int,
                                  new_rate: float,
                                  maturity_extension: int,
                                  haircut_pct: float) -> dict:
    """
    Calculate impact of debt restructuring scenario.
    
    Returns:
        {
            'new_annual_payment': float,
            'fiscal_space_freed': float,
            'new_debt_to_gdp': float,
            'social_spending_increase_pct': float
        }
    """
    pass

def calculate_annuity_payment(principal: float, 
                             rate: float, 
                             periods: int) -> float:
    """
    Calculate annual payment using annuity formula.
    
    Formula: P * (r * (1 + r)^n) / ((1 + r)^n - 1)
    """
    pass
```

### 3. Heatmap Component (`components/heatmap.py`)

**Purpose**: Render Africa choropleth map colored by debt-to-GDP

**Key Function**:

```python
def create_africa_heatmap(df: pd.DataFrame, 
                         metric: str = 'debt_to_gdp',
                         year: int = 2024) -> go.Figure:
    """
    Create interactive choropleth map of Africa.
    
    Args:
        df: DataFrame with country-level data
        metric: Column name to visualize
        year: Year to display
    
    Returns:
        Plotly Figure object
    """
    pass
```

**Implementation Details**:
- Use `plotly.express.choropleth` with `locations` set to ISO 3-letter codes
- Color scale: `RdYlGn_r` (reversed red-yellow-green)
- Range: 0-100% for debt-to-GDP
- Hover template: `{country_name}<br>Debt-to-GDP: {debt_to_gdp:.1f}%<br>Total Debt: ${total_debt_usd:.2f}B`
- Geographic scope: `scope='africa'` to zoom to continent

### 4. Debt Service Component (`components/debt_service.py`)

**Purpose**: Visualize debt service pressure and creditor composition

**Key Functions**:

```python
def create_debt_service_bar_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create sortable bar chart of debt service as % of revenue.
    
    Color coding:
    - Red: >30%
    - Yellow: 20-30%
    - Green: <20%
    """
    pass

def create_creditor_stacked_area(df: pd.DataFrame) -> go.Figure:
    """
    Create stacked area chart showing debt service by creditor type over time.
    
    Stacks: multilateral (blue), bilateral (orange), commercial (red)
    """
    pass
```

### 5. Social Impact Component (`components/social_impact.py`)

**Purpose**: Compare debt service against social spending with opportunity costs

**Key Functions**:

```python
def create_comparison_bar_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create grouped bar chart comparing debt service, health, and education spending.
    
    Three bars per country:
    - Debt service (red)
    - Health spending (blue)
    - Education spending (green)
    """
    pass

def create_opportunity_cost_panel(country: str, 
                                 debt_service_usd: float) -> dict:
    """
    Calculate and format opportunity cost conversions.
    
    Returns:
        {
            'schools': int,
            'hospitals': int,
            'vaccine_doses': int,
            'teachers': int
        }
    """
    pass
```

### 6. Simulator Component (`components/simulator.py`)

**Purpose**: Interactive debt restructuring scenario modeling

**Key Function**:

```python
def create_simulator_interface(country_data: pd.DataFrame) -> None:
    """
    Render simulator UI with sliders and results display.
    
    Components:
    - Current state metrics (left column)
    - Scenario controls (center)
    - Results display (right column)
    """
    pass
```

### 7. Main Application (`app.py`)

**Purpose**: Orchestrate all components into cohesive dashboard

**Structure**:

```python
import streamlit as st
import pandas as pd
from components import heatmap, debt_service, social_impact, simulator
from utils import calculations, constants

# Page config
st.set_page_config(page_title="Africa Debt Crisis Dashboard", 
                   layout="wide")

# Load cached data
@st.cache_data
def load_data():
    return pd.read_parquet('data/cached/dashboard_data.parquet')

df = load_data()

# Sidebar filters
with st.sidebar:
    year_range = st.slider("Year Range", 2014, 2024, (2020, 2024))
    region = st.selectbox("Region", ["All", "West Africa", ...])
    country = st.selectbox("Focus Country", df['country_name'].unique())

# Filter data
filtered_df = apply_filters(df, year_range, region, country)

# Section 1: Overview
st.header("Africa Sovereign Debt Crisis Overview")
col1, col2, col3, col4 = st.columns(4)
# ... KPI tiles ...
st.plotly_chart(heatmap.create_africa_heatmap(filtered_df))

# Section 2: Debt Service Pressure
st.header("Debt Service Pressure")
# ... charts ...

# Section 3: Social Impact
st.header("Social Impact Comparison")
# ... charts and opportunity cost panel ...

# Section 4: Country Simulator
st.header("Country Scenario Simulator")
simulator.create_simulator_interface(filtered_df)
```

## Data Models

### Primary DataFrame Schema

The cached parquet file contains the following columns:

| Column Name | Type | Description | Source |
|------------|------|-------------|--------|
| country_code | str | ISO 3-letter country code | Static |
| country_name | str | Full country name | Static |
| region | str | African sub-region | Static |
| year | int | Year (2014-2024) | API |
| debt_to_gdp | float | Public debt as % of GDP | World Bank |
| total_debt_usd | float | Total external debt stock (USD) | World Bank |
| debt_service_usd | float | Annual debt service payments (USD) | World Bank |
| gdp_usd | float | GDP in current USD | World Bank |
| gdp_growth | float | GDP growth rate (%) | World Bank |
| revenue_pct_gdp | float | Government revenue as % of GDP | World Bank |
| health_pct_gdp | float | Health expenditure as % of GDP | World Bank |
| education_pct_gdp | float | Education expenditure as % of GDP | World Bank |
| creditor_multilateral_pct | float | % of debt owed to multilateral creditors | Static CSV |
| creditor_bilateral_pct | float | % of debt owed to bilateral creditors | Static CSV |
| creditor_commercial_pct | float | % of debt owed to commercial creditors | Static CSV |
| avg_interest_rate | float | Weighted average interest rate (%) | Static CSV |
| avg_maturity_years | int | Weighted average maturity (years) | Static CSV |

### World Bank API Indicators

| Indicator Code | Description | Usage |
|---------------|-------------|-------|
| DT.DOD.DECT.CD | External debt stock | Total debt amounts |
| GC.DOD.TOTL.GD.ZS | Debt-to-GDP ratio | Heatmap, KPIs |
| NY.GDP.MKTP.CD | GDP (current USD) | Calculations base |
| NY.GDP.MKTP.KD.ZG | GDP growth | Simulator scenarios |
| GC.REV.XGRT.GD.ZS | Government revenue | Debt service pressure |
| DT.TDS.DECT.CD | Debt service payments | Main visualizations |
| SH.XPD.CHEX.GD.ZS | Health expenditure | Social impact |
| SE.XPD.TOTL.GD.ZS | Education expenditure | Social impact |

### Constants (`utils/constants.py`)

```python
# African country codes (54 countries)
AFRICAN_COUNTRIES = {
    'DZA': 'Algeria',
    'AGO': 'Angola',
    'BEN': 'Benin',
    # ... all 54 countries
}

# Regional groupings
REGIONS = {
    'West Africa': ['BEN', 'BFA', 'CPV', ...],
    'East Africa': ['BDI', 'COM', 'DJI', ...],
    'Central Africa': ['AGO', 'CMR', 'CAF', ...],
    'Southern Africa': ['BWA', 'LSO', 'MWI', ...],
    'North Africa': ['DZA', 'EGY', 'LBY', ...]
}

# Color palette
COLORS = {
    'debt': '#E74C3C',        # Red
    'health': '#3498DB',      # Blue
    'education': '#2ECC71',   # Green
    'gdp': '#95A5A6',         # Gray
    'multilateral': '#3498DB',
    'bilateral': '#F39C12',
    'commercial': '#E74C3C'
}

# Unit costs for opportunity cost calculations
UNIT_COSTS = {
    'school': 875_000,         # Primary school construction
    'hospital': 11_600_000,    # District hospital
    'vaccine_dose': 50,        # Single vaccine dose
    'teacher': 8_000           # Annual teacher salary
}

# Debt distress thresholds
THRESHOLDS = {
    'debt_to_gdp_high': 60,    # High risk threshold
    'debt_to_gdp_moderate': 40, # Moderate risk threshold
    'debt_service_high': 30,    # High burden (% of revenue)
    'debt_service_moderate': 20 # Moderate burden
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After reviewing the prework analysis, several properties can be consolidated to eliminate redundancy:

- Properties about hover templates (2.3, 3.4) can be combined into a single property about hover data completeness
- Properties about KPI tile rendering (2.1, 3.1, 4.1) can be combined into a general property about KPI calculation correctness
- Properties about chart rendering with correct data (3.2, 3.5, 4.2) share the same underlying concern: data integrity in visualizations
- Color coding properties (2.2, 3.3, 8.1) can be consolidated into a property about consistent color palette application

The consolidated properties below provide unique validation value without redundancy.

### Property 1: API Data Completeness
*For any* successful API fetch operation, the returned DataFrame should contain data for all 54 African countries and all years in the specified range (2014-2024).
**Validates: Requirements 1.1, 1.2**

### Property 2: Data Merge Preserves Information
*For any* valid set of World Bank, IMF, and creditor DataFrames, merging them should produce a unified dataset where every country present in any input DataFrame appears in the output with all expected columns populated.
**Validates: Requirements 1.3**

### Property 3: Parquet Round-Trip Preserves Data
*For any* valid DataFrame, saving to parquet format and then loading should produce a DataFrame with identical values, column names, and data types.
**Validates: Requirements 1.4**

### Property 4: Forward-Fill Respects Gap Limits
*For any* dataset with missing values, the forward-fill function should only fill gaps of 2 years or less, leaving larger gaps as null values.
**Validates: Requirements 1.6**

### Property 5: KPI Calculations Are Correct
*For any* dataset, calculated KPI values (total debt, median debt-to-GDP, countries in distress count, debt service totals) should match manual calculations using the same formulas.
**Validates: Requirements 2.1, 3.1, 4.1**

### Property 6: Heatmap Highlights Top Countries
*For any* dataset, the heatmap highlighting function should identify and mark exactly the three countries with the highest debt-to-GDP ratios.
**Validates: Requirements 2.5**

### Property 7: Insight Generation Produces Valid Output
*For any* dataset with valid debt metrics, the insight generation function should produce a non-empty string containing at least one statistic and country reference.
**Validates: Requirements 2.6**

### Property 8: Color Coding Follows Thresholds
*For any* debt service percentage value, the color assignment function should return red for values >30%, yellow for values 20-30%, and green for values <20%.
**Validates: Requirements 3.3**

### Property 9: Chart Data Integrity
*For any* dataset, all countries present in the input data should appear in rendered charts with their corresponding metric values unchanged from the source data.
**Validates: Requirements 3.2, 3.5, 4.2**

### Property 10: Sort Order Correctness
*For any* dataset, when countries are sorted by debt service in descending order, each country's debt service value should be greater than or equal to the next country's value.
**Validates: Requirements 4.3**

### Property 11: Conditional Highlighting Accuracy
*For any* dataset, countries where debt service exceeds health spending should be flagged for highlighting, and countries where debt service is less than or equal to health spending should not be flagged.
**Validates: Requirements 4.4**

### Property 12: Opportunity Cost Calculations
*For any* debt service amount in USD, the opportunity cost calculation should return the integer division of the debt service by the unit cost, producing consistent results for schools (÷875,000), hospitals (÷11,600,000), vaccines (÷50), and teachers (÷8,000).
**Validates: Requirements 4.5**

### Property 13: Scenario Calculation Consistency
*For any* set of restructuring parameters (maturity extension, interest rate reduction, haircut percentage), the scenario calculation should produce a new annual payment that is less than or equal to the current payment when any relief is applied.
**Validates: Requirements 5.3**

### Property 14: Annuity Formula Correctness
*For any* principal amount, interest rate, and number of periods, the annuity payment calculation should match the standard formula: P × (r × (1 + r)^n) / ((1 + r)^n - 1).
**Validates: Requirements 5.7**

### Property 15: Year Range Filter Correctness
*For any* year range selection [start_year, end_year], the filtered dataset should contain only records where start_year ≤ year ≤ end_year.
**Validates: Requirements 6.2**

### Property 16: Region Filter Correctness
*For any* region selection, the filtered dataset should contain only countries whose country codes are in the predefined list for that region.
**Validates: Requirements 6.3**

### Property 17: Country Filter Isolation
*For any* country selection, the filtered dataset should contain only records matching that country's country code.
**Validates: Requirements 6.4**

### Property 18: Cache Loading Source
*For any* dashboard startup, the data loading function should read from the local parquet cache file and not make any HTTP requests to external APIs.
**Validates: Requirements 7.3**

### Property 19: Graceful Handling of Missing Data
*For any* dataset with null values, visualization functions should render successfully without errors and return valid chart objects.
**Validates: Requirements 7.5**

### Property 20: Color Palette Consistency
*For any* chart rendering function, the colors used for debt metrics, health spending, education spending, and creditor types should match the values defined in the COLORS constant dictionary.
**Validates: Requirements 8.1**

## Error Handling

### Data Fetching Errors

**API Timeout or Connection Failure**:
- Strategy: Implement retry logic with exponential backoff (3 attempts)
- Fallback: Log error and continue with partial data
- User Communication: Display warning banner indicating which countries/indicators failed

**Invalid API Response**:
- Strategy: Validate response structure before parsing
- Fallback: Skip invalid records, log details
- User Communication: Show data quality indicator

**Rate Limiting**:
- Strategy: Implement request throttling (1 request per second)
- Fallback: Cache intermediate results, resume from last successful fetch
- User Communication: Progress indicator during fetch

### Data Processing Errors

**Missing Required Columns**:
- Strategy: Validate DataFrame schema after each transformation
- Fallback: Use default values or skip affected records
- User Communication: Flag low-confidence data in visualizations

**Invalid Numeric Values** (negative debt, >100% ratios):
- Strategy: Implement validation checks, log anomalies
- Fallback: Cap values at reasonable bounds or mark as outliers
- User Communication: Add footnote explaining data quality issues

**Merge Conflicts** (duplicate keys, mismatched indices):
- Strategy: Use outer joins to preserve all data, deduplicate by taking most recent
- Fallback: Log conflicts, prefer World Bank data over IMF when conflicts occur
- User Communication: Show data source attribution

### Visualization Errors

**Empty Dataset**:
- Strategy: Check for empty DataFrames before rendering
- Fallback: Display "No data available" message with filter reset button
- User Communication: Clear message explaining why no data is shown

**Plotly Rendering Failure**:
- Strategy: Wrap chart creation in try-except blocks
- Fallback: Display static error message with data table as alternative
- User Communication: "Chart unavailable - showing data table instead"

**Invalid Country Codes**:
- Strategy: Validate country codes against AFRICAN_COUNTRIES constant
- Fallback: Skip invalid codes, log warning
- User Communication: No user-facing error (silent skip)

### Calculation Errors

**Division by Zero** (in debt service percentage calculations):
- Strategy: Check for zero denominators before division
- Fallback: Return None or np.nan for invalid calculations
- User Communication: Display "N/A" in charts for missing values

**Annuity Formula Edge Cases** (zero interest rate, zero periods):
- Strategy: Handle special cases explicitly
  - If rate = 0: payment = principal / periods
  - If periods = 0: return principal
- Fallback: Return original debt service if calculation fails
- User Communication: Show warning in simulator results

**Negative Fiscal Space** (restructuring increases payments):
- Strategy: Allow negative values, don't constrain
- Fallback: N/A (this is valid scenario outcome)
- User Communication: Display clearly with warning color

### User Input Errors

**Invalid Filter Selections**:
- Strategy: Validate selections against available options
- Fallback: Reset to default ("All" for regions, full range for years)
- User Communication: Toast notification "Invalid selection - reset to default"

**Simulator Parameter Conflicts**:
- Strategy: Validate parameter combinations (e.g., haircut + extension)
- Fallback: Allow all combinations (user experimentation encouraged)
- User Communication: Show warning if scenario seems unrealistic

## Testing Strategy

### Unit Testing

**Framework**: pytest 7.4+

**Coverage Areas**:

1. **Data Fetching Functions** (`data/fetch_data.py`):
   - Test API response parsing with mock responses
   - Test error handling for failed requests
   - Test data merging with sample DataFrames
   - Example: Test that `merge_datasets()` correctly combines three DataFrames with overlapping country codes

2. **Calculation Functions** (`utils/calculations.py`):
   - Test debt service pressure calculation with known inputs/outputs
   - Test opportunity cost conversions with sample values
   - Test annuity formula with standard financial examples
   - Example: Test that `calculate_annuity_payment(100000, 0.05, 10)` returns approximately 12,950

3. **Filter Functions** (`app.py`):
   - Test year range filtering with edge cases (single year, full range)
   - Test region filtering with each region
   - Test country filtering with valid and invalid codes
   - Example: Test that filtering for "West Africa" returns only countries in REGIONS['West Africa']

4. **Component Functions** (`components/*.py`):
   - Test that chart creation functions return valid Plotly Figure objects
   - Test that functions handle empty DataFrames gracefully
   - Test color assignment logic with boundary values
   - Example: Test that `create_africa_heatmap()` returns a Figure with 54 traces (one per country)

**Test Organization**:
```
tests/
├── test_fetch_data.py
├── test_calculations.py
├── test_components.py
└── fixtures/
    ├── sample_wb_response.json
    ├── sample_imf_response.json
    └── sample_merged_data.parquet
```

### Property-Based Testing

**Framework**: Hypothesis 6.92+

**Configuration**: Each property test should run minimum 100 iterations

**Test Tagging**: Each property-based test must include a comment with format:
```python
# Feature: africa-debt-dashboard, Property {number}: {property_text}
```

**Property Test Implementations**:

1. **Property 3: Parquet Round-Trip** (`test_data_persistence.py`):
```python
from hypothesis import given, strategies as st
import pandas as pd

# Feature: africa-debt-dashboard, Property 3: Parquet Round-Trip Preserves Data
@given(st.data())
def test_parquet_roundtrip_preserves_data(data):
    """Test that saving and loading parquet preserves DataFrame integrity"""
    # Generate random DataFrame with debt data structure
    df = generate_random_debt_dataframe(data)
    
    # Save to parquet
    df.to_parquet('test_cache.parquet')
    
    # Load from parquet
    loaded_df = pd.read_parquet('test_cache.parquet')
    
    # Assert equality
    pd.testing.assert_frame_equal(df, loaded_df)
```

2. **Property 4: Forward-Fill Respects Gap Limits** (`test_data_processing.py`):
```python
# Feature: africa-debt-dashboard, Property 4: Forward-Fill Respects Gap Limits
@given(st.data())
def test_forward_fill_respects_gap_limits(data):
    """Test that forward-fill only fills gaps of 2 years or less"""
    # Generate DataFrame with intentional gaps
    df = generate_dataframe_with_gaps(data, max_gap=5)
    
    # Apply forward-fill
    filled_df = forward_fill_with_limit(df, max_gap=2)
    
    # Check that gaps > 2 years remain null
    for country in filled_df['country_code'].unique():
        country_data = filled_df[filled_df['country_code'] == country]
        gaps = find_null_gaps(country_data)
        assert all(gap <= 2 for gap in gaps if gap > 0)
```

3. **Property 8: Color Coding Follows Thresholds** (`test_visualizations.py`):
```python
# Feature: africa-debt-dashboard, Property 8: Color Coding Follows Thresholds
@given(st.floats(min_value=0, max_value=100))
def test_color_coding_follows_thresholds(debt_service_pct):
    """Test that color assignment follows threshold rules"""
    color = assign_debt_service_color(debt_service_pct)
    
    if debt_service_pct > 30:
        assert color == COLORS['debt']  # Red
    elif debt_service_pct >= 20:
        assert color == '#F39C12'  # Yellow
    else:
        assert color == COLORS['education']  # Green
```

4. **Property 10: Sort Order Correctness** (`test_data_processing.py`):
```python
# Feature: africa-debt-dashboard, Property 10: Sort Order Correctness
@given(st.data())
def test_sort_order_correctness(data):
    """Test that sorting by debt service produces descending order"""
    df = generate_random_debt_dataframe(data)
    
    sorted_df = df.sort_values('debt_service_usd', ascending=False)
    
    # Check that each value >= next value
    debt_values = sorted_df['debt_service_usd'].values
    for i in range(len(debt_values) - 1):
        assert debt_values[i] >= debt_values[i + 1]
```

5. **Property 12: Opportunity Cost Calculations** (`test_calculations.py`):
```python
# Feature: africa-debt-dashboard, Property 12: Opportunity Cost Calculations
@given(st.floats(min_value=1_000_000, max_value=10_000_000_000))
def test_opportunity_cost_calculations(debt_service_usd):
    """Test that opportunity cost calculations use correct unit costs"""
    schools = calculate_opportunity_cost(debt_service_usd, 'school')
    hospitals = calculate_opportunity_cost(debt_service_usd, 'hospital')
    vaccines = calculate_opportunity_cost(debt_service_usd, 'vaccine_dose')
    teachers = calculate_opportunity_cost(debt_service_usd, 'teacher')
    
    assert schools == int(debt_service_usd / 875_000)
    assert hospitals == int(debt_service_usd / 11_600_000)
    assert vaccines == int(debt_service_usd / 50)
    assert teachers == int(debt_service_usd / 8_000)
```

6. **Property 14: Annuity Formula Correctness** (`test_calculations.py`):
```python
# Feature: africa-debt-dashboard, Property 14: Annuity Formula Correctness
@given(
    st.floats(min_value=1000, max_value=1_000_000_000),
    st.floats(min_value=0.001, max_value=0.15),
    st.integers(min_value=1, max_value=30)
)
def test_annuity_formula_correctness(principal, rate, periods):
    """Test that annuity calculation matches standard formula"""
    payment = calculate_annuity_payment(principal, rate, periods)
    
    # Calculate expected using formula
    expected = principal * (rate * (1 + rate)**periods) / ((1 + rate)**periods - 1)
    
    # Allow small floating point tolerance
    assert abs(payment - expected) < 0.01
```

7. **Property 15: Year Range Filter Correctness** (`test_filtering.py`):
```python
# Feature: africa-debt-dashboard, Property 15: Year Range Filter Correctness
@given(
    st.data(),
    st.integers(min_value=2014, max_value=2024),
    st.integers(min_value=2014, max_value=2024)
)
def test_year_range_filter_correctness(data, start_year, end_year):
    """Test that year filtering returns only records in range"""
    if start_year > end_year:
        start_year, end_year = end_year, start_year
    
    df = generate_random_debt_dataframe(data)
    filtered = filter_by_year_range(df, start_year, end_year)
    
    # All years should be in range
    assert all(start_year <= year <= end_year for year in filtered['year'])
```

### Integration Testing

**Scope**: Test end-to-end workflows

1. **Data Pipeline Integration**:
   - Test: Run `fetch_all_data()` with mock APIs → verify parquet file created
   - Test: Load cached data → verify all expected columns present
   - Test: Apply filters → verify visualizations update correctly

2. **Simulator Integration**:
   - Test: Select country → adjust sliders → verify calculations update
   - Test: Run scenario → verify all result metrics change appropriately
   - Test: Reset scenario → verify return to original state

3. **Cross-Component Integration**:
   - Test: Click country on heatmap → verify simulator loads that country
   - Test: Apply region filter → verify all sections update consistently
   - Test: Change year range → verify KPIs and charts reflect new range

**Test Execution**:
- Run unit tests on every code change
- Run property tests before committing
- Run integration tests before deployment
- Target: All tests complete in <30 seconds

### Manual Testing Checklist

Before demo:
- [ ] Load dashboard in fresh browser session
- [ ] Verify all 4 sections render without errors
- [ ] Test each filter (year, region, country)
- [ ] Run Zambia scenario in simulator
- [ ] Verify hover interactions work on all charts
- [ ] Test on demo screen resolution
- [ ] Verify load time <3 seconds
- [ ] Check data timestamp is current

## Deployment Architecture

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Fetch and cache data (run once before demo)
python data/fetch_data.py

# Run dashboard locally
streamlit run app.py
```

### Streamlit Cloud Deployment

**Configuration** (`.streamlit/config.toml`):
```toml
[theme]
primaryColor = "#E74C3C"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#ECF0F1"
textColor = "#2C3E50"

[server]
maxUploadSize = 200
enableCORS = false
```

**Deployment Steps**:
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Set Python version to 3.10+
4. Deploy from main branch
5. Verify public URL accessibility

**Pre-Deployment Checklist**:
- [ ] Cached parquet file committed to repo
- [ ] requirements.txt includes all dependencies with versions
- [ ] No hardcoded file paths (use relative paths)
- [ ] No API keys or secrets in code
- [ ] Test deployment on Streamlit Cloud 24 hours before demo

### Performance Optimization

**Data Loading**:
- Use `@st.cache_data` decorator on `load_data()` function
- Load parquet file once at startup, reuse for all interactions
- Expected load time: <1 second for 54 countries × 11 years

**Chart Rendering**:
- Limit heatmap to 54 countries (no aggregation needed)
- Use Plotly's `scattergl` for large datasets (if needed)
- Debounce slider interactions (update on release, not drag)

**Memory Management**:
- Keep cached DataFrame in memory (< 50MB)
- Avoid creating copies of full DataFrame
- Use views and filters instead of copies

## Security Considerations

**Data Privacy**:
- All data is public (World Bank, IMF)
- No user data collected
- No authentication required

**API Security**:
- No API keys stored in code
- Rate limiting implemented to respect API terms
- Graceful handling of API failures

**Deployment Security**:
- Streamlit Cloud provides HTTPS by default
- No server-side data storage
- Stateless application (no session persistence)

## Future Enhancements

**Phase 2** (Post-Hackathon):
- Add creditor network graph visualization
- Implement PDF export for policy briefs
- Add mobile responsive design
- Include debt restructuring timeline
- Add predictive models for debt distress early warning

**Phase 3** (Long-term):
- Expand to Latin America and Asia (200+ countries)
- Build REST API for external developers
- Add user accounts for saving scenarios
- Integrate with additional data sources (OECD, regional development banks)
- Add multi-language support (French, Portuguese, Arabic)

**Scalability Considerations**:
- Current architecture supports up to 200 countries without changes
- For >1000 countries, consider database backend (PostgreSQL)
- For high traffic, consider caching layer (Redis)
- For real-time data, implement incremental updates instead of full refresh
