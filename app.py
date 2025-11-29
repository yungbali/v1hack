"""
Africa Sovereign Debt Crisis Dashboard
Main Streamlit application entry point
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, List

# Import utilities
from utils.constants import COLORS, THRESHOLDS, REGIONS, AFRICAN_COUNTRIES
from utils.calculations import calculate_kpi_metrics, generate_insight
from components.heatmap import create_africa_heatmap
from components.pan_african import (
    render_objective_banner,
    render_opportunity_cost_summary,
    render_pan_african_metadata_cards,
    render_recommendations_panel,
)
from components.social_impact import (
    create_comparison_bar_chart,
    create_opportunity_cost_panel,
    identify_countries_debt_exceeds_health,
)

# Page configuration
st.set_page_config(
    page_title="Africa Sovereign Debt Crisis Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and inject custom CSS
def load_css():
    """Load custom CSS from assets/style.css"""
    css_file = Path("assets/style.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Additional inline CSS for Streamlit-specific overrides
    st.markdown("""
        <style>
        /* Remove Streamlit branding but keep navigation */
        footer {visibility: hidden;}
        
        /* Main app background */
        .stApp {
            background-color: #F9FAFB;
        }
        
        /* Sidebar styling - keep page navigation visible */
        [data-testid="stSidebar"] {
            background-color: white;
            border-right: 1px solid #E2E8F0;
        }
        
        /* Style the page navigation */
        [data-testid="stSidebarNav"] {
            padding-top: 1rem;
        }
        
        /* Remove padding from main container */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

# Load CSS
load_css()

# Load cached data
@st.cache_data
def load_data():
    """
    Load dashboard data from parquet cache.
    
    This function loads pre-fetched data from the local parquet cache file,
    ensuring no API calls are made during dashboard startup.
    
    Returns:
        pd.DataFrame: Cached dashboard data with all required columns
    
    Validates: Requirements 1.5, 7.3
    """
    import time
    start_time = time.time()
    
    # Try primary cache location first
    cache_path = Path("data/cached/dashboard_data.parquet")
    
    # Fallback to test cache if primary doesn't exist
    if not cache_path.exists():
        cache_path = Path("data/cached/test_cache.parquet")
    
    if cache_path.exists():
        df = pd.read_parquet(cache_path)
        load_time = time.time() - start_time
        
        # Verify load time is under 3 seconds (Requirement 7.1)
        if load_time > 3.0:
            st.warning(f"⚠️ Data load took {load_time:.2f}s (target: <3s)")
        
        return df
    else:
        # Return empty DataFrame with expected schema if no cache exists
        return pd.DataFrame(columns=[
            'country_code', 'country_name', 'year', 'debt_to_gdp',
            'total_debt_usd', 'debt_service_usd', 'gdp_usd',
            'revenue_pct_gdp', 'health_pct_gdp', 'education_pct_gdp'
        ])

