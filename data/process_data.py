"""
Data processing utilities for cleaning and transforming dashboard data
"""

import pandas as pd
import numpy as np
from typing import List


def forward_fill_with_limit(
    data: pd.DataFrame,
    max_gap: int = 2,
    value_columns: List[str] = None
) -> pd.DataFrame:
    """
    Forward-fill missing values for gaps of max_gap years or less.
    Larger gaps remain as null values.
    
    Args:
        data: DataFrame with country_code, year, and value columns
        max_gap: Maximum gap size (in years) to fill
        value_columns: List of columns to apply forward-fill to.
                      If None, applies to all numeric columns except year.
    
    Returns:
        DataFrame with forward-filled values
    """
    # Make a copy to avoid modifying original
    df = data.copy()
    
    # Determine which columns to fill
    if value_columns is None:
        # Fill all numeric columns except year and country identifiers
        exclude_cols = ['year', 'country_code', 'country_name']
        value_columns = [
            col for col in df.columns 
            if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])
        ]
    
    # Process each country separately
    if 'country_code' in df.columns:
        filled_dfs = []
        
        for country_code in df['country_code'].unique():
            country_df = df[df['country_code'] == country_code].copy()
            
            # Sort by year to ensure proper forward-fill
            country_df = country_df.sort_values('year')
            
            # Apply forward-fill with limit to each value column
            for col in value_columns:
                if col in country_df.columns:
                    # Forward fill with limit
                    country_df[col] = country_df[col].ffill(limit=max_gap)
            
            filled_dfs.append(country_df)
        
        # Combine all countries
        result = pd.concat(filled_dfs, ignore_index=True)
    else:
        # No country grouping - just apply forward-fill
        result = df.copy()
        for col in value_columns:
            if col in result.columns:
                result[col] = result[col].ffill(limit=max_gap)
    
    return result


def find_null_gaps(data: pd.DataFrame, column: str) -> List[int]:
    """
    Find the size of null value gaps in a time series.
    
    Args:
        data: DataFrame sorted by year
        column: Column name to check for gaps
    
    Returns:
        List of gap sizes (in number of consecutive null values)
    """
    if column not in data.columns:
        return []
    
    gaps = []
    current_gap = 0
    
    for value in data[column]:
        if pd.isna(value):
            current_gap += 1
        else:
            if current_gap > 0:
                gaps.append(current_gap)
                current_gap = 0
    
    # Add final gap if series ends with nulls
    if current_gap > 0:
        gaps.append(current_gap)
    
    return gaps


def clean_data(data: pd.DataFrame, apply_forward_fill: bool = True) -> pd.DataFrame:
    """
    Apply all data cleaning operations.
    
    Args:
        data: Raw merged dataset
        apply_forward_fill: Whether to apply forward-fill for missing values
    
    Returns:
        Cleaned DataFrame
    """
    df = data.copy()
    
    # Apply forward-fill if requested
    if apply_forward_fill:
        df = forward_fill_with_limit(df, max_gap=2)
    
    # Additional cleaning operations can be added here
    # For example:
    # - Remove outliers
    # - Validate ranges
    # - Handle negative values
    
    return df
