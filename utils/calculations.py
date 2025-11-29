"""
Calculation utilities for the Africa Sovereign Debt Crisis Dashboard.

This module provides functions for calculating debt metrics, opportunity costs,
and debt restructuring scenarios.
"""

import pandas as pd
import numpy as np
from typing import Union, Dict
from utils.constants import UNIT_COSTS


def calculate_debt_service_pressure(
    debt_service_usd: Union[float, pd.Series],
    gdp_usd: Union[float, pd.Series],
    revenue_pct_gdp: Union[float, pd.Series]
) -> Union[float, pd.Series]:
    """
    Calculate debt service as percentage of government revenue.
    
    This metric shows how much of a government's revenue is consumed by
    debt service payments. Higher percentages indicate greater fiscal pressure.
    
    Args:
        debt_service_usd: Annual debt service payments in USD
        gdp_usd: GDP in current USD
        revenue_pct_gdp: Government revenue as percentage of GDP
    
    Returns:
        Debt service as percentage of government revenue
        
    Formula:
        (debt_service_usd / (gdp_usd * revenue_pct_gdp / 100)) * 100
        
    Example:
        >>> calculate_debt_service_pressure(1_000_000_000, 50_000_000_000, 20)
        >>> 10.0  # Debt service is 10% of government revenue
    """
    # Handle division by zero
    revenue_usd = gdp_usd * revenue_pct_gdp / 100
    
    # Use numpy for element-wise operations that work with both scalars and Series
    with np.errstate(divide='ignore', invalid='ignore'):
        result = (debt_service_usd / revenue_usd) * 100
    
    # Replace inf and nan with None for cleaner handling
    if isinstance(result, pd.Series):
        result = result.replace([np.inf, -np.inf], np.nan)
    elif np.isinf(result) or np.isnan(result):
        result = np.nan
    
    return result


def calculate_opportunity_cost(
    debt_service_usd: float,
    unit_type: str
) -> int:
    """
    Convert debt payment to tangible social spending units.
    
    This function calculates how many schools, hospitals, vaccines, or teachers
    could be funded with the money spent on debt service, helping communicate
    the human cost of debt obligations.
    
    Args:
        debt_service_usd: Annual debt service in USD
        unit_type: One of 'school', 'hospital', 'vaccine_dose', 'teacher'
    
    Returns:
        Number of units that could be funded (integer division)
        
    Raises:
        ValueError: If unit_type is not recognized
        
    Example:
        >>> calculate_opportunity_cost(10_000_000, 'school')
        >>> 11  # Could build 11 schools
    """
    if unit_type not in UNIT_COSTS:
        raise ValueError(
            f"Invalid unit_type '{unit_type}'. "
            f"Must be one of: {', '.join(UNIT_COSTS.keys())}"
        )
    
    unit_cost = UNIT_COSTS[unit_type]
    
    # Return integer division
    return int(debt_service_usd / unit_cost)


def calculate_annuity_payment(
    principal: float,
    rate: float,
    periods: int
) -> float:
    """
    Calculate annual payment using standard annuity formula.
    
    This function computes the fixed annual payment required to pay off
    a loan over a specified number of periods at a given interest rate.
    
    Args:
        principal: Principal amount (total debt)
        rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
        periods: Number of payment periods (years)
    
    Returns:
        Annual payment amount
        
    Formula:
        P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        
    Edge Cases:
        - If rate = 0: payment = principal / periods
        - If periods = 0: return principal
        
    Example:
        >>> calculate_annuity_payment(100_000, 0.05, 10)
        >>> 12950.46  # Approximately
    """
    # Handle edge case: zero periods
    if periods == 0:
        return principal
    
    # Handle edge case: zero interest rate
    if rate == 0:
        return principal / periods
    
    # Standard annuity formula
    numerator = rate * (1 + rate) ** periods
    denominator = (1 + rate) ** periods - 1
    
    return principal * (numerator / denominator)


