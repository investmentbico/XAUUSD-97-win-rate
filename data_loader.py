"""
Data Loader Module

Handles loading and processing of market data for backtesting.
Includes sample data generation for testing purposes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_data(num_candles=1000, start_price=2000.0):
    """
    Generate sample OHLC data for testing.
    Simulates XAUUSD (Gold) price movements.
    
    Args:
        num_candles: Number of 1-minute candles to generate
        start_price: Starting price for gold
        
    Returns:
        DataFrame with OHLC data
    """
    np.random.seed(42)  # For reproducibility
    
    # Generate timestamps (1-minute intervals)
    start_time = datetime.now() - timedelta(minutes=num_candles)
    timestamps = [start_time + timedelta(minutes=i) for i in range(num_candles)]
    
    data = []
    current_price = start_price
    
    for i in range(num_candles):
        # Simulate price movement with some trend and noise
        trend = np.sin(i / 100) * 2  # Sinusoidal trend
        noise = np.random.randn() * 1.5  # Random noise
        
        # Calculate OHLC
        open_price = current_price
        close_price = open_price + trend + noise
        
        high_price = max(open_price, close_price) + abs(np.random.randn() * 0.5)
        low_price = min(open_price, close_price) - abs(np.random.randn() * 0.5)
        
        # Volume (random)
        volume = np.random.randint(100, 1000)
        
        data.append({
            'timestamp': timestamps[i],
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume
        })
        
        current_price = close_price
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return df


def load_csv_data(filepath):
    """
    Load OHLC data from CSV file.
    
    Expected CSV format:
    timestamp,open,high,low,close,volume
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        DataFrame with OHLC data
    """
    df = pd.read_csv(filepath)
    
    # Convert timestamp to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
    
    # Ensure required columns exist
    required_cols = ['open', 'high', 'low', 'close']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    return df


def validate_ohlc_data(df):
    """
    Validate OHLC data integrity.
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        Boolean indicating if data is valid
    """
    # Check for required columns
    required_cols = ['open', 'high', 'low', 'close']
    if not all(col in df.columns for col in required_cols):
        return False
    
    # Check that high >= low
    if not (df['high'] >= df['low']).all():
        return False
    
    # Check that high >= open and high >= close
    if not ((df['high'] >= df['open']) & (df['high'] >= df['close'])).all():
        return False
    
    # Check that low <= open and low <= close
    if not ((df['low'] <= df['open']) & (df['low'] <= df['close'])).all():
        return False
    
    return True