def filter_by_year_range(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Filter DataFrame to include only records within the specified year range.
    
    Args:
        df: Input DataFrame with 'year' column
        start_year: Start year (inclusive)
        end_year: End year (inclusive)
    
    Returns:
        pd.DataFrame: Filtered DataFrame containing only records where start_year <= year <= end_year
    
    Validates: Requirements 6.2
    """
    if df.empty or 'year' not in df.columns:
        return df
    
    return df[(df['year'] >= start_year) & (df['year'] <= end_year)]


def filter_by_region(df: pd.DataFrame, region: str) -> pd.DataFrame:
    """
    Filter DataFrame to include only countries within the specified region.
    
    Args:
        df: Input DataFrame with 'country_code' column
        region: Region name (must be a key in REGIONS constant)
    
    Returns:
        pd.DataFrame: Filtered DataFrame containing only countries in the specified region
    
    Validates: Requirements 6.3
    """
    if df.empty or 'country_code' not in df.columns:
        return df
    
    if region not in REGIONS:
        return df
    
    region_countries = REGIONS[region]
    return df[df['country_code'].isin(region_countries)]


def filter_by_country(df: pd.DataFrame, country_code: str) -> pd.DataFrame:
    """
    Filter DataFrame to include only records for the specified country.
    
    Args:
        df: Input DataFrame with 'country_code' column
        country_code: ISO 3-letter country code
    
    Returns:
        pd.DataFrame: Filtered DataFrame containing only records for the specified country
    
    Validates: Requirements 6.4
    """
    if df.empty or 'country_code' not in df.columns:
        return df
    
    return df[df['country_code'] == country_code]


def check_data_quality(df: pd.DataFrame) -> Dict[str, any]:
    """
    Check data quality and identify low-confidence data points.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary with quality metrics and warnings
    
    Validates: Requirements 7.5
    """
    quality_report = {
        'has_data': not df.empty,
        'total_records': len(df),
        'missing_debt_to_gdp': 0,
        'missing_debt_service': 0,
        'missing_social_spending': 0,
        'warnings': []
    }
    
    if df.empty:
        quality_report['warnings'].append("No data available")
        return quality_report
    
    # Check for missing critical fields
    if 'debt_to_gdp' in df.columns:
        missing_debt = df['debt_to_gdp'].isna().sum()
        quality_report['missing_debt_to_gdp'] = missing_debt
        if missing_debt > len(df) * 0.3:
            quality_report['warnings'].append(f"High missing data: {missing_debt} records missing debt-to-GDP")
    
    if 'debt_service_usd' in df.columns:
        missing_service = df['debt_service_usd'].isna().sum()
        quality_report['missing_debt_service'] = missing_service
        if missing_service > len(df) * 0.3:
            quality_report['warnings'].append(f"High missing data: {missing_service} records missing debt service")
    
    if 'health_pct_gdp' in df.columns and 'education_pct_gdp' in df.columns:
        missing_social = (df['health_pct_gdp'].isna() | df['education_pct_gdp'].isna()).sum()
        quality_report['missing_social_spending'] = missing_social
        if missing_social > len(df) * 0.3:
            quality_report['warnings'].append(f"High missing data: {missing_social} records missing social spending")
    
    return quality_report


# Load data with loading indicator
with st.spinner('Loading dashboard data...'):
    try:
        df = load_data()
        data_available = not df.empty
        
        # Show success message briefly
        if data_available:
            st.success(f'✓ Data loaded successfully ({len(df)} records)', icon="✅")
            import time
            time.sleep(0.5)  # Brief pause to show success message
            st.empty()  # Clear the success message
    except Exception as e:
        st.error(f"Error loading data: {e}")
        df = pd.DataFrame()
        data_available = False

# Sidebar
with st.sidebar:
    # Logo and title
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #F1F5F9;">
            <div style="height: 2rem; width: 2rem; border-radius: 0.375rem; background: #0F172A; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 0.75rem; font-weight: 600; color: white;">AD</span>
            </div>
            <div style="display: flex; flex-direction: column;">
                <span style="font-size: 0.875rem; font-weight: 600; color: #0F172A;">Africa Debt</span>
                <span style="font-size: 0.75rem; color: #64748B;">Crisis Dashboard</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("""
        <div style="padding: 1rem 0;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.75rem; padding: 0 0.5rem;">
                Main views
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation info
    st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0.75rem; border-radius: 0.375rem; background: #0F172A; color: white;">
                <span>🌍</span>
                <span style="font-size: 0.875rem; font-weight: 500;">Overview</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="padding: 0.75rem 0.5rem; border-top: 1px solid #F1F5F9;">
            <p style="font-size: 0.75rem; color: #64748B; margin: 0;">
                Navigate to other views using the sidebar or the pages menu above.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Risk bands legend
    st.markdown("""
        <div style="padding: 1.5rem 0.5rem 1rem 0.5rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.75rem;">
                Risk bands
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Risk indicators
    risk_bands = [
        (COLORS['debt'], "High risk", f"> {THRESHOLDS['debt_to_gdp_high']}% GDP"),
        (COLORS['bilateral'], "Moderate", f"{THRESHOLDS['debt_to_gdp_moderate']}–{THRESHOLDS['debt_to_gdp_high']}% GDP"),
        (COLORS['education'], "Low risk", f"< {THRESHOLDS['debt_to_gdp_moderate']}% GDP")
    ]
    
    for color, label, threshold in risk_bands:
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; padding: 0 0.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="height: 0.625rem; width: 0.625rem; border-radius: 9999px; background: {color};"></span>
                    <span style="font-size: 0.75rem; color: #475569;">{label}</span>
                </div>
                <span style="font-size: 0.7rem; color: #64748B;">{threshold}</span>
            </div>
        """, unsafe_allow_html=True)
    
    # Quick guide
    st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; background: #F8FAFC; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
            <div style="display: flex; align-items: start; gap: 0.75rem;">
                <div style="margin-top: 0.125rem; height: 1.75rem; width: 1.75rem; border-radius: 9999px; background: rgba(15, 23, 42, 0.05); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 0.875rem;">ℹ️</span>
                </div>
                <div style="flex: 1;">
                    <p style="font-size: 0.75rem; font-weight: 500; color: #0F172A; margin-bottom: 0.25rem;">
                        Quick guide
                    </p>
                    <p style="font-size: 0.75rem; color: #475569; line-height: 1.4;">
                        Hover the map for fast stats. Click a country to sync all charts and the simulator.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Data refresh timestamp
    if data_available:
        # Check for last refresh timestamp
        timestamp_file = Path("data/cached/last_refresh.txt")
        if timestamp_file.exists():
            with open(timestamp_file, 'r') as f:
                last_refresh = f.read().strip()
            st.markdown(f"""
                <div style="margin-top: 1rem; padding: 0.75rem; background: white; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        Data refresh
                    </p>
                    <p style="font-size: 0.75rem; color: #475569;">
                        {last_refresh}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="margin-top: 1rem; padding: 0.75rem; background: white; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                        Data refresh
                    </p>
                    <p style="font-size: 0.75rem; color: #475569;">
                        Using cached data
                    </p>
                </div>
            """, unsafe_allow_html=True)

# Main content area
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Top bar with global filters
st.markdown("""
    <div style="position: sticky; top: 0; z-index: 20; background: rgba(249, 250, 251, 0.95); backdrop-filter: blur(8px); border-bottom: 1px solid #E2E8F0; padding: 0.75rem 0; margin: -2rem -1rem 1.5rem -1rem;">
        <div style="padding: 0 1rem;">
        </div>
    </div>
""", unsafe_allow_html=True)

# Global filters in columns
col1, col2, col3, col4 = st.columns([2, 2, 2, 3])

with col1:
    # Region selector
    region_options = ["All Regions"] + list(REGIONS.keys())
    selected_region = st.selectbox(
        "Region",
        region_options,
        key="region_filter",
        label_visibility="collapsed"
    )
    st.markdown("""
        <style>
        div[data-testid="stSelectbox"] label {
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: #64748B;
        }
        </style>
    """, unsafe_allow_html=True)

with col2:
    # Year range selector
    year_range = st.slider(
        "Year Range",
        min_value=2014,
        max_value=2024,
        value=(2020, 2024),
        key="year_range_filter",
        label_visibility="collapsed"
    )

with col3:
    # Currency selector (static for now)
    st.markdown("""
        <div style="display: inline-flex; align-items: center; gap: 0.5rem; border-radius: 0.375rem; border: 1px solid #E2E8F0; background: white; padding: 0.375rem 0.75rem; height: 38px;">
            <span style="font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.14em; color: #64748B;">Currency</span>
            <span style="font-size: 0.875rem; font-weight: 500; color: #1E293B;">USD (constant)</span>
        </div>
    """, unsafe_allow_html=True)

with col4:
    # Country search box
    country_options = ["All Countries"] + sorted(AFRICAN_COUNTRIES.values())
    selected_country = st.selectbox(
        "Search country",
        country_options,
        key="country_filter",
        label_visibility="collapsed"
    )

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

# Hero section with title and metadata cards
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <!-- Breadcrumb tags -->
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
            <span style="display: inline-flex; align-items: center; border-radius: 9999px; border: 1px solid #E2E8F0; background: white; padding: 0.125rem 0.625rem; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B;">
                Policy Analytics
            </span>
            <span style="display: inline-flex; align-items: center; border-radius: 9999px; border: 1px solid #E2E8F0; background: white; padding: 0.125rem 0.625rem; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B;">
                Africa Sovereign Debt
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Title and description in left column, metadata cards in right column
hero_col1, hero_col2 = st.columns([7, 5])

with hero_col1:
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-size: 2.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.75rem; line-height: 1.2;">
                Africa Sovereign Debt Crisis Dashboard
            </h1>
            <p style="font-size: 1.125rem; color: #475569; line-height: 1.6;">
                A data-first interface to help policymakers, researchers, and advocates understand debt risks, creditor exposure, and the social trade‑offs of austerity across African economies.
            </p>
        </div>
    """, unsafe_allow_html=True)

with hero_col2:
    render_pan_african_metadata_cards()

render_objective_banner()

# Add spacing after hero section
st.markdown("<br>", unsafe_allow_html=True)

# Check if data is available
if not data_available:
    st.warning("⚠️ No data available. Please run the data fetching script first.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Apply filters to data
filtered_df = df.copy()

# Apply year range filter
if 'year_range_filter' in st.session_state:
    year_start, year_end = st.session_state.year_range_filter
    filtered_df = filter_by_year_range(filtered_df, year_start, year_end)

# Apply region filter
if 'region_filter' in st.session_state and st.session_state.region_filter != "All Regions":
    filtered_df = filter_by_region(filtered_df, st.session_state.region_filter)

# Apply country filter
if 'country_filter' in st.session_state and st.session_state.country_filter != "All Countries":
    # Find country code from name
    country_code = None
    for code, name in AFRICAN_COUNTRIES.items():
        if name == st.session_state.country_filter:
            country_code = code
            break
    if country_code:
        filtered_df = filter_by_country(filtered_df, country_code)

# Check data quality and display warnings
quality_report = check_data_quality(filtered_df)
if quality_report['warnings']:
    st.markdown("""
        <div style="margin-bottom: 1rem; padding: 1rem; background: #FEF3C7; border-radius: 0.5rem; border: 1px solid #FDE68A;">
            <div style="display: flex; align-items: start; gap: 0.75rem;">
                <div style="margin-top: 0.125rem; height: 1.75rem; width: 1.75rem; border-radius: 9999px; background: rgba(245, 158, 11, 0.1); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 0.875rem;">⚠️</span>
                </div>
                <div style="flex: 1;">
                    <p style="font-size: 0.75rem; font-weight: 500; color: #92400E; margin-bottom: 0.25rem;">
                        Data quality notice
                    </p>
                    <p style="font-size: 0.875rem; color: #78350F; line-height: 1.5;">
    """, unsafe_allow_html=True)
    for warning in quality_report['warnings']:
        st.markdown(f"• {warning}<br>", unsafe_allow_html=True)
    st.markdown("""
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# OVERVIEW SECTION
# ============================================================================

st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
            System-level indicators
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Aggregates update with region and year filters.
        </p>
    </div>
""", unsafe_allow_html=True)

# Prepare containers for downstream sections
debt_exceeds_health_list: List[str] = []

# Calculate KPI metrics
if not filtered_df.empty:
    latest_year = filtered_df['year'].max()
    latest_data = filtered_df[filtered_df['year'] == latest_year].copy()
    kpis = calculate_kpi_metrics(filtered_df)
    debt_exceeds_health_list = identify_countries_debt_exceeds_health(
        filtered_df, year=latest_year
    )
    high_risk_threshold = THRESHOLDS['debt_to_gdp_high']
    high_risk_count = int((latest_data['debt_to_gdp'] > high_risk_threshold).sum())
    baseline_debt_service = latest_data['debt_service_usd'].median()
    baseline_panel = (
        create_opportunity_cost_panel("Median Country", baseline_debt_service)
        if pd.notna(baseline_debt_service) and baseline_debt_service > 0
        else None
    )
    
    # Create 4-column grid for KPI tiles
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    # KPI 1: Median Debt-to-GDP
    with kpi_col1:
        debt_to_gdp = kpis['median_debt_to_gdp']
        debt_trend = kpis['debt_to_gdp_trend']
        
        # Determine risk level
        if debt_to_gdp > THRESHOLDS['debt_to_gdp_high']:
            risk_color = COLORS['debt']
            risk_label = "High risk"
        elif debt_to_gdp > THRESHOLDS['debt_to_gdp_moderate']:
            risk_color = COLORS['bilateral']
            risk_label = "Moderate"
        else:
            risk_color = COLORS['education']
            risk_label = "Low risk"
        
        # Trend arrow
        if debt_trend > 0:
            trend_arrow = "↗"
            trend_color = COLORS['debt']
            trend_sign = "+"
        elif debt_trend < 0:
            trend_arrow = "↘"
            trend_color = COLORS['education']
            trend_sign = ""
        else:
            trend_arrow = "→"
            trend_color = COLORS['gdp']
            trend_sign = ""
        
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); transition: all 0.2s;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                    Debt-to-GDP (median)
                </p>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <p style="font-size: 2rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                        {debt_to_gdp:.1f}%
                    </p>
                    <span style="display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; font-weight: 500; color: {risk_color};">
                        <span style="height: 0.375rem; width: 0.375rem; border-radius: 9999px; background: {risk_color};"></span>
                        {risk_label}
                    </span>
                </div>
                <div style="display: flex; align-items: center; justify-between; font-size: 0.75rem; color: #64748B;">
                    <div style="display: inline-flex; align-items: center; gap: 0.25rem;">
                        <span style="font-size: 1rem; color: {trend_color};">{trend_arrow}</span>
                        <span style="font-weight: 500; color: {trend_color};">{trend_sign}{debt_trend:.1f} pp</span>
                    </div>
                    <span>vs previous year</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # KPI 2: Debt Service / Revenue
    with kpi_col2:
        debt_service_pct = kpis['debt_service_pct_revenue']
        service_trend = kpis['debt_service_trend']
        
        # Determine risk level
        if debt_service_pct > THRESHOLDS['debt_service_high']:
            risk_color = COLORS['debt']
            risk_label = "High burden"
        elif debt_service_pct > THRESHOLDS['debt_service_moderate']:
            risk_color = COLORS['bilateral']
            risk_label = "Upper band"
        else:
            risk_color = COLORS['education']
            risk_label = "Manageable"
        
        # Trend arrow
        if service_trend > 0:
            trend_arrow = "↗"
            trend_color = COLORS['debt']
            trend_sign = "+"
        elif service_trend < 0:
            trend_arrow = "↘"
            trend_color = COLORS['education']
            trend_sign = ""
        else:
            trend_arrow = "→"
            trend_color = COLORS['gdp']
            trend_sign = ""
        
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); transition: all 0.2s;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                    Debt service / revenue
                </p>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <p style="font-size: 2rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                        {debt_service_pct:.1f}%
                    </p>
                    <span style="display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; font-weight: 500; color: {risk_color};">
                        <span style="height: 0.375rem; width: 0.375rem; border-radius: 9999px; background: {risk_color};"></span>
                        {risk_label}
                    </span>
                </div>
                <div style="display: flex; align-items: center; justify-between; font-size: 0.75rem; color: #64748B;">
                    <div style="display: inline-flex; align-items: center; gap: 0.25rem;">
                        <span style="font-size: 1rem; color: {trend_color};">{trend_arrow}</span>
                        <span style="font-weight: 500; color: {trend_color};">{trend_sign}{service_trend:.1f} pts</span>
                    </div>
                    <span>5-year trend</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # KPI 3: Health vs Debt Service
    with kpi_col3:
        health_ratio = kpis['health_vs_debt']
        
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); transition: all 0.2s;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                    Health vs debt service
                </p>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <p style="font-size: 2rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                        {health_ratio:.1f}×
                    </p>
                    <span style="display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; font-weight: 500; color: {COLORS['health']};">
                        <span style="height: 0.375rem; width: 0.375rem; border-radius: 9999px; background: {COLORS['health']};"></span>
                        Health
                    </span>
                </div>
                <div style="display: flex; align-items: center; justify-between; font-size: 0.75rem; color: #64748B;">
                    <span>Median health spend / debt service</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # KPI 4: Education vs Debt Service
    with kpi_col4:
        education_ratio = kpis['education_vs_debt']
        
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); transition: all 0.2s;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                    Education vs debt service
                </p>
                <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <p style="font-size: 2rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                        {education_ratio:.1f}×
                    </p>
                    <span style="display: inline-flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; font-weight: 500; color: {COLORS['education']};">
                        <span style="height: 0.375rem; width: 0.375rem; border-radius: 9999px; background: {COLORS['education']};"></span>
                        Education
                    </span>
                </div>
                <div style="display: flex; align-items: center; justify-between; font-size: 0.75rem; color: #64748B;">
                    <span>Median education spend / debt service</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    if baseline_panel:
        render_opportunity_cost_summary(
            baseline_panel,
            title="Baseline opportunity cost snapshot",
            subtitle=f"Median country debt service in {latest_year} could fund:",
        )

    debt_exceeds_health_count = len(debt_exceeds_health_list)
    if high_risk_count > 0:
        risk_recommendation = (
            f"{high_risk_count} countries exceed the {high_risk_threshold}% debt-to-GDP threshold. "
            "Use the heatmap and KPI tiles to prioritize them for deeper modelling."
        )
    else:
        risk_recommendation = (
            f"No countries currently exceed the {high_risk_threshold}% debt-to-GDP threshold. "
            "Keep the heatmap synced with filters to catch emerging pressure."
        )

    if debt_exceeds_health_count > 0:
        social_recommendation = (
            f"{debt_exceeds_health_count} countries spend more on debt service than health. "
            "Bring those cases into the social impact comparison and annotate the opportunity-cost tiles."
        )
    else:
        social_recommendation = (
            "Monitor when debt service outpaces health spending using the social impact comparison and "
            "opportunity-cost tiles."
        )

    baseline_restructure = ""
    if baseline_panel and pd.notna(baseline_debt_service):
        baseline_restructure = (
            f"The median country is servicing roughly ${baseline_debt_service / 1e9:.1f}B annually—"
            "prototype restructuring mixes in the simulator and translate saved dollars into schools or hospitals."
        )
    else:
        baseline_restructure = (
            "Use the simulator to prototype restructuring mixes and quantify savings in social-service units."
        )

    recommendations = [
        {
            "title": "Prioritize high-risk economies",
            "description": risk_recommendation,
        },
        {
            "title": "Investigate social service trade-offs",
            "description": social_recommendation,
        },
        {
            "title": "Map creditor leverage",
            "description": (
                "Interrogate the creditor composition area chart to see where commercial versus multilateral "
                "exposure is climbing, and capture negotiation angles for your policy brief."
            ),
        },
        {
            "title": "Prototype restructuring scenarios",
            "description": baseline_restructure,
        },
    ]

    render_recommendations_panel(
        recommendations,
        intro=f"Anchor your hackathon storyline on these next steps using the {latest_year} snapshot.",
    )
else:
    st.info("No data available for selected filters")

# Add spacing
st.markdown("<br>", unsafe_allow_html=True)

# Africa Heatmap Section
st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
            Africa risk heatmap
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Debt-to-GDP ratios across the continent. Hover for details, click to focus.
        </p>
    </div>
""", unsafe_allow_html=True)

