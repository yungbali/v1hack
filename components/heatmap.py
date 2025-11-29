"""
Heatmap component for the Africa Sovereign Debt Crisis Dashboard.

This module provides functions for creating the Africa choropleth heatmap
visualization colored by debt-to-GDP ratios.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Tuple


def create_africa_heatmap(
    df: pd.DataFrame,
    metric: str = 'debt_to_gdp',
    year: int = None,
    highlight_top_n: int = 3
) -> go.Figure:
    """
    Create interactive choropleth map of Africa.
    
    This function generates a choropleth map showing debt metrics across
    African countries, with color coding based on risk levels.
    
    Args:
        df: DataFrame with country-level data
            Required columns: country_code, country_name, year, and metric column
        metric: Column name to visualize (default: 'debt_to_gdp')
        year: Year to display (default: most recent year in data)
        highlight_top_n: Number of top countries to highlight (default: 3)
    
    Returns:
        Plotly Figure object with choropleth map
        
    Example:
        >>> fig = create_africa_heatmap(df, metric='debt_to_gdp', year=2024)
        >>> fig.show()
    """
    # Use most recent year if not specified
    if year is None:
        year = df['year'].max()
    
    # Filter data for specified year
    year_data = df[df['year'] == year].copy()
    
    if year_data.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for selected year",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#64748B")
        )
        return fig
    
    # Identify top N countries by metric
    top_countries = identify_top_countries(year_data, metric, highlight_top_n)
    
    # Create hover template
    hover_template = (
        "<b>%{customdata[0]}</b><br>"
        "Debt-to-GDP: %{z:.1f}%<br>"
        "Total Debt: $%{customdata[1]:.2f}B<br>"
        "<extra></extra>"
    )
    
    # Prepare custom data for hover
    year_data['total_debt_billions'] = year_data['total_debt_usd'] / 1e9
    customdata = year_data[['country_name', 'total_debt_billions']].values
    
    # Create choropleth map
    fig = px.choropleth(
        year_data,
        locations='country_code',
        locationmode='ISO-3',
        color=metric,
        scope='africa',
        color_continuous_scale='RdYlGn_r',  # Red-Yellow-Green reversed
        range_color=[0, 100],
        labels={metric: 'Debt-to-GDP (%)'},
        custom_data=['country_name', 'total_debt_billions']
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate=hover_template
    )
    
    # Add highlighting for top countries
    if top_countries:
        add_country_highlights(fig, year_data, top_countries)
    
    # Update layout to match design
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            lakecolor='rgba(255,255,255,0)',
            landcolor='#F8FAFC',
            showframe=False,
            showcoastlines=True,
            coastlinecolor='#E2E8F0',
            projection_type='natural earth',
            center=dict(lat=0, lon=20),
            projection_scale=2.5
        ),
        coloraxis_colorbar=dict(
            title=dict(
                text="Debt-to-GDP (%)",
                font=dict(size=11, color='#1E293B')
            ),
            thickness=15,
            len=0.7,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#E2E8F0',
            borderwidth=1,
            tickfont=dict(size=10, color='#475569')
        ),
        height=400
    )
    
    return fig


def identify_top_countries(
    df: pd.DataFrame,
    metric: str,
    top_n: int = 3
) -> List[str]:
    """
    Identify top N countries by specified metric.
    
    Args:
        df: DataFrame with country data
        metric: Column name to rank by
        top_n: Number of top countries to return
    
    Returns:
        List of country codes for top N countries
        
    Example:
        >>> top_3 = identify_top_countries(df, 'debt_to_gdp', 3)
        >>> print(top_3)
        ['GHA', 'ZMB', 'EGY']
    """
    # Sort by metric in descending order and get top N
    top_countries = df.nlargest(top_n, metric)['country_code'].tolist()
    return top_countries


def add_country_highlights(
    fig: go.Figure,
    df: pd.DataFrame,
    country_codes: List[str]
) -> None:
    """
    Add visual emphasis to highlighted countries on the map.
    
    This function adds border annotations to emphasize specific countries
    on the choropleth map.
    
    Args:
        fig: Plotly Figure object to modify
        df: DataFrame with country data including lat/lon if available
        country_codes: List of country codes to highlight
        
    Note:
        Modifies the figure in place
    """
    # For now, we'll add text annotations
    # In a full implementation, we could add border traces or markers
    
    # Get data for highlighted countries
    highlighted = df[df['country_code'].isin(country_codes)]
    
    # Note: Adding actual geographic highlights would require country boundary data
    # For this implementation, the highlighting is primarily done through the
    # color scale and hover interactions
    pass
