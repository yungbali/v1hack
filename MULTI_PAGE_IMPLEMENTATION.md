# Multi-Page Dashboard Implementation

## Overview

The Africa Sovereign Debt Crisis Dashboard has been converted from a single-page application to a multi-page Streamlit app with dedicated pages for different analysis views.

## Pages Implemented

### 1. 🌍 Overview (Main Page - `app.py`)
**Purpose**: System-level overview and entry point to the dashboard

**Features**:
- Four KPI tiles (Debt-to-GDP, Debt Service/Revenue, Health vs Debt, Education vs Debt)
- Africa risk heatmap with debt-to-GDP visualization
- Auto-generated insights
- Debt service pressure section with bar chart and creditor composition
- Social impact comparison with opportunity cost analysis
- Debt restructuring simulator

**Location**: `app.py` (main entry point)

---

### 2. 📊 Debt Service (Page 1)
**Purpose**: Deep dive into debt service pressure analysis

**Features**:
- Key metrics: Average debt service/revenue, total debt service, high burden countries, median debt service
- Debt service by country bar chart (color-coded by risk level)
- Creditor composition over time (stacked area chart)
- Key insights about fiscal constraints and creditor types

**Location**: `pages/1_📊_Debt_Service.py`

---

### 3. 🏦 Creditor Mix (Page 2)
**Purpose**: Analyze creditor composition and debt structure

**Features**:
- Creditor composition overview (Multilateral, Bilateral, Commercial percentages)
- Stacked bar chart showing creditor mix by country
- Detailed creditor type characteristics (terms, flexibility, restructuring implications)
- Educational content about different creditor types

**Location**: `pages/2_🏦_Creditor_Mix.py`

---

### 4. ❤️ Social Spending (Page 3)
**Purpose**: Compare debt service against social spending

**Features**:
- Spending priorities KPIs (health, education, combined social spending)
- Alert for countries where debt service exceeds health spending
- Grouped bar chart comparing debt service, health, and education spending
- Enhanced opportunity cost analysis with larger cards and better visuals
- Key insights about the human cost of debt

**Location**: `pages/3_❤️_Social_Spending.py`

---

### 5. 🔍 Country Deep Dive (Page 4)
**Purpose**: Detailed country-level analysis and scenario modeling

**Features**:
- Country selector in sidebar with quick stats
- Current debt profile KPIs (Debt-to-GDP, Total Debt, Debt Service, GDP)
- Historical trends charts (Debt-to-GDP over time, Debt service over time)
- Full debt restructuring simulator
- Country-specific insights and analysis notes

**Location**: `pages/4_🔍_Country_Deep_Dive.py`

---

## How Streamlit Multi-Page Apps Work

Streamlit automatically discovers pages in the `pages/` directory and creates navigation:

1. **File naming convention**: `[number]_[emoji]_[Name].py`
   - Number determines order in sidebar
   - Emoji appears in navigation
   - Name becomes the page title

2. **Automatic navigation**: Streamlit adds a page selector in the sidebar automatically

3. **Shared state**: Session state is shared across pages

4. **Independent execution**: Each page runs independently when selected

## Running the Dashboard

```bash
# Start the dashboard
streamlit run app.py

# The app will be available at http://localhost:8501
# Use the sidebar to navigate between pages
```

## Key Features

### Consistent Design
- All pages use the same custom CSS from `assets/style.css`
- Consistent color palette from `utils/constants.py`
- Matching typography and spacing

### Shared Components
- All pages use the same data loading function
- Shared filter functions (year range, region, country)
- Reusable visualization components from `components/`

### Responsive Filters
- Each page has appropriate filters in the sidebar
- Filters update visualizations in real-time
- Data quality warnings when applicable

## Data Requirements

All pages load data from:
- `data/cached/dashboard_data.parquet` (primary)
- `data/cached/test_cache.parquet` (fallback)

Ensure data is generated using:
```bash
python scripts/generate_sample_data.py
```

## Next Steps

To further enhance the multi-page dashboard:

1. **Add page-specific filters**: Each page could have unique filter options
2. **Cross-page navigation**: Add "View in Country Deep Dive" buttons
3. **Bookmarkable URLs**: Streamlit supports query parameters for deep linking
4. **Export functionality**: Add data export buttons on each page
5. **Comparison mode**: Allow comparing multiple countries side-by-side

## Technical Notes

- Each page is a standalone Python script
- Pages share the same virtual environment and dependencies
- Custom CSS is loaded on each page for consistency
- All pages handle missing data gracefully
- Error handling with try-except blocks around visualizations

## File Structure

```
.
├── app.py                          # Main overview page
├── pages/
│   ├── 1_📊_Debt_Service.py       # Debt service analysis
│   ├── 2_🏦_Creditor_Mix.py       # Creditor composition
│   ├── 3_❤️_Social_Spending.py    # Social impact comparison
│   └── 4_🔍_Country_Deep_Dive.py  # Country-level analysis
├── components/
│   ├── debt_service.py
│   ├── heatmap.py
│   ├── simulator.py
│   └── social_impact.py
├── utils/
│   ├── calculations.py
│   ├── constants.py
│   └── api_client.py
└── data/
    └── cached/
        └── dashboard_data.parquet
```

## Success Criteria

✅ Four new pages created with distinct purposes
✅ Consistent design and styling across all pages
✅ Shared data loading and filtering logic
✅ All existing components integrated into appropriate pages
✅ Graceful error handling and missing data scenarios
✅ Responsive layouts with proper column grids
✅ Educational content and insights on each page

The multi-page dashboard is now ready for use!