# Create and display heatmap
if not filtered_df.empty:
    # Get the most recent year for the heatmap
    latest_year = filtered_df['year'].max()
    
    # Create heatmap with loading indicator
    with st.spinner('Generating Africa heatmap...'):
        heatmap_fig = create_africa_heatmap(
            filtered_df,
            metric='debt_to_gdp',
            year=latest_year,
            highlight_top_n=3
        )
    
    # Display the heatmap
    st.plotly_chart(heatmap_fig, use_container_width=True, key="africa_heatmap")
    
    # Generate and display insight
    insight_text = generate_insight(filtered_df)
    st.markdown(f"""
        <div style="margin-top: 1rem; padding: 1rem; background: #F8FAFC; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
            <div style="display: flex; align-items: start; gap: 0.75rem;">
                <div style="margin-top: 0.125rem; height: 1.75rem; width: 1.75rem; border-radius: 9999px; background: rgba(15, 23, 42, 0.05); display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 0.875rem;">💡</span>
                </div>
                <div style="flex: 1;">
                    <p style="font-size: 0.75rem; font-weight: 500; color: #0F172A; margin-bottom: 0.25rem;">
                        Key insight
                    </p>
                    <p style="font-size: 0.875rem; color: #475569; line-height: 1.5;">
                        {insight_text}
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("No data available for heatmap")

# Add spacing
st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# DEBT SERVICE PRESSURE SECTION
# ============================================================================

from components.debt_service import create_debt_service_bar_chart, create_creditor_stacked_area

st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
            Debt service pressure
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Annual debt payments relative to government revenue and creditor composition.
        </p>
    </div>
""", unsafe_allow_html=True)

