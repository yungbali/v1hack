"""
Debt Service Pressure Components for the Africa Sovereign Debt Crisis Dashboard.

This module provides visualization components for analyzing debt service pressure
and creditor composition across African countries.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
from utils.constants import COLORS, THRESHOLDS


def assign_debt_service_color(debt_service_pct: float) -> str:
    """
    Assign color based on debt service pressure thresholds.
    
    This function implements the color coding logic for debt service
    as percentage of government revenue:
    - Red: High pressure (>30%)
    - Yellow: Moderate pressure (20-30%)
    - Green: Low pressure (<20%)
    
    Args:
        debt_service_pct: Debt service as percentage of government revenue
    
    Returns:
        Hex color code string
        
    Requirements: 3.3
    
    Example:
        >>> assign_debt_service_color(35.0)
        '#E74C3C'  # Red
        >>> assign_debt_service_color(25.0)
        '#F39C12'  # Yellow
        >>> assign_debt_service_color(15.0)
        '#2ECC71'  # Green
    """
    if debt_service_pct > THRESHOLDS['debt_service_high']:
        return COLORS['debt']  # Red
    elif debt_service_pct >= THRESHOLDS['debt_service_moderate']:
        return COLORS['bilateral']  # Yellow/Orange
    else:
        return COLORS['education']  # Green


def create_debt_service_bar_chart(
    df: pd.DataFrame,
    year: Optional[int] = None,
    top_n: Optional[int] = None
) -> go.Figure:
    """
    Create sortable horizontal bar chart of debt service as % of revenue.
    
    This chart visualizes debt service pressure across countries, with
    color coding to indicate risk levels. Bars are sorted by debt service
    percentage in descending order.
    
    Args:
        df: DataFrame with columns: country_name, debt_service_usd, gdp_usd,
            revenue_pct_gdp, year
        year: Optional year to filter (defaults to most recent)
        top_n: Optional limit to top N countries by debt service pressure
    
    Returns:
        Plotly Figure object with horizontal bar chart
        
    Requirements: 3.2, 3.4, 8.1
    
    Example:
        >>> fig = create_debt_service_bar_chart(df, year=2024, top_n=20)
        >>> fig.show()
    """
    # Filter to specified year or most recent
    if year is None:
        year = df['year'].max()
    
    chart_data = df[df['year'] == year].copy()
    
    if chart_data.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for selected year",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=COLORS['text'])
        )
        return fig
    
    # Calculate debt service as % of revenue
    from utils.calculations import calculate_debt_service_pressure
    
    chart_data['debt_service_pct_revenue'] = calculate_debt_service_pressure(
        chart_data['debt_service_usd'],
        chart_data['gdp_usd'],
        chart_data['revenue_pct_gdp']
    )
    
    # Remove rows with invalid calculations
    chart_data = chart_data.dropna(subset=['debt_service_pct_revenue'])
    
    # Sort by debt service percentage descending
    chart_data = chart_data.sort_values('debt_service_pct_revenue', ascending=True)
    
    # Limit to top N if specified
    if top_n is not None and len(chart_data) > top_n:
        chart_data = chart_data.tail(top_n)
    
    # Assign colors based on thresholds
    chart_data['color'] = chart_data['debt_service_pct_revenue'].apply(
        assign_debt_service_color
    )
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=chart_data['country_name'],
        x=chart_data['debt_service_pct_revenue'],
        orientation='h',
        marker=dict(
            color=chart_data['color'],
            line=dict(color=COLORS['border'], width=1)
        ),
        text=chart_data['debt_service_pct_revenue'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
        hovertemplate=(
            '<b>%{y}</b><br>' +
            'Debt Service: %{x:.1f}% of revenue<br>' +
            'Absolute Amount: $%{customdata:,.0f}<br>' +
            '<extra></extra>'
        ),
        customdata=chart_data['debt_service_usd']
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'Debt Service Pressure by Country ({year})',
            font=dict(size=20, color=COLORS['text'], family='Inter')
        ),
        xaxis=dict(
            title=dict(
                text='Debt Service (% of Government Revenue)',
                font=dict(size=14, color=COLORS['text'])
            ),
            tickfont=dict(size=12, color=COLORS['text']),
            gridcolor=COLORS['border'],
            showgrid=True
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=11, color=COLORS['text']),
            showgrid=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=max(400, len(chart_data) * 25),  # Dynamic height based on number of countries
        margin=dict(l=150, r=100, t=60, b=60),
        showlegend=False,
        hovermode='closest'
    )
    
    # Add threshold reference lines
    fig.add_vline(
        x=THRESHOLDS['debt_service_high'],
        line_dash="dash",
        line_color=COLORS['debt'],
        opacity=0.5,
        annotation_text="High Risk (30%)",
        annotation_position="top"
    )
    
    fig.add_vline(
        x=THRESHOLDS['debt_service_moderate'],
        line_dash="dash",
        line_color=COLORS['bilateral'],
        opacity=0.5,
        annotation_text="Moderate Risk (20%)",
        annotation_position="top"
    )
    
    return fig


def create_creditor_stacked_area(
    df: pd.DataFrame,
    country: Optional[str] = None
) -> go.Figure:
    """
    Create stacked area chart showing debt service by creditor type over time.
    
    This chart visualizes how debt service payments are distributed across
    different creditor types (multilateral, bilateral, commercial) and how
    this composition changes over time.
    
    Args:
        df: DataFrame with columns: year, debt_service_usd,
            creditor_multilateral_pct, creditor_bilateral_pct,
            creditor_commercial_pct, country_name (optional)
        country: Optional country name to filter for single country view
    
    Returns:
        Plotly Figure object with stacked area chart
        
    Requirements: 3.5, 8.1
    
    Example:
        >>> fig = create_creditor_stacked_area(df)
        >>> fig.show()
        >>> # Or for a specific country:
        >>> fig = create_creditor_stacked_area(df, country='Nigeria')
    """
    # Check if creditor columns exist
    required_cols = ['creditor_multilateral_pct', 'creditor_bilateral_pct', 'creditor_commercial_pct']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="Creditor composition data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=COLORS['text'])
        )
        return fig
    
    # Filter by country if specified
    if country is not None:
        chart_data = df[df['country_name'] == country].copy()
        title_suffix = f' - {country}'
    else:
        # Aggregate across all countries
        chart_data = df.groupby('year').agg({
            'debt_service_usd': 'sum',
            'creditor_multilateral_pct': 'mean',
            'creditor_bilateral_pct': 'mean',
            'creditor_commercial_pct': 'mean'
        }).reset_index()
        title_suffix = ' - All Countries'
    
    if chart_data.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No creditor data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=COLORS['text'])
        )
        return fig
    
    # Sort by year
    chart_data = chart_data.sort_values('year')
    
    # Calculate debt service by creditor type
    chart_data['multilateral_usd'] = (
        chart_data['debt_service_usd'] * 
        chart_data['creditor_multilateral_pct'] / 100
    )
    chart_data['bilateral_usd'] = (
        chart_data['debt_service_usd'] * 
        chart_data['creditor_bilateral_pct'] / 100
    )
    chart_data['commercial_usd'] = (
        chart_data['debt_service_usd'] * 
        chart_data['creditor_commercial_pct'] / 100
    )
    
    # Create stacked area chart
    fig = go.Figure()
    
    # Add traces in order (bottom to top)
    fig.add_trace(go.Scatter(
        x=chart_data['year'],
        y=chart_data['multilateral_usd'],
        name='Multilateral',
        mode='lines',
        line=dict(width=0.5, color=COLORS['multilateral']),
        fillcolor=COLORS['multilateral'],
        fill='tozeroy',
        stackgroup='one',
        hovertemplate=(
            '<b>Multilateral Creditors</b><br>' +
            'Year: %{x}<br>' +
            'Amount: $%{y:,.0f}<br>' +
            '<extra></extra>'
        )
    ))
    
    fig.add_trace(go.Scatter(
        x=chart_data['year'],
        y=chart_data['bilateral_usd'],
        name='Bilateral',
        mode='lines',
        line=dict(width=0.5, color=COLORS['bilateral']),
        fillcolor=COLORS['bilateral'],
        fill='tonexty',
        stackgroup='one',
        hovertemplate=(
            '<b>Bilateral Creditors</b><br>' +
            'Year: %{x}<br>' +
            'Amount: $%{y:,.0f}<br>' +
            '<extra></extra>'
        )
    ))
    
    fig.add_trace(go.Scatter(
        x=chart_data['year'],
        y=chart_data['commercial_usd'],
        name='Commercial',
        mode='lines',
        line=dict(width=0.5, color=COLORS['commercial']),
        fillcolor=COLORS['commercial'],
        fill='tonexty',
        stackgroup='one',
        hovertemplate=(
            '<b>Commercial Creditors</b><br>' +
            'Year: %{x}<br>' +
            'Amount: $%{y:,.0f}<br>' +
            '<extra></extra>'
        )
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'Debt Service by Creditor Type{title_suffix}',
            font=dict(size=20, color=COLORS['text'], family='Inter')
        ),
        xaxis=dict(
            title=dict(
                text='Year',
                font=dict(size=14, color=COLORS['text'])
            ),
            tickfont=dict(size=12, color=COLORS['text']),
            gridcolor=COLORS['border'],
            showgrid=True,
            dtick=1  # Show every year
        ),
        yaxis=dict(
            title=dict(
                text='Debt Service (USD)',
                font=dict(size=14, color=COLORS['text'])
            ),
            tickfont=dict(size=12, color=COLORS['text']),
            gridcolor=COLORS['border'],
            showgrid=True,
            tickformat='$,.0f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=80, r=40, t=60, b=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=12, color=COLORS['text'])
        ),
        hovermode='x unified'
    )
    
    return fig
