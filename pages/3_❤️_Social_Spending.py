"""
Social Spending Comparison Page
Dedicated page for comparing debt service against social spending
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Import utilities
from utils.constants import COLORS, THRESHOLDS, REGIONS, AFRICAN_COUNTRIES
from components.social_impact import (
    create_comparison_bar_chart,
    create_opportunity_cost_panel,
    identify_countries_debt_exceeds_health
)

# Page configuration
st.set_page_config(
    page_title="Social Spending - Africa Debt Dashboard",
    page_icon="❤️",
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
                ❤️ Social Spending Analysis
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
            ❤️ Social Spending vs Debt Service
        </h1>
        <p style="font-size: 1.125rem; color: #475569; line-height: 1.6;">
            Compare debt service payments against health and education spending to understand the human cost of debt obligations.
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

# Get latest year
latest_year = filtered_df['year'].max()
latest_data = filtered_df[filtered_df['year'] == latest_year]

# KPI Section
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Spending Priorities
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            How debt service compares to social spending across selected countries
        </p>
    </div>
""", unsafe_allow_html=True)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    # Median health spending
    if 'health_pct_gdp' in latest_data.columns:
        median_health = latest_data['health_pct_gdp'].median()
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                    Median Health Spending
                </p>
                <p style="font-size: 2rem; font-weight: 600; color: {COLORS['health']}; margin: 0;">
                    {median_health:.1f}%
                </p>
                <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                    of GDP
                </p>
            </div>
        """, unsafe_allow_html=True)

with kpi_col2:
    # Median education spending
    if 'education_pct_gdp' in latest_data.columns:
        median_education = latest_data['education_pct_gdp'].median()
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                    Median Education Spending
                </p>
                <p style="font-size: 2rem; font-weight: 600; color: {COLORS['education']}; margin: 0;">
                    {median_education:.1f}%
                </p>
                <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                    of GDP
                </p>
            </div>
        """, unsafe_allow_html=True)

with kpi_col3:
    # Countries where debt > health
    debt_exceeds_health = identify_countries_debt_exceeds_health(filtered_df, year=latest_year)
    count_debt_exceeds = len(debt_exceeds_health)
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                Debt > Health Spending
            </p>
            <p style="font-size: 2rem; font-weight: 600; color: {COLORS['debt']}; margin: 0;">
                {count_debt_exceeds}
            </p>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                countries
            </p>
        </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    # Combined social spending
    if 'health_pct_gdp' in latest_data.columns and 'education_pct_gdp' in latest_data.columns:
        median_social = (latest_data['health_pct_gdp'] + latest_data['education_pct_gdp']).median()
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                    Combined Social Spending
                </p>
                <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                    {median_social:.1f}%
                </p>
                <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                    of GDP (median)
                </p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Comparison Chart
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Spending Comparison by Country
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Debt service, health, and education spending as percentage of GDP
        </p>
    </div>
""", unsafe_allow_html=True)

try:
    with st.spinner('Creating comparison chart...'):
        comparison_chart = create_comparison_bar_chart(filtered_df, year=latest_year)
    st.plotly_chart(comparison_chart, width="stretch", key="social_comparison")
    
    # Alert for countries where debt exceeds health
    if debt_exceeds_health:
        st.markdown(f"""
            <div style="margin-top: 1rem; padding: 1rem; background: #FEF2F2; border-radius: 0.5rem; border: 1px solid #FEE2E2;">
                <div style="display: flex; align-items: start; gap: 0.75rem;">
                    <div style="margin-top: 0.125rem; height: 1.75rem; width: 1.75rem; border-radius: 9999px; background: rgba(239, 68, 68, 0.1); display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 0.875rem;">⚠️</span>
                    </div>
                    <div style="flex: 1;">
                        <p style="font-size: 0.75rem; font-weight: 500; color: #991B1B; margin-bottom: 0.25rem;">
                            Critical Alert
                        </p>
                        <p style="font-size: 0.875rem; color: #7F1D1D; line-height: 1.5;">
                            <strong>{count_debt_exceeds} countries</strong> spend more on debt service than health: {', '.join(debt_exceeds_health[:8])}{'...' if len(debt_exceeds_health) > 8 else ''}
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error creating comparison chart: {e}")

st.markdown("<br><br>", unsafe_allow_html=True)

# Opportunity Cost Analysis
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Opportunity Cost Analysis
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            What median debt service payments could fund instead
        </p>
    </div>
