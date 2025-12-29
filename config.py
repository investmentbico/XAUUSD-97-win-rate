"""
Configuration settings for XAUUSD Heikin Ashi backtesting
"""

# Trading pair
SYMBOL = "XAUUSD"

# Timeframe
TIMEFRAME = "1m"  # 1 minute Heikin Ashi candles

# Backtesting parameters
INITIAL_CAPITAL = 10000.0  # Starting capital in USD
POSITION_SIZE = 0.1  # Position size in lots (0.1 = 0.1 oz of gold)
STOP_LOSS_PIPS = 50  # Stop loss in pips
TAKE_PROFIT_PIPS = 100  # Take profit in pips

# Heikin Ashi strategy parameters
USE_HEIKIN_ASHI = True  # Use Heikin Ashi candles for backtesting

# Risk management
MAX_RISK_PER_TRADE = 0.02  # Maximum 2% risk per trade
