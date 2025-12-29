"""
Simple tests for the Heikin Ashi backtesting system.
"""

import pandas as pd
import numpy as np
from heikin_ashi import calculate_heikin_ashi, get_candle_color, has_upper_shadow, has_lower_shadow
from data_loader import generate_sample_data, validate_ohlc_data
from strategy import HeikinAshiStrategy
from backtest_engine import BacktestEngine


def test_heikin_ashi_calculation():
    """Test Heikin Ashi candle calculation."""
    print("Testing Heikin Ashi calculation...")
    
    # Create simple test data
    data = {
        'open': [100, 102, 101, 103],
        'high': [105, 106, 104, 107],
        'low': [99, 101, 100, 102],
        'close': [103, 104, 102, 105]
    }
    df = pd.DataFrame(data)
    
    # Calculate Heikin Ashi
    ha_df = calculate_heikin_ashi(df)
    
    # Verify columns exist
    assert 'ha_open' in ha_df.columns
    assert 'ha_high' in ha_df.columns
    assert 'ha_low' in ha_df.columns
    assert 'ha_close' in ha_df.columns
    
    # Verify HA high >= HA low
    assert (ha_df['ha_high'] >= ha_df['ha_low']).all()
    
    print("✓ Heikin Ashi calculation test passed")


def test_candle_color():
    """Test candle color detection."""
    print("Testing candle color detection...")
    
    # Green candle
    row_green = pd.Series({'ha_open': 100, 'ha_close': 105})
    assert get_candle_color(row_green) == 'green'
    
    # Red candle
    row_red = pd.Series({'ha_open': 105, 'ha_close': 100})
    assert get_candle_color(row_red) == 'red'
    
    print("✓ Candle color test passed")


def test_data_generation():
    """Test sample data generation."""
    print("Testing sample data generation...")
    
    df = generate_sample_data(num_candles=100, start_price=2000.0)
    
    # Check data structure
    assert len(df) == 100
    assert 'open' in df.columns
    assert 'high' in df.columns
    assert 'low' in df.columns
    assert 'close' in df.columns
    
    # Validate data
    assert validate_ohlc_data(df)
    
    print("✓ Data generation test passed")


def test_strategy_signals():
    """Test strategy signal generation."""
    print("Testing strategy signal generation...")
    
    # Generate sample data
    df = generate_sample_data(num_candles=200, start_price=2000.0)
    
    # Convert to Heikin Ashi
    ha_df = calculate_heikin_ashi(df)
    
    # Generate signals
    strategy = HeikinAshiStrategy(stop_loss_pips=50, take_profit_pips=100)
    ha_df = strategy.generate_signals(ha_df)
    
    # Check signal column exists
    assert 'signal' in ha_df.columns
    
    # Check signals are valid (-1, 0, or 1)
    assert ha_df['signal'].isin([-1, 0, 1]).all()
    
    print("✓ Strategy signal generation test passed")


def test_backtest_engine():
    """Test backtesting engine."""
    print("Testing backtest engine...")
    
    # Generate sample data
    df = generate_sample_data(num_candles=500, start_price=2000.0)
    
    # Convert to Heikin Ashi
    ha_df = calculate_heikin_ashi(df)
    
    # Run backtest
    strategy = HeikinAshiStrategy(stop_loss_pips=50, take_profit_pips=100)
    engine = BacktestEngine(initial_capital=10000.0, position_size=0.1)
    results = engine.run_backtest(ha_df, strategy)
    
    # Check results structure
    assert 'total_trades' in results
    assert 'winning_trades' in results
    assert 'losing_trades' in results
    assert 'win_rate' in results
    assert 'total_pnl' in results
    assert 'final_capital' in results
    
    # Check calculations
    assert results['total_trades'] == results['winning_trades'] + results['losing_trades']
    assert results['final_capital'] == 10000.0 + results['total_pnl']
    
    print("✓ Backtest engine test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("RUNNING TESTS FOR HEIKIN ASHI BACKTESTING SYSTEM")
    print("=" * 70)
    print()
    
    try:
        test_heikin_ashi_calculation()
        test_candle_color()
        test_data_generation()
        test_strategy_signals()
        test_backtest_engine()
        
        print()
        print("=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