""", unsafe_allow_html=True)

try:
    # Calculate median debt service
    median_debt_service = latest_data['debt_service_usd'].median()
    
    if pd.notna(median_debt_service) and median_debt_service > 0:
        # Get opportunity cost data
        opp_cost = create_opportunity_cost_panel("Median Country", median_debt_service)
        
        # Display in 4-column grid
        opp_col1, opp_col2, opp_col3, opp_col4 = st.columns(4)
        
        with opp_col1:
            st.markdown(f"""
                <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1.5rem; text-align: center;">
                    <div style="height: 3.5rem; width: 3.5rem; border-radius: 0.5rem; background: #DBEAFE; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto;">
                        <span style="font-size: 2rem;">{opp_cost['schools']['emoji']}</span>
                    </div>
                    <p style="font-size: 2.25rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
                        {opp_cost['schools']['quantity']:,}
                    </p>
                    <p style="font-size: 1rem; font-weight: 500; color: #475569; margin-bottom: 0.5rem;">
                        {opp_cost['schools']['label']}
                    </p>
                    <p style="font-size: 0.75rem; color: #64748B;">
                        @ ${opp_cost['schools']['unit_cost']:,.0f} each
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with opp_col2:
            st.markdown(f"""
                <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1.5rem; text-align: center;">
                    <div style="height: 3.5rem; width: 3.5rem; border-radius: 0.5rem; background: #FEE2E2; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto;">
                        <span style="font-size: 2rem;">{opp_cost['hospitals']['emoji']}</span>
                    </div>
                    <p style="font-size: 2.25rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
                        {opp_cost['hospitals']['quantity']:,}
                    </p>
                    <p style="font-size: 1rem; font-weight: 500; color: #475569; margin-bottom: 0.5rem;">
                        {opp_cost['hospitals']['label']}
                    </p>
                    <p style="font-size: 0.75rem; color: #64748B;">
                        @ ${opp_cost['hospitals']['unit_cost']:,.0f} each
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with opp_col3:
            st.markdown(f"""
                <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1.5rem; text-align: center;">
                    <div style="height: 3.5rem; width: 3.5rem; border-radius: 0.5rem; background: #DCFCE7; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto;">
                        <span style="font-size: 2rem;">{opp_cost['vaccine_doses']['emoji']}</span>
                    </div>
                    <p style="font-size: 2.25rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
                        {opp_cost['vaccine_doses']['quantity']:,}
                    </p>
                    <p style="font-size: 1rem; font-weight: 500; color: #475569; margin-bottom: 0.5rem;">
                        {opp_cost['vaccine_doses']['label']}
                    </p>
                    <p style="font-size: 0.75rem; color: #64748B;">
                        @ ${opp_cost['vaccine_doses']['unit_cost']:,.0f} each
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with opp_col4:
            st.markdown(f"""
                <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1.5rem; text-align: center;">
                    <div style="height: 3.5rem; width: 3.5rem; border-radius: 0.5rem; background: #FEF3C7; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto;">
                        <span style="font-size: 2rem;">{opp_cost['teachers']['emoji']}</span>
                    </div>
                    <p style="font-size: 2.25rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
                        {opp_cost['teachers']['quantity']:,}
                    </p>
                    <p style="font-size: 1rem; font-weight: 500; color: #475569; margin-bottom: 0.5rem;">
                        {opp_cost['teachers']['label']}
                    </p>
                    <p style="font-size: 0.75rem; color: #64748B;">
                        @ ${opp_cost['teachers']['unit_cost']:,.0f} each
                    </p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Insufficient data for opportunity cost analysis")
except Exception as e:
    st.error(f"Error creating opportunity cost panel: {e}")

st.markdown("<br><br>", unsafe_allow_html=True)

# Insights
st.markdown("""
    <div style="padding: 1.5rem; background: #F8FAFC; border-radius: 0.75rem; border: 1px solid #E2E8F0;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
            💡 Key Insights
        </h3>
        <ul style="font-size: 0.875rem; color: #475569; line-height: 1.8; margin: 0; padding-left: 1.5rem;">
            <li>High debt service crowds out essential social spending on health and education</li>
            <li>Countries spending more on debt than health face severe public health challenges</li>
            <li>Debt relief could free up significant resources for development priorities</li>
            <li>The opportunity cost of debt service is measured in schools, hospitals, and lives</li>
            <li>Sustainable debt levels are essential for achieving SDG targets</li>
        </ul>
    </div>
""", unsafe_allow_html=True)
