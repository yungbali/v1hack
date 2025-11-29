"""
Country Deep Dive Page
Dedicated page for detailed country-level analysis and debt restructuring scenarios
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go

# Import utilities
from utils.constants import COLORS, THRESHOLDS, REGIONS, AFRICAN_COUNTRIES
from components.simulator import create_simulator_interface
from components.heatmap import create_africa_heatmap

# Page configuration
st.set_page_config(
    page_title="Country Deep Dive - Africa Debt Dashboard",
    page_icon="🔍",
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

# Load data
df = load_data()
data_available = not df.empty

# Sidebar - Country selector
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0 1.5rem 0; border-bottom: 1px solid #F1F5F9;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">
                🔍 Country Deep Dive
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Country selector
    st.markdown("**Select Country**")
    
    if data_available:
        # Get list of countries with data
        available_countries = sorted(df['country_name'].unique())
        
        # Default to Nigeria if available
        default_idx = 0
        if 'Nigeria' in available_countries:
            default_idx = available_countries.index('Nigeria')
        
        selected_country_name = st.selectbox(
            "Country",
            available_countries,
            index=default_idx,
            key="country_selector"
        )
        
        # Get country code
        selected_country_code = None
        for code, name in AFRICAN_COUNTRIES.items():
            if name == selected_country_name:
                selected_country_code = code
                break
    else:
        st.warning("No data available")
        selected_country_name = None
        selected_country_code = None
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick stats for selected country
    if selected_country_code and data_available:
        country_data = df[df['country_code'] == selected_country_code]
        if not country_data.empty:
            latest_year = country_data['year'].max()
            latest = country_data[country_data['year'] == latest_year].iloc[0]
            
            st.markdown("""
                <div style="padding: 1rem; background: #F8FAFC; border-radius: 0.5rem; border: 1px solid #E2E8F0;">
                    <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.75rem;">
                        Quick Stats
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            if 'debt_to_gdp' in latest:
                st.metric("Debt-to-GDP", f"{latest['debt_to_gdp']:.1f}%")
            
            if 'debt_service_usd' in latest:
                st.metric("Debt Service", f"${latest['debt_service_usd']/1e9:.2f}B")
            
            if 'gdp_usd' in latest:
                st.metric("GDP", f"${latest['gdp_usd']/1e9:.1f}B")

# Main content
st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.75rem;">
            🔍 Country Deep Dive
        </h1>
        <p style="font-size: 1.125rem; color: #475569; line-height: 1.6;">
            Detailed analysis and debt restructuring scenarios for individual countries.
        </p>
    </div>
""", unsafe_allow_html=True)

if not data_available:
    st.warning("⚠️ No data available. Please run the data fetching script first.")
    st.stop()

if not selected_country_code:
    st.info("Please select a country from the sidebar")
    st.stop()

# Get country data
country_df = df[df['country_code'] == selected_country_code]

if country_df.empty:
    st.warning(f"No data available for {selected_country_name}")
    st.stop()

# Country header
st.markdown(f"""
    <div style="padding: 1.5rem; background: linear-gradient(to right, #0F172A, #1E293B); border-radius: 0.75rem; margin-bottom: 2rem;">
        <h2 style="font-size: 2rem; font-weight: 600; color: white; margin-bottom: 0.5rem;">
            {selected_country_name}
        </h2>
        <p style="font-size: 1rem; color: #CBD5E1; margin: 0;">
            Comprehensive debt analysis and restructuring scenarios
        </p>
    </div>