if not filtered_df.empty:
    # Create 2-column layout for charts
    debt_col1, debt_col2 = st.columns([1, 1])
    
    with debt_col1:
        # Debt service bar chart
        try:
            with st.spinner('Creating debt service chart...'):
                latest_year = filtered_df['year'].max()
                bar_chart = create_debt_service_bar_chart(filtered_df, year=latest_year, top_n=20)
            st.plotly_chart(bar_chart, use_container_width=True, key="debt_service_bar")
        except Exception as e:
            st.error(f"Error creating debt service chart: {e}")
    
    with debt_col2:
        # Creditor stacked area chart
        try:
            with st.spinner('Creating creditor composition chart...'):
                area_chart = create_creditor_stacked_area(filtered_df)
            st.plotly_chart(area_chart, use_container_width=True, key="creditor_area")
        except Exception as e:
            st.error(f"Error creating creditor composition chart: {e}")
else:
    st.info("No data available for debt service analysis")

# Add spacing
st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SOCIAL IMPACT SECTION
# ============================================================================

st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
            Social impact comparison
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Debt service payments compared to health and education spending, with opportunity cost analysis.
        </p>
    </div>
""", unsafe_allow_html=True)

if not filtered_df.empty:
    # Comparison bar chart
    try:
        with st.spinner('Creating social impact comparison...'):
            latest_year = filtered_df['year'].max()
            comparison_chart = create_comparison_bar_chart(filtered_df, year=latest_year)
        st.plotly_chart(comparison_chart, use_container_width=True, key="social_comparison")
        
        # Identify countries where debt exceeds health
        debt_exceeds_health = debt_exceeds_health_list
        if debt_exceeds_health:
            st.markdown(f"""
                <div style="margin-top: 1rem; padding: 1rem; background: #FEF2F2; border-radius: 0.5rem; border: 1px solid #FEE2E2;">
                    <div style="display: flex; align-items: start; gap: 0.75rem;">
                        <div style="margin-top: 0.125rem; height: 1.75rem; width: 1.75rem; border-radius: 9999px; background: rgba(239, 68, 68, 0.1); display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 0.875rem;">⚠️</span>
                        </div>
                        <div style="flex: 1;">
                            <p style="font-size: 0.75rem; font-weight: 500; color: #991B1B; margin-bottom: 0.25rem;">
                                Critical alert
                            </p>
                            <p style="font-size: 0.875rem; color: #7F1D1D; line-height: 1.5;">
                                {len(debt_exceeds_health)} countries spend more on debt service than health: {', '.join(debt_exceeds_health[:5])}{'...' if len(debt_exceeds_health) > 5 else ''}
                            </p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error creating social impact chart: {e}")
    
    # Add spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Opportunity cost panel
    st.markdown("""
        <div style="margin-bottom: 1rem;">
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
                Opportunity cost analysis
            </h3>
            <p style="font-size: 0.875rem; color: #64748B;">
                What debt payments could fund instead (based on median debt service)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        # Calculate median debt service for opportunity cost
        latest_data = filtered_df[filtered_df['year'] == latest_year]
        median_debt_service = latest_data['debt_service_usd'].median()
        
        if pd.notna(median_debt_service) and median_debt_service > 0:
            # Get opportunity cost panel data
            opp_cost = create_opportunity_cost_panel("Median Country", median_debt_service)

            render_opportunity_cost_summary(
                opp_cost,
                title="Median opportunity cost conversions",
                subtitle=f"Median country debt service in {latest_year} could fund:",
            )
        else:
            st.info("Insufficient data for opportunity cost analysis")
    except Exception as e:
        st.error(f"Error creating opportunity cost panel: {e}")
else:
    st.info("No data available for social impact analysis")

# Add spacing
st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SIMULATOR SECTION
# ============================================================================

# Import simulator component
from components.simulator import create_simulator_interface

# Display simulator
if not filtered_df.empty:
    try:
        create_simulator_interface(filtered_df, default_country='NGA')
    except Exception as e:
        st.error(f"Error loading simulator: {e}")
        st.info("The simulator component encountered an error. Please check the data and try again.")
        # Show error details in expander for debugging
        with st.expander("Error Details"):
            import traceback
            st.code(traceback.format_exc())
else:
    st.info("No data available for simulator")

# Add spacing
st.markdown("<br><br>", unsafe_allow_html=True)

# Footer CTA section
st.markdown("""
    <div style="padding: 3rem 2rem; background: linear-gradient(to right, #0F172A, #1E293B); border-radius: 0.75rem; text-align: center; color: white; margin-top: 2rem;">
        <h3 style="font-size: 1.75rem; font-weight: 600; margin-bottom: 1rem; color: white; letter-spacing: -0.025em;">
            Ready to explore debt restructuring scenarios?
        </h3>
        <p style="font-size: 1.125rem; color: #CBD5E1; margin-bottom: 2rem; line-height: 1.6; max-width: 600px; margin-left: auto; margin-right: auto;">
            Use the simulator above to model policy options and see their impact on fiscal space and social spending.
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin-bottom: 1.5rem;">
            <a href="#" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.875rem 1.75rem; background: white; color: #0F172A; border: none; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 500; text-decoration: none; transition: all 0.2s;">
                📊 Download Data
            </a>
            <a href="#" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.875rem 1.75rem; background: transparent; color: white; border: 1px solid white; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 500; text-decoration: none; transition: all 0.2s;">
                📖 View Methodology
            </a>
        </div>
        <div style="padding-top: 1.5rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">
            <p style="font-size: 0.875rem; color: #94A3B8; margin: 0;">
                Built for policymakers, researchers, and advocates • Data from World Bank & IMF APIs
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Additional footer with metadata
st.markdown("""
    <div style="margin-top: 2rem; padding: 1.5rem 0; border-top: 1px solid #E2E8F0;">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;">
            <div>
                <p style="font-size: 0.875rem; font-weight: 500; color: #0F172A; margin-bottom: 0.25rem;">
                    Africa Sovereign Debt Crisis Dashboard
                </p>
                <p style="font-size: 0.75rem; color: #64748B; margin: 0;">
                    Bringing transparency to debt data across 54 African countries
                </p>
            </div>
            <div style="display: flex; gap: 1.5rem; flex-wrap: wrap;">
                <a href="#" style="font-size: 0.75rem; color: #64748B; text-decoration: none; transition: color 0.2s;">
                    About
                </a>
                <a href="#" style="font-size: 0.75rem; color: #64748B; text-decoration: none; transition: color 0.2s;">
                    Data Sources
                </a>
                <a href="#" style="font-size: 0.75rem; color: #64748B; text-decoration: none; transition: color 0.2s;">
                    Methodology
                </a>
                <a href="#" style="font-size: 0.75rem; color: #64748B; text-decoration: none; transition: color 0.2s;">
                    Contact
                </a>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