def calculate_restructuring_impact(
    current_debt: float,
    current_rate: float,
    current_maturity: int,
    new_rate: float,
    maturity_extension: int,
    haircut_pct: float,
    gdp_usd: float = None
) -> Dict[str, float]:
    """
    Calculate impact of debt restructuring scenario.
    
    This function models the effects of debt restructuring by applying
    a combination of principal haircut, maturity extension, and interest
    rate reduction.
    
    Args:
        current_debt: Current total debt amount
        current_rate: Current interest rate (as decimal, e.g., 0.05 for 5%)
        current_maturity: Current remaining maturity (years)
        new_rate: New interest rate after reduction (as decimal)
        maturity_extension: Additional years added to maturity
        haircut_pct: Principal reduction percentage (0-100)
        gdp_usd: Optional GDP for debt-to-GDP calculation
    
    Returns:
        Dictionary containing:
            - new_annual_payment: Annual payment under new terms
            - fiscal_space_freed: Annual savings from restructuring
            - new_debt_to_gdp: New debt-to-GDP ratio (if GDP provided)
            - current_annual_payment: Current annual payment for comparison
            
    Example:
        >>> calculate_restructuring_impact(
        ...     current_debt=1_000_000_000,
        ...     current_rate=0.06,
        ...     current_maturity=10,
        ...     new_rate=0.03,
        ...     maturity_extension=5,
        ...     haircut_pct=20,
        ...     gdp_usd=10_000_000_000
        ... )
    """
    # Calculate current annual payment
    current_annual_payment = calculate_annuity_payment(
        current_debt,
        current_rate,
        current_maturity
    )
    
    # Apply haircut to principal
    new_principal = current_debt * (1 - haircut_pct / 100)
    
    # Calculate new maturity
    new_maturity = current_maturity + maturity_extension
    
    # Calculate new annual payment
    new_annual_payment = calculate_annuity_payment(
        new_principal,
        new_rate,
        new_maturity
    )
    
    # Calculate fiscal space freed
    fiscal_space_freed = current_annual_payment - new_annual_payment
    
    # Build result dictionary
    result = {
        'new_annual_payment': new_annual_payment,
        'fiscal_space_freed': fiscal_space_freed,
        'current_annual_payment': current_annual_payment
    }
    
    # Add debt-to-GDP if GDP provided
    if gdp_usd is not None and gdp_usd > 0:
        result['new_debt_to_gdp'] = (new_principal / gdp_usd) * 100
    
    return result


def calculate_kpi_metrics(df: pd.DataFrame) -> Dict[str, Union[float, int, str]]:
    """
    Calculate KPI metrics for the overview section.
    
    This function computes the four main KPI metrics displayed in the
    overview section: median debt-to-GDP, debt service as % of revenue,
    health vs debt service ratio, and education vs debt service ratio.
    
    Args:
        df: DataFrame with debt and social spending data
            Required columns: debt_to_gdp, debt_service_usd, gdp_usd,
            revenue_pct_gdp, health_pct_gdp, education_pct_gdp
    
    Returns:
        Dictionary containing:
            - median_debt_to_gdp: Median debt-to-GDP ratio across countries
            - debt_service_pct_revenue: Median debt service as % of revenue
            - health_vs_debt: Ratio of health spending to debt service
            - education_vs_debt: Ratio of education spending to debt service
            - debt_to_gdp_trend: Year-over-year change in median debt-to-GDP
            - debt_service_trend: Year-over-year change in debt service ratio
            
    Example:
        >>> kpis = calculate_kpi_metrics(df)
        >>> print(f"Median debt-to-GDP: {kpis['median_debt_to_gdp']:.1f}%")
    """
    # Get most recent year data
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year].copy()
    
    # Calculate median debt-to-GDP
    median_debt_to_gdp = latest_data['debt_to_gdp'].median()
    
    # Calculate debt service as % of revenue
    latest_data['debt_service_pct_revenue'] = calculate_debt_service_pressure(
        latest_data['debt_service_usd'],
        latest_data['gdp_usd'],
        latest_data['revenue_pct_gdp']
    )
    debt_service_pct_revenue = latest_data['debt_service_pct_revenue'].median()
    
    # Calculate health vs debt service ratio
    # Health spending in USD = GDP * health_pct_gdp / 100
    latest_data['health_usd'] = latest_data['gdp_usd'] * latest_data['health_pct_gdp'] / 100
    health_vs_debt = (latest_data['health_usd'] / latest_data['debt_service_usd']).median()
    
    # Calculate education vs debt service ratio
    latest_data['education_usd'] = latest_data['gdp_usd'] * latest_data['education_pct_gdp'] / 100
    education_vs_debt = (latest_data['education_usd'] / latest_data['debt_service_usd']).median()
    
    # Calculate trends (year-over-year change)
    debt_to_gdp_trend = 0.0
    debt_service_trend = 0.0
    
    if latest_year > df['year'].min():
        previous_year = latest_year - 1
        previous_data = df[df['year'] == previous_year].copy()
        
        if not previous_data.empty:
            prev_median_debt = previous_data['debt_to_gdp'].median()
            debt_to_gdp_trend = median_debt_to_gdp - prev_median_debt
            
            previous_data['debt_service_pct_revenue'] = calculate_debt_service_pressure(
                previous_data['debt_service_usd'],
                previous_data['gdp_usd'],
                previous_data['revenue_pct_gdp']
            )
            prev_debt_service = previous_data['debt_service_pct_revenue'].median()
            debt_service_trend = debt_service_pct_revenue - prev_debt_service
    
    return {
        'median_debt_to_gdp': median_debt_to_gdp,
        'debt_service_pct_revenue': debt_service_pct_revenue,
        'health_vs_debt': health_vs_debt,
        'education_vs_debt': education_vs_debt,
        'debt_to_gdp_trend': debt_to_gdp_trend,
        'debt_service_trend': debt_service_trend
    }