""", unsafe_allow_html=True)

# Get latest year data
latest_year = country_df['year'].max()
latest_data = country_df[country_df['year'] == latest_year].iloc[0]

# Overview KPIs
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Current Debt Profile
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Key debt metrics as of {year}
        </p>
    </div>
""".format(year=latest_year), unsafe_allow_html=True)

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    debt_to_gdp = latest_data.get('debt_to_gdp', 0)
    risk_color = COLORS['debt'] if debt_to_gdp > 60 else (COLORS['bilateral'] if debt_to_gdp > 40 else COLORS['education'])
    
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                Debt-to-GDP Ratio
            </p>
            <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                {debt_to_gdp:.1f}%
            </p>
            <div style="margin-top: 0.5rem;">
                <span style="height: 0.5rem; width: 0.5rem; border-radius: 9999px; background: {risk_color}; display: inline-block;"></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    total_debt = latest_data.get('total_debt_usd', 0) / 1e9
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                Total External Debt
            </p>
            <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                ${total_debt:.1f}B
            </p>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                USD
            </p>
        </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    debt_service = latest_data.get('debt_service_usd', 0) / 1e9
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                Annual Debt Service
            </p>
            <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                ${debt_service:.2f}B
            </p>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                Per year
            </p>
        </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    gdp = latest_data.get('gdp_usd', 0) / 1e9
    st.markdown(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: white; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.5rem;">
                GDP
            </p>
            <p style="font-size: 2rem; font-weight: 600; color: #0F172A; margin: 0;">
                ${gdp:.1f}B
            </p>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.5rem;">
                Current USD
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Historical trends
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Historical Trends
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Debt metrics over time (2014-2024)
        </p>
    </div>
""", unsafe_allow_html=True)

# Create time series chart
trend_col1, trend_col2 = st.columns(2)

with trend_col1:
    # Debt-to-GDP over time
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=country_df['year'],
        y=country_df['debt_to_gdp'],
        mode='lines+markers',
        name='Debt-to-GDP',
        line=dict(color=COLORS['debt'], width=3),
        marker=dict(size=8)
    ))
    
    # Add threshold lines
    fig1.add_hline(y=60, line_dash="dash", line_color=COLORS['debt'], 
                   annotation_text="High risk (60%)", annotation_position="right")
    fig1.add_hline(y=40, line_dash="dash", line_color=COLORS['bilateral'],
                   annotation_text="Moderate risk (40%)", annotation_position="right")
    
    fig1.update_layout(
        title="Debt-to-GDP Ratio Over Time",
        xaxis_title="Year",
        yaxis_title="Debt-to-GDP (%)",
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, sans-serif", size=12, color="#475569"),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig1, width="stretch", key="debt_trend")

with trend_col2:
    # Debt service over time
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=country_df['year'],
        y=country_df['debt_service_usd'] / 1e9,
        mode='lines+markers',
        name='Debt Service',
        line=dict(color=COLORS['bilateral'], width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(243, 156, 18, 0.1)'
    ))
    
    fig2.update_layout(
        title="Annual Debt Service Payments",
        xaxis_title="Year",
        yaxis_title="Debt Service ($ Billions)",
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, sans-serif", size=12, color="#475569"),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, width="stretch", key="service_trend")

st.markdown("<br><br>", unsafe_allow_html=True)

# Debt Restructuring Simulator
st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
            Debt Restructuring Simulator
        </h2>
        <p style="font-size: 0.875rem; color: #64748B;">
            Model different restructuring scenarios and see their impact on fiscal space
        </p>
    </div>
""", unsafe_allow_html=True)

# Display simulator
try:
    create_simulator_interface(country_df, default_country=selected_country_code)
except Exception as e:
    st.error(f"Error loading simulator: {e}")

st.markdown("<br><br>", unsafe_allow_html=True)

# Additional insights
st.markdown("""
    <div style="padding: 1.5rem; background: #F8FAFC; border-radius: 0.75rem; border: 1px solid #E2E8F0;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #0F172A; margin-bottom: 1rem;">
            💡 Analysis Notes
        </h3>
        <ul style="font-size: 0.875rem; color: #475569; line-height: 1.8; margin: 0; padding-left: 1.5rem;">
            <li>Use the simulator above to explore different restructuring options</li>
            <li>Adjust interest rates, maturity extensions, and principal haircuts to see fiscal impact</li>
            <li>Compare current vs. reformed scenarios to understand potential savings</li>
            <li>Consider creditor composition when evaluating restructuring feasibility</li>
        </ul>
    </div>
""", unsafe_allow_html=True)
