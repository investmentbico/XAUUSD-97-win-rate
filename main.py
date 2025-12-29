"""
Main execution script for XAUUSD Heikin Ashi backtesting.

This is a smoke code (basic implementation) for backtesting on Heikin Ashi candles
with 1-minute timeframe.
"""

import pandas as pd
from datetime import datetime

from data_loader import generate_sample_data, validate_ohlc_data
from heikin_ashi import calculate_heikin_ashi
from strategy import HeikinAshiStrategy
from backtest_engine import BacktestEngine
import config


def print_separator():
    """Print a separator line."""
    print("=" * 70)


def print_results(results):
    """
    Print backtest results in a formatted way.
    
    Args:
        results: Dictionary with backtest results
    """
    print_separator()
    print("BACKTEST RESULTS - XAUUSD Heikin Ashi Strategy (1m timeframe)")
    print_separator()
    print(f"Initial Capital:     ${config.INITIAL_CAPITAL:,.2f}")
    print(f"Final Capital:       ${results['final_capital']:,.2f}")
    print(f"Total P&L:           ${results['total_pnl']:,.2f}")
    print(f"Return:              {results['return_pct']:.2f}%")
    print_separator()
    print(f"Total Trades:        {results['total_trades']}")
    print(f"Winning Trades:      {results['winning_trades']}")
    print(f"Losing Trades:       {results['losing_trades']}")
    print(f"Win Rate:            {results['win_rate']:.2f}%")
    print_separator()
    
    if results['total_trades'] > 0:
        print(f"Average Win:         ${results['avg_win']:,.2f}")
        print(f"Average Loss:        ${results['avg_loss']:,.2f}")
        print_separator()
        
        print("\nLast 5 Trades:")
        print("-" * 70)
        trades = results['trades'][-5:]
        for i, trade in enumerate(trades, 1):
            pnl_sign = "+" if trade['pnl'] > 0 else ""
            print(f"{i}. {trade['type'].upper():5s} | "
                  f"Entry: ${trade['entry_price']:,.2f} | "
                  f"Exit: ${trade['exit_price']:,.2f} | "
                  f"P&L: {pnl_sign}${trade['pnl']:,.2f} | "
                  f"Reason: {trade['exit_reason']}")
        print_separator()


def main():
    """
    Main execution function.
    """
    print("\n" + "=" * 70)
    print("XAUUSD HEIKIN ASHI BACKTESTING - 1 MINUTE TIMEFRAME")
    print("=" * 70)
    print(f"Timeframe: {config.TIMEFRAME}")
    print(f"Symbol: {config.SYMBOL}")
    print(f"Position Size: {config.POSITION_SIZE} lots")
    print(f"Stop Loss: {config.STOP_LOSS_PIPS} pips")
    print(f"Take Profit: {config.TAKE_PROFIT_PIPS} pips")
    print("=" * 70)
    
    # Step 1: Load or generate data
    print("\n[1/5] Loading market data...")
    # For this smoke code, we generate sample data
    # In production, you would load real data from CSV or API
    df = generate_sample_data(num_candles=2000, start_price=2000.0)
    print(f"✓ Loaded {len(df)} candles")
    
    # Step 2: Validate data
    print("\n[2/5] Validating OHLC data...")
    if not validate_ohlc_data(df):
        print("✗ Data validation failed!")
        return
    print("✓ Data validation passed")
    
    # Step 3: Convert to Heikin Ashi
    print("\n[3/5] Converting to Heikin Ashi candles...")
    ha_df = calculate_heikin_ashi(df)
    print(f"✓ Converted {len(ha_df)} candles to Heikin Ashi format")
    
    # Step 4: Initialize strategy and backtest engine
    print("\n[4/5] Initializing strategy and backtest engine...")
    strategy = HeikinAshiStrategy(
        stop_loss_pips=config.STOP_LOSS_PIPS,
        take_profit_pips=config.TAKE_PROFIT_PIPS
    )
    engine = BacktestEngine(
        initial_capital=config.INITIAL_CAPITAL,
        position_size=config.POSITION_SIZE
    )
    print("✓ Strategy and engine initialized")
    
    # Step 5: Run backtest
    print("\n[5/5] Running backtest...")
    results = engine.run_backtest(ha_df, strategy)
    print("✓ Backtest completed\n")
    
    # Print results
    print_results(results)
    
    print("\n✓ Backtesting complete!")
    print("\nNote: This is a smoke code for demonstration purposes.")
    print("For production use, integrate with real market data and refine the strategy.\n")


if __name__ == "__main__":
    main()