def generate_insight(df: pd.DataFrame) -> str:
    """
    Generate a compelling insight from the debt data.
    
    This function analyzes the data to find the most significant debt crisis
    statistic and returns a formatted string highlighting it.
    
    Args:
        df: DataFrame with debt and social spending data
    
    Returns:
        Formatted string with insight and country reference
        
    Example:
        >>> insight = generate_insight(df)
        >>> print(insight)
        "23 countries spend more on debt service than health care"
    """
    # Get most recent year data
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year].copy()
    
    # Calculate health and education spending in USD
    latest_data['health_usd'] = latest_data['gdp_usd'] * latest_data['health_pct_gdp'] / 100
    latest_data['education_usd'] = latest_data['gdp_usd'] * latest_data['education_pct_gdp'] / 100
    
    # Count countries where debt service > health spending
    debt_exceeds_health = (latest_data['debt_service_usd'] > latest_data['health_usd']).sum()
    
    # Count countries where debt service > education spending
    debt_exceeds_education = (latest_data['debt_service_usd'] > latest_data['education_usd']).sum()
    
    # Count countries in high risk category (debt-to-GDP > 60%)
    high_risk_countries = (latest_data['debt_to_gdp'] > 60).sum()
    
    # Find country with highest debt-to-GDP
    if not latest_data.empty:
        highest_debt_country = latest_data.loc[latest_data['debt_to_gdp'].idxmax()]
        highest_debt_name = highest_debt_country.get('country_name', 'Unknown')
        highest_debt_ratio = highest_debt_country['debt_to_gdp']
    else:
        highest_debt_name = 'Unknown'
        highest_debt_ratio = 0
    
    # Generate insight based on most compelling statistic
    insights = []
    
    if debt_exceeds_health > 0:
        insights.append(
            f"{debt_exceeds_health} countries spend more on debt service than health care"
        )
    
    if high_risk_countries > 0:
        insights.append(
            f"{high_risk_countries} countries have debt-to-GDP ratios exceeding 60% (high risk)"
        )
    
    if highest_debt_ratio > 0:
        insights.append(
            f"{highest_debt_name} has the highest debt-to-GDP ratio at {highest_debt_ratio:.1f}%"
        )
    
    # Return the first insight, or a default message
    if insights:
        return insights[0]
    else:
        return "Analyzing debt crisis patterns across African economies"
