"""
Debt Service Pressure Analysis Page
Dedicated page for analyzing debt service payments relative to government revenue
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Import utilities
from utils.constants import COLORS, THRESHOLDS, REGIONS, AFRICAN_COUNTRIES
from utils.calculations import calculate_kpi_metrics
from components.debt_service import create_debt_service_bar_chart, create_creditor_stacked_area

# Page configuration
st.set_page_config(
    page_title="Debt Service Analysis - Africa Debt Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    """Load custom CSS from assets/style.css"""
    css_file = Path("assets/style.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        footer {visibility: hidden;}
        .stApp {background-color: #F9FAFB;}
        [data-testid="stSidebar"] {background-color: white; border-right: 1px solid #E2E8F0;}
        [data-testid="stSidebarNav"] {padding-top: 1rem;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        </style>
    """, unsafe_allow_html=True)

load_css()

# Load cached data
@st.cache_data
def load_data():
    """Load dashboard data from parquet cache"""
    cache_path = Path("data/cached/dashboard_data.parquet")
    if not cache_path.exists():
        cache_path = Path("data/cached/test_cache.parquet")
    
    if cache_path.exists():
        return pd.read_parquet(cache_path)
    else:
        return pd.DataFrame()

# Filter functions
def filter_by_year_range(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    if df.empty or 'year' not in df.columns:
        return df
    return df[(df['year'] >= start_year) & (df['year'] <= end_year)]

def filter_by_region(df: pd.DataFrame, region: str) -> pd.DataFrame:
    if df.empty or 'country_code' not in df.columns or region not in REGIONS:
        return df
    return df[df['country_code'].isin(REGIONS[region])]

def filter_by_country(df: pd.DataFrame, country_code: str) -> pd.DataFrame:
    if df.empty or 'country_code' not in df.columns:
        return df
    return df[df['country_code'] == country_code]

# Load data
df = load_data()
data_available = not df.empty

# Sidebar filters
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #F1F5F9;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">
                📊 Debt Service Analysis
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filters
    st.markdown("**Filters**")
    
    region_options = ["All Regions"] + list(REGIONS.keys())
    selected_region = st.selectbox("Region", region_options, key="region_filter")
    
    year_range = st.slider(
        "Year Range",
        min_value=2014,
        max_value=2024,
        value=(2020, 2024),
        key="year_range_filter"
    )
    
    country_options = ["All Countries"] + sorted(AFRICAN_COUNTRIES.values())
    selected_country = st.selectbox("Focus Country", country_options, key="country_filter")

# Main content
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.75rem;">
            📊 Debt Service Pressure Analysis
        </h1>
        <p style="font-size: 1.125rem; color: #475569; line-height: 1.6;">
            Analyze annual debt service payments relative to government revenue and understand creditor composition across African countries.
        </p>
    </div>
""", unsafe_allow_html=True)

if not data_available:
    st.warning("⚠️ No data available. Please run the data fetching script first.")
    st.stop()

# Apply filters
filtered_df = df.copy()

if 'year_range_filter' in st.session_state:
    year_start, year_end = st.session_state.year_range_filter
    filtered_df = filter_by_year_range(filtered_df, year_start, year_end)

if 'region_filter' in st.session_state and st.session_state.region_filter != "All Regions":
    filtered_df = filter_by_region(filtered_df, st.session_state.region_filter)

if 'country_filter' in st.session_state and st.session_state.country_filter != "All Countries":
    country_code = None
    for code, name in AFRICAN_COUNTRIES.items():
        if name == st.session_state.country_filter:
            country_code = code
            break
    if country_code:
        filtered_df = filter_by_country(filtered_df, country_code)

if filtered_df.empty:
    st.info("No data available for selected filters")
    st.stop()

# KPI Section
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Key Metrics
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Overview of debt service burden across selected countries
        </p>
    </div>
""", unsafe_allow_html=True)

