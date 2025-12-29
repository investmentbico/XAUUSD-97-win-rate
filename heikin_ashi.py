"""
Heikin Ashi Candle Calculation Module

Converts standard OHLC (Open, High, Low, Close) candles to Heikin Ashi candles.
Heikin Ashi candles help identify trends more clearly by smoothing price data.
"""

import pandas as pd
import numpy as np


def calculate_heikin_ashi(df):
    """
    Convert standard OHLC data to Heikin Ashi candles.
    
    Args:
        df: DataFrame with columns ['open', 'high', 'low', 'close']
        
    Returns:
        DataFrame with Heikin Ashi OHLC values
    """
    ha_df = df.copy()
    
    # Initialize Heikin Ashi columns
    ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    # First candle's HA open is the average of open and close
    ha_df.loc[ha_df.index[0], 'ha_open'] = (df.loc[df.index[0], 'open'] + 
                                              df.loc[df.index[0], 'close']) / 2
    
    # Calculate HA open for subsequent candles
    for i in range(1, len(ha_df)):
        ha_df.loc[ha_df.index[i], 'ha_open'] = (
            ha_df.loc[ha_df.index[i-1], 'ha_open'] + 
            ha_df.loc[ha_df.index[i-1], 'ha_close']
        ) / 2
    
    # Calculate HA high and low
    ha_df['ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].max(axis=1)
    ha_df['ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].min(axis=1)
    
    return ha_df


def get_candle_color(row):
    """
    Determine if Heikin Ashi candle is bullish (green) or bearish (red).
    
    Args:
        row: DataFrame row with ha_open and ha_close
        
    Returns:
        'green' for bullish, 'red' for bearish
    """
    return 'green' if row['ha_close'] > row['ha_open'] else 'red'


def has_upper_shadow(row, threshold=0.1):
    """
    Check if candle has an upper shadow (wick).
    
    Args:
        row: DataFrame row with HA OHLC data
        threshold: Minimum shadow size as percentage of candle range
        
    Returns:
        Boolean indicating presence of upper shadow
    """
    body_top = max(row['ha_open'], row['ha_close'])
    shadow = row['ha_high'] - body_top
    candle_range = row['ha_high'] - row['ha_low']
    
    if candle_range == 0:
        return False
    
    return (shadow / candle_range) > threshold


def has_lower_shadow(row, threshold=0.1):
    """
    Check if candle has a lower shadow (wick).
    
    Args:
        row: DataFrame row with HA OHLC data
        threshold: Minimum shadow size as percentage of candle range
        
    Returns:
        Boolean indicating presence of lower shadow
    """
    body_bottom = min(row['ha_open'], row['ha_close'])
    shadow = body_bottom - row['ha_low']
    candle_range = row['ha_high'] - row['ha_low']
    
    if candle_range == 0:
        return False
    
    return (shadow / candle_range) > threshold
