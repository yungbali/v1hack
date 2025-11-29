"""
Country Scenario Simulator Component

This module provides the interactive debt restructuring simulator interface
that allows users to model policy scenarios and see their fiscal impact.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict
from textwrap import dedent
from utils.constants import COLORS, AFRICAN_COUNTRIES
from utils.calculations import (
    calculate_restructuring_impact,
    calculate_opportunity_cost
)
from components.pan_african import render_reform_results_summary


def create_simulator_interface(df: pd.DataFrame, default_country: str = 'NGA') -> None:
    """
    Create the interactive simulator interface with two-column layout.
    
    This function renders the complete simulator UI with:
    - Current state display (left column)
    - Scenario controls and results (right column)
    
    Args:
        df: DataFrame with country debt data
        default_country: Default country code to display (default: 'NGA' for Nigeria)
    
    Requirements:
        - 5.1: Display current state metrics
        - 5.2: Provide interactive scenario controls
        - 8.5: Match design mockup styling
    """
    # Check if DataFrame is empty
    if df.empty:
        st.warning("No data available for simulator. Please check your data source.")
        return
    
    # Check for required columns
    required_columns = ['country_code', 'country_name', 'year', 'debt_to_gdp', 
                       'total_debt_usd', 'debt_service_usd', 'gdp_usd']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns for simulator: {', '.join(missing_columns)}")
        st.info("Please ensure your data includes all required debt metrics.")
        return
    
    # Section header
    st.markdown(dedent("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h2 style="font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin-bottom: 0.5rem;">
                        Country scenario simulator
                    </h2>
                    <p style="font-size: 0.875rem; color: #64748B;">
                        Model debt restructuring scenarios and see immediate fiscal impact.
                    </p>
                </div>
                <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.375rem 0.75rem; background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 0.375rem;">
                    <span style="height: 0.375rem; width: 0.375rem; border-radius: 9999px; background: #22C55E;"></span>
                    <span style="font-size: 0.75rem; font-weight: 500; color: #15803D;">Synced with filters</span>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)
    
    # Country selector
    country_options = sorted(AFRICAN_COUNTRIES.values())
    
    # Get default country name
    default_country_name = AFRICAN_COUNTRIES.get(default_country, 'Nigeria')
    default_index = country_options.index(default_country_name) if default_country_name in country_options else 0
    
    selected_country_name = st.selectbox(
        "Select country for simulation",
        country_options,
        index=default_index,
        key="simulator_country"
    )
    
    # Get country code from name
    selected_country_code = None
    for code, name in AFRICAN_COUNTRIES.items():
        if name == selected_country_name:
            selected_country_code = code
            break
    
    if selected_country_code is None:
        st.error("Country not found")
        return
    
    # Filter data for selected country
    country_data = df[df['country_code'] == selected_country_code].copy()
    
    if country_data.empty:
        st.warning(f"No data available for {selected_country_name}")
        return
    
    # Get most recent year data
    latest_year = country_data['year'].max()
    latest_data = country_data[country_data['year'] == latest_year].iloc[0]
    
    # Create two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Display current state
        _display_current_state(latest_data, selected_country_name)
    
    with col2:
        # Display scenario controls and results
        _display_scenario_controls(latest_data, selected_country_name)


def _display_current_state(data: pd.Series, country_name: str) -> None:
    """
    Display current state metrics in a styled card.
    
    Args:
        data: Series with country data for latest year
        country_name: Name of the country
    
    Requirements:
        - 5.1: Show current metrics
        - 8.2: Match mockup styling
    """
    # Extract current metrics
    debt_to_gdp = data.get('debt_to_gdp', 0)
    debt_service_usd = data.get('debt_service_usd', 0)
    gdp_usd = data.get('gdp_usd', 1)
    
    # Handle missing or zero values
    if debt_service_usd == 0 or pd.isna(debt_service_usd):
        debt_service_usd = 0
    
    # Calculate annual debt service in billions
    debt_service_billions = debt_service_usd / 1_000_000_000
    
    # Calculate fiscal space (simplified as revenue - debt service)
    revenue_pct_gdp = data.get('revenue_pct_gdp', 0)
    revenue_usd = gdp_usd * revenue_pct_gdp / 100
    fiscal_space_usd = revenue_usd - debt_service_usd
    fiscal_space_billions = fiscal_space_usd / 1_000_000_000
    
    st.markdown(dedent(f"""
        <div style="border-radius: 0.75rem; border: 1px solid #E2E8F0; background: #F8FAFC; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">
                    Current state
                </h3>
                <span style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.25rem 0.5rem; background: white; border: 1px solid #E2E8F0; border-radius: 0.25rem; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.14em; color: #64748B;">
                    Baseline
                </span>
            </div>
            
            <!-- Metric 1: Annual Debt Service -->
            <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #E2E8F0;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                    Annual debt service
                </p>
                <p style="font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                    ${debt_service_billions:.2f}B
                </p>
            </div>
            
            <!-- Metric 2: Debt-to-GDP -->
            <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #E2E8F0;">
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                    Debt-to-GDP ratio
                </p>
                <p style="font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                    {debt_to_gdp:.1f}%
                </p>
            </div>
            
            <!-- Metric 3: Fiscal Space -->
            <div>
                <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.25rem;">
                    Fiscal space available
                </p>
                <p style="font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: #0F172A; margin: 0;">
                    ${fiscal_space_billions:.2f}B
                </p>
                <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.25rem;">
                    Revenue minus debt service
                </p>
            </div>
        </div>
    """), unsafe_allow_html=True)


def _display_scenario_controls(data: pd.Series, country_name: str) -> None:
    """
    Display scenario control sliders and results.
    
    Args:
        data: Series with country data for latest year
        country_name: Name of the country
    
    Requirements:
        - 5.2: Provide interactive sliders
        - 5.3: Wire up calculations
        - 5.4: Show instant impact
        - 5.5: Display results in green card
        - 8.5: Match mockup design
    """
    st.markdown(dedent("""
        <div style="margin-bottom: 1rem;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 0.5rem;">
                Reform scenario parameters
            </h3>
            <p style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.5rem;">
                Adjust sliders to model debt restructuring impact
            </p>
            <div style="padding: 0.75rem; background: #FEF3C7; border: 1px solid #FDE68A; border-radius: 0.5rem;">
                <p style="font-size: 0.75rem; color: #92400E; margin: 0;">
                    💡 <strong>Tip:</strong> Move the sliders above to see how different restructuring options affect debt payments and fiscal space
                </p>
            </div>
        </div>
    """), unsafe_allow_html=True)
    
    # Scenario control sliders
    st.markdown('<div style="background: white; border: 1px solid #E2E8F0; border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    
    # Interest rate reduction slider
    interest_reduction = st.slider(
        "Interest rate reduction",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.1,
        format="%.1f%%",
        key="interest_reduction",
        help="Reduce the interest rate by this percentage"
    )
    st.markdown('<p style="font-size: 0.75rem; color: #64748B; margin-top: -0.5rem; margin-bottom: 1rem;">Lower rates reduce annual payments</p>', unsafe_allow_html=True)
    
    # Maturity extension slider
    maturity_extension = st.slider(
        "Maturity extension",
        min_value=0,
        max_value=10,
        value=0,
        step=1,
        format="%d years",
        key="maturity_extension",
        help="Extend the loan maturity by this many years"
    )
    st.markdown('<p style="font-size: 0.75rem; color: #64748B; margin-top: -0.5rem; margin-bottom: 1rem;">Longer maturity spreads payments over more years</p>', unsafe_allow_html=True)
    
    # Principal haircut slider
    haircut_pct = st.slider(
        "Principal haircut",
        min_value=0,
        max_value=50,
        value=0,
        step=1,
        format="%d%%",
        key="haircut_pct",
        help="Reduce the principal by this percentage"
    )
    st.markdown('<p style="font-size: 0.75rem; color: #64748B; margin-top: -0.5rem;">Direct reduction in total debt owed</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate restructuring impact
    current_debt = data.get('total_debt_usd', 0)
    current_debt_service = data.get('debt_service_usd', 0)
    gdp_usd = data.get('gdp_usd', 1)
    
    # Use default values if creditor data not available
    current_rate = data.get('avg_interest_rate', 5.0)
    if current_rate > 1:  # If it's a percentage, convert to decimal
        current_rate = current_rate / 100
    current_maturity = data.get('avg_maturity_years', 10)
    
    # If we have actual debt service, use it as the baseline
    # This ensures the "no reform" scenario shows the correct current payment
    if current_debt_service > 0 and current_debt > 0:
        # Back-calculate an effective rate that matches the actual debt service
        # This is a simplification but ensures consistency
        # Using the annuity formula: payment = principal * (r * (1+r)^n) / ((1+r)^n - 1)
        # We'll use the provided rate and maturity, but adjust if needed
        pass  # Keep the defaults for now
    
    # New rate after reduction
    new_rate = max(0, current_rate - (interest_reduction / 100))
    
    # Calculate impact
    impact = calculate_restructuring_impact(
        current_debt=current_debt,
        current_rate=current_rate,
        current_maturity=current_maturity,
        new_rate=new_rate,
        maturity_extension=maturity_extension,
        haircut_pct=haircut_pct,
        gdp_usd=gdp_usd
    )
    
    # Override the current_annual_payment with actual debt service if available
    # This ensures the baseline is accurate
    if current_debt_service > 0:
        actual_current_payment = current_debt_service
        impact['current_annual_payment'] = actual_current_payment
        # Recalculate fiscal space freed based on actual current payment
        impact['fiscal_space_freed'] = actual_current_payment - impact['new_annual_payment']
    
    # Display results
    _display_scenario_results(impact, data)


def _display_scenario_results(impact: Dict[str, float], data: pd.Series) -> None:
    """
    Display reform scenario results in a green-tinted card.
    
    Args:
        impact: Dictionary with restructuring impact metrics
        data: Series with country data for latest year
    
    Requirements:
        - 5.4: Show new metrics
        - 5.5: Display fiscal space composition
        - 8.2: Match mockup styling
    """
    new_annual_payment = impact['new_annual_payment'] / 1_000_000_000
    fiscal_space_freed = impact['fiscal_space_freed'] / 1_000_000_000
    new_debt_to_gdp = impact.get('new_debt_to_gdp', 0)
    
    # Calculate percentage change
    current_payment = impact['current_annual_payment']
    if current_payment > 0:
        payment_reduction_pct = (fiscal_space_freed * 1_000_000_000 / current_payment) * 100
    else:
        payment_reduction_pct = 0
    
    render_reform_results_summary(
        instant_impact_value=fiscal_space_freed,
        payment_reduction_pct=payment_reduction_pct,
        new_annual_debt_service=new_annual_payment,
        debt_to_gdp_year5=new_debt_to_gdp,
        fiscal_space_freed_value=fiscal_space_freed,
    )
    
    # Fiscal space composition (opportunity cost breakdown)
    if fiscal_space_freed > 0:
        st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
        _display_fiscal_space_composition(fiscal_space_freed * 1_000_000_000)
        st.markdown('</div>', unsafe_allow_html=True)


def _display_fiscal_space_composition(fiscal_space_usd: float) -> None:
    """
    Display fiscal space composition showing potential social spending.
    
    Args:
        fiscal_space_usd: Fiscal space freed in USD
    
    Requirements:
        - 5.5: Show fiscal space composition
    """
    # Calculate opportunity costs
    schools = calculate_opportunity_cost(fiscal_space_usd, 'school')
    hospitals = calculate_opportunity_cost(fiscal_space_usd, 'hospital')
    vaccines = calculate_opportunity_cost(fiscal_space_usd, 'vaccine_dose')
    teachers = calculate_opportunity_cost(fiscal_space_usd, 'teacher')
    
    st.markdown(dedent("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 0.75rem; padding: 1rem;">
            <p style="font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.16em; color: #64748B; margin-bottom: 0.75rem;">
                Freed fiscal space could fund
            </p>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem;">
    """), unsafe_allow_html=True)
    
    # Schools
    # Schools
    st.markdown(dedent(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="height: 2rem; width: 2rem; border-radius: 0.375rem; background: #DBEAFE; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1rem;">🏫</span>
            </div>
            <div>
                <p style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">{schools:,}</p>
                <p style="font-size: 0.7rem; color: #64748B; margin: 0;">Schools</p>
            </div>
        </div>
    """), unsafe_allow_html=True)
    
    # Hospitals
    # Hospitals
    st.markdown(dedent(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="height: 2rem; width: 2rem; border-radius: 0.375rem; background: #FEE2E2; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1rem;">🏥</span>
            </div>
            <div>
                <p style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">{hospitals:,}</p>
                <p style="font-size: 0.7rem; color: #64748B; margin: 0;">Hospitals</p>
            </div>
        </div>
    """), unsafe_allow_html=True)
    
    # Vaccines
    # Vaccines
    st.markdown(dedent(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="height: 2rem; width: 2rem; border-radius: 0.375rem; background: #DCFCE7; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1rem;">💉</span>
            </div>
            <div>
                <p style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">{vaccines:,}</p>
                <p style="font-size: 0.7rem; color: #64748B; margin: 0;">Vaccines</p>
            </div>
        </div>
    """), unsafe_allow_html=True)
    
    # Teachers
    # Teachers
    st.markdown(dedent(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="height: 2rem; width: 2rem; border-radius: 0.375rem; background: #FEF3C7; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1rem;">👨‍🏫</span>
            </div>
            <div>
                <p style="font-size: 1rem; font-weight: 600; color: #0F172A; margin: 0;">{teachers:,}</p>
                <p style="font-size: 0.7rem; color: #64748B; margin: 0;">Teachers</p>
            </div>
        </div>
    """), unsafe_allow_html=True)
    
    st.markdown(dedent("""
            </div>
        </div>
    """), unsafe_allow_html=True)