# Calculate KPIs
latest_year = filtered_df['year'].max()
latest_data = filtered_df[filtered_df['year'] == latest_year]

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    # Average debt service as % of revenue
    if 'debt_service_usd' in latest_data.columns and 'revenue_pct_gdp' in latest_data.columns:
        avg_debt_service_pct = (
            latest_data['debt_service_usd'] / 
            (latest_data['gdp_usd'] * latest_data['revenue_pct_gdp'] / 100)
        ).mean() * 100
        
        risk_color = COLORS['debt'] if avg_debt_service_pct > 30 else (
            COLORS['bilateral'] if avg_debt_service_pct > 20 else COLORS['education']
        )
        
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                    Avg Debt Service / Revenue
                </p>
                <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                    {avg_debt_service_pct:.1f}%
                </p>
                <div style="margin-top: 0.5rem;">
                    <span style="height: 0.5rem; width: 0.5rem; border-radius: 9999px; background: {risk_color}; display: inline-block;"></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

with kpi_col2:
    # Total debt service
    total_debt_service = latest_data['debt_service_usd'].sum() / 1e9
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                Total Debt Service
            </p>
            <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                ${total_debt_service:.1f}B
            </p>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                Annual payments ({latest_year})
            </p>
        </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    # Countries in high burden
    high_burden_count = (
        (latest_data['debt_service_usd'] / (latest_data['gdp_usd'] * latest_data['revenue_pct_gdp'] / 100) * 100) > 30
    ).sum()
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                High Burden Countries
            </p>
            <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                {high_burden_count}
            </p>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                Debt service > 30% revenue
            </p>
        </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    # Median debt service
    median_debt_service = latest_data['debt_service_usd'].median() / 1e9
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                Median Debt Service
            </p>
            <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                ${median_debt_service:.2f}B
            </p>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                Per country
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Charts Section
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Debt Service Analysis
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Country-by-country breakdown and creditor composition over time
        </p>
    </div>
""", unsafe_allow_html=True)

# Create 2-column layout
chart_col1, chart_col2 = st.columns([1, 1])

with chart_col1:
    st.markdown("""
        <div style="margin-bottom: 1rem;">
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 0.25rem;">
                Debt Service by Country
            </h3>
            <p style="font-size: 0.875rem; color: #64748B;">
                As percentage of government revenue (color-coded by risk level)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        with st.spinner('Creating debt service chart...'):
            bar_chart = create_debt_service_bar_chart(filtered_df, year=latest_year, top_n=25)
        st.plotly_chart(bar_chart, use_container_width=True, key="debt_service_bar")
    except Exception as e:
        st.error(f"Error creating chart: {e}")

with chart_col2:
    st.markdown("""
        <div style="margin-bottom: 1rem;">
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 0.25rem;">
                Creditor Composition Over Time
            </h3>
            <p style="font-size: 0.875rem; color: #64748B;">
                Debt service payments by creditor type (multilateral, bilateral, commercial)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        with st.spinner('Creating creditor composition chart...'):
            area_chart = create_creditor_stacked_area(filtered_df)
        st.plotly_chart(area_chart, use_container_width=True, key="creditor_area")
    except Exception as e:
        st.error(f"Error creating chart: {e}")

st.markdown("<br><br>", unsafe_allow_html=True)

# Insights Section
st.markdown("""
    <div style="padding: 1.5rem; background: #F8FAFC; border-radius: 0.75rem; border: 1px solid #E2E8F0;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
            💡 Key Insights
        </h3>
        <ul style="font-size: 0.875rem; color: #475569; line-height: 1.8; margin: 0; padding-left: 1.5rem;">
            <li>Countries with debt service exceeding 30% of revenue face severe fiscal constraints</li>
            <li>Creditor composition affects restructuring options and negotiation leverage</li>
            <li>Commercial debt typically has higher interest rates and shorter maturities</li>
            <li>Multilateral creditors often provide more favorable terms but less flexibility</li>
        </ul>
    </div>
""", unsafe_allow_html=True)
