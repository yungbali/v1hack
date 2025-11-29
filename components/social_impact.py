"""
Social Impact Component for the Africa Sovereign Debt Crisis Dashboard.

This module provides visualizations comparing debt service payments against
social spending (health and education) and calculates opportunity costs to
communicate the human impact of debt obligations.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List
from utils.constants import COLORS, UNIT_COSTS


def create_comparison_bar_chart(df: pd.DataFrame, year: int = None) -> go.Figure:
    """
    Create grouped bar chart comparing debt service, health, and education spending.
    
    This visualization shows three bars per country representing:
    - Debt service (red)
    - Health spending (blue)
    - Education spending (green)
    
    Countries are sorted by debt service in descending order to highlight
    those with the highest debt burdens.
    
    Args:
        df: DataFrame with columns: country_name, debt_service_usd, gdp_usd,
            health_pct_gdp, education_pct_gdp, year
        year: Optional year to filter data. If None, uses most recent year.
    
    Returns:
        Plotly Figure object with grouped bar chart
        
    Requirements: 4.2, 4.3, 8.1
    """
    # Filter to specific year if provided, otherwise use most recent
    if year is not None:
        data = df[df['year'] == year].copy()
    else:
        latest_year = df['year'].max()
        data = df[df['year'] == latest_year].copy()
    
    # Calculate spending as % of GDP for comparison
    # Debt service as % of GDP
    data['debt_service_pct_gdp'] = (data['debt_service_usd'] / data['gdp_usd']) * 100
    
    # Health and education are already in % of GDP
    data['health_pct_gdp'] = data['health_pct_gdp']
    data['education_pct_gdp'] = data['education_pct_gdp']
    
    # Sort by debt service descending (Requirement 4.3)
    data = data.sort_values('debt_service_pct_gdp', ascending=False)
    
    # Remove rows with missing data
    data = data.dropna(subset=['country_name', 'debt_service_pct_gdp', 
                                'health_pct_gdp', 'education_pct_gdp'])
    
    # Create figure
    fig = go.Figure()
    
    # Add debt service bars (red)
    fig.add_trace(go.Bar(
        name='Debt Service',
        x=data['country_name'],
        y=data['debt_service_pct_gdp'],
        marker_color=COLORS['debt'],
        hovertemplate='<b>%{x}</b><br>' +
                      'Debt Service: %{y:.2f}% of GDP<br>' +
                      '<extra></extra>'
    ))
    
    # Add health spending bars (blue)
    fig.add_trace(go.Bar(
        name='Health Spending',
        x=data['country_name'],
        y=data['health_pct_gdp'],
        marker_color=COLORS['health'],
        hovertemplate='<b>%{x}</b><br>' +
                      'Health: %{y:.2f}% of GDP<br>' +
                      '<extra></extra>'
    ))
    
    # Add education spending bars (green)
    fig.add_trace(go.Bar(
        name='Education Spending',
        x=data['country_name'],
        y=data['education_pct_gdp'],
        marker_color=COLORS['education'],
        hovertemplate='<b>%{x}</b><br>' +
                      'Education: %{y:.2f}% of GDP<br>' +
                      '<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title='Debt Service vs Social Spending (% of GDP)',
        xaxis_title='Country',
        yaxis_title='Percentage of GDP',
        barmode='group',
        hovermode='closest',
        height=500,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def identify_countries_debt_exceeds_health(df: pd.DataFrame, year: int = None) -> List[str]:
    """
    Identify countries where debt service exceeds health spending.
    
    This function supports conditional highlighting by identifying which
    countries spend more on debt service than on health care, a key indicator
    of fiscal distress impacting social welfare.
    
    Args:
        df: DataFrame with columns: country_name, debt_service_usd, gdp_usd,
            health_pct_gdp, year
        year: Optional year to filter data. If None, uses most recent year.
    
    Returns:
        List of country names where debt service > health spending
        
    Requirements: 4.4
    """
    # Filter to specific year if provided, otherwise use most recent
    if year is not None:
        data = df[df['year'] == year].copy()
    else:
        latest_year = df['year'].max()
        data = df[df['year'] == latest_year].copy()
    
    # Calculate health spending in USD
    data['health_usd'] = data['gdp_usd'] * data['health_pct_gdp'] / 100
    
    # Identify countries where debt service > health spending
    debt_exceeds_health = data[data['debt_service_usd'] > data['health_usd']]
    
    # Return list of country names
    return debt_exceeds_health['country_name'].tolist()


def create_opportunity_cost_panel(
    country_name: str,
    debt_service_usd: float
) -> Dict[str, Dict[str, any]]:
    """
    Calculate and format opportunity cost conversions for display.
    
    This function converts debt service payments into tangible social spending
    units (schools, hospitals, vaccines, teachers) to communicate the human
    cost of debt obligations in relatable terms.
    
    Args:
        country_name: Name of the country
        debt_service_usd: Annual debt service in USD
    
    Returns:
        Dictionary with four keys (schools, hospitals, vaccine_doses, teachers),
        each containing:
            - quantity: Number of units that could be funded
            - unit_cost: Cost per unit in USD
            - emoji: Icon for display
            - label: Display label
            
    Requirements: 4.5, 8.2, 8.5
    
    Example:
        >>> panel = create_opportunity_cost_panel('Nigeria', 5_000_000_000)
        >>> print(f"Could fund {panel['schools']['quantity']} schools")
    """
    from utils.calculations import calculate_opportunity_cost
    
    # Calculate quantities for each unit type
    schools = calculate_opportunity_cost(debt_service_usd, 'school')
    hospitals = calculate_opportunity_cost(debt_service_usd, 'hospital')
    vaccine_doses = calculate_opportunity_cost(debt_service_usd, 'vaccine_dose')
    teachers = calculate_opportunity_cost(debt_service_usd, 'teacher')
    
    # Format results with display metadata
    result = {
        'schools': {
            'quantity': schools,
            'unit_cost': UNIT_COSTS['school'],
            'emoji': '🏫',
            'label': 'Primary Schools',
            'description': f'Could build {schools:,} primary schools'
        },
        'hospitals': {
            'quantity': hospitals,
            'unit_cost': UNIT_COSTS['hospital'],
            'emoji': '🏥',
            'label': 'District Hospitals',
            'description': f'Could build {hospitals:,} district hospitals'
        },
        'vaccine_doses': {
            'quantity': vaccine_doses,
            'unit_cost': UNIT_COSTS['vaccine_dose'],
            'emoji': '💉',
            'label': 'Vaccine Doses',
            'description': f'Could provide {vaccine_doses:,} vaccine doses'
        },
        'teachers': {
            'quantity': teachers,
            'unit_cost': UNIT_COSTS['teacher'],
            'emoji': '👨‍🏫',
            'label': 'Teacher Salaries',
            'description': f'Could pay {teachers:,} teachers annually'
        }
    }
    
    return result
