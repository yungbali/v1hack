"""
Creditor Mix Analysis Page
Dedicated page for analyzing creditor composition and debt structure
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Import utilities
from utils.constants import COLORS, THRESHOLDS, REGIONS, AFRICAN_COUNTRIES

# Page configuration
st.set_page_config(
    page_title="Creditor Mix - Africa Debt Dashboard",
    page_icon="🏦",
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

# Load data
df = load_data()
data_available = not df.empty

# Sidebar filters
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #F1F5F9;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">
                🏦 Creditor Mix Analysis
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

# Main content
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.75rem;">
            🏦 Creditor Mix Analysis
        </h1>
        <p style="font-size: 1.125rem; color: #475569; line-height: 1.6;">
            Understand the composition of African debt by creditor type and analyze how creditor structure affects restructuring options.
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

if filtered_df.empty:
    st.info("No data available for selected filters")
    st.stop()

# Get latest year data
latest_year = filtered_df['year'].max()
latest_data = filtered_df[filtered_df['year'] == latest_year]

# KPI Section
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Creditor Composition Overview
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Breakdown of debt by creditor type across selected countries
        </p>
    </div>
""", unsafe_allow_html=True)

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    # Multilateral creditors
    if 'creditor_multilateral_pct' in latest_data.columns:
        avg_multilateral = latest_data['creditor_multilateral_pct'].mean()
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="height: 0.75rem; width: 0.75rem; border-radius: 9999px; background: {COLORS['multilateral']};"></div>
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin: 0;">
                        Multilateral
                    </p>
                </div>
                <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                    {avg_multilateral:.1f}%
                </p>
                <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                    World Bank, IMF, AfDB
                </p>
            </div>
        """, unsafe_allow_html=True)

with kpi_col2:
    # Bilateral creditors
    if 'creditor_bilateral_pct' in latest_data.columns:
        avg_bilateral = latest_data['creditor_bilateral_pct'].mean()
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="height: 0.75rem; width: 0.75rem; border-radius: 9999px; background: {COLORS['bilateral']};"></div>
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin: 0;">
                        Bilateral
                    </p>
                </div>
                <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                    {avg_bilateral:.1f}%
                </p>
                <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                    China, Paris Club, others
                </p>
            </div>
        """, unsafe_allow_html=True)

with kpi_col3:
    # Commercial creditors
    if 'creditor_commercial_pct' in latest_data.columns:
        avg_commercial = latest_data['creditor_commercial_pct'].mean()
        st.markdown(f"""
            <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="height: 0.75rem; width: 0.75rem; border-radius: 9999px; background: {COLORS['commercial']};"></div>
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin: 0;">
                        Commercial
                    </p>
                </div>
                <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                    {avg_commercial:.1f}%
                </p>
                <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                    Bonds, private lenders
                </p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Creditor Mix by Country
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Creditor Mix by Country
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Stacked bar chart showing creditor composition for each country
        </p>
    </div>
""", unsafe_allow_html=True)

# Create stacked bar chart
if all(col in latest_data.columns for col in ['creditor_multilateral_pct', 'creditor_bilateral_pct', 'creditor_commercial_pct']):
    # Prepare data
    chart_data = latest_data.sort_values('debt_to_gdp', ascending=False).head(30)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Multilateral',
        x=chart_data['country_name'],
        y=chart_data['creditor_multilateral_pct'],
        marker_color=COLORS['multilateral'],
        hovertemplate='<b>%{x}</b><br>Multilateral: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        name='Bilateral',
        x=chart_data['country_name'],
        y=chart_data['creditor_bilateral_pct'],
        marker_color=COLORS['bilateral'],
        hovertemplate='<b>%{x}</b><br>Bilateral: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        name='Commercial',
        x=chart_data['country_name'],
        y=chart_data['creditor_commercial_pct'],
        marker_color=COLORS['commercial'],
        hovertemplate='<b>%{x}</b><br>Commercial: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        barmode='stack',
        height=500,
        xaxis_title="",
        yaxis_title="Creditor Composition (%)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, sans-serif", size=12, color="#475569"),
        xaxis=dict(tickangle=-45, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#F1F5F9'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    st.plotly_chart(fig, use_container_width=True, key="creditor_mix_bar")
else:
    st.info("Creditor composition data not available")

st.markdown("<br><br>", unsafe_allow_html=True)

# Creditor Type Characteristics
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Understanding Creditor Types
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Key characteristics and implications for debt restructuring
        </p>
    </div>
""", unsafe_allow_html=True)

cred_col1, cred_col2, cred_col3 = st.columns(3)

with cred_col1:
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1.5rem;">
            <div style="height: 3rem; width: 3rem; border-radius: 0.5rem; background: {COLORS['multilateral']}20; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🏛️</span>
            </div>
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 0.75rem;">
                Multilateral Creditors
            </h3>
            <ul style="font-size: 0.875rem; color: #475569; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>World Bank, IMF, AfDB</li>
                <li>Typically lower interest rates</li>
                <li>Longer maturities</li>
                <li>Preferred creditor status</li>
                <li>Less flexible on restructuring</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with cred_col2:
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1.5rem;">
            <div style="height: 3rem; width: 3rem; border-radius: 0.5rem; background: {COLORS['bilateral']}20; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">🤝</span>
            </div>
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 0.75rem;">
                Bilateral Creditors
            </h3>
            <ul style="font-size: 0.875rem; color: #475569; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>China, Paris Club members</li>
                <li>Variable interest rates</li>
                <li>Medium-term maturities</li>
                <li>Political considerations</li>
                <li>More negotiable terms</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with cred_col3:
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1.5rem;">
            <div style="height: 3rem; width: 3rem; border-radius: 0.5rem; background: {COLORS['commercial']}20; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">💼</span>
            </div>
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 0.75rem;">
                Commercial Creditors
            </h3>
            <ul style="font-size: 0.875rem; color: #475569; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>Bondholders, private banks</li>
                <li>Higher interest rates</li>
                <li>Shorter maturities</li>
                <li>Market-driven terms</li>
                <li>Collective action challenges</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Insights
st.markdown("""
    <div style="padding: 1.5rem; background: #F8FAFC; border-radius: 0.75rem; border: 1px solid #E2E8F0;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
            💡 Key Insights
        </h3>
        <ul style="font-size: 0.875rem; color: #475569; line-height: 1.8; margin: 0; padding-left: 1.5rem;">
            <li>Countries with diverse creditor bases face more complex restructuring negotiations</li>
            <li>High commercial debt exposure increases vulnerability to market sentiment</li>
            <li>Multilateral debt is rarely restructured, limiting fiscal relief options</li>
            <li>China's bilateral lending has grown significantly, changing negotiation dynamics</li>
            <li>Creditor coordination is essential for successful debt restructuring</li>
        </ul>
    </div>
""", unsafe_allow_html=True)
