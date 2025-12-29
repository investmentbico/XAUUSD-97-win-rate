# XAUUSD Heikin Ashi Backtesting System

A backtesting framework for XAUUSD (Gold/USD) trading using Heikin Ashi candles on a 1-minute timeframe.

## Overview

This is a smoke code (basic implementation) that demonstrates backtesting a trading strategy using Heikin Ashi candles. Heikin Ashi candles help identify trends more clearly by smoothing price data.

## Features

- **Heikin Ashi Candle Calculation**: Converts standard OHLC data to Heikin Ashi format
- **Trading Strategy**: Simple trend-following strategy based on Heikin Ashi patterns
- **Backtesting Engine**: Full backtesting framework with position tracking and P&L calculation
- **Sample Data Generation**: Built-in sample data generator for testing
- **Performance Metrics**: Win rate, total P&L, return percentage, and trade statistics

## Installation

1. Clone the repository:
```bash
git clone https://github.com/investmentbico/XAUUSD-97-win-rate.git
cd XAUUSD-97-win-rate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the backtest with sample data:

```bash
python main.py
```

This will:
1. Generate sample XAUUSD 1-minute OHLC data
2. Convert it to Heikin Ashi candles
3. Apply the trading strategy
4. Run the backtest
5. Display results including win rate, P&L, and trade statistics

## Configuration

Edit `config.py` to customize:

- `INITIAL_CAPITAL`: Starting capital (default: $10,000)
- `POSITION_SIZE`: Position size in lots (default: 0.1)
- `STOP_LOSS_PIPS`: Stop loss distance (default: 50 pips)
- `TAKE_PROFIT_PIPS`: Take profit distance (default: 100 pips)
- `TIMEFRAME`: Candle timeframe (default: "1m")

## Strategy

The default Heikin Ashi strategy:

**Entry Rules:**
- LONG: Two consecutive green Heikin Ashi candles with no lower shadows
- SHORT: Two consecutive red Heikin Ashi candles with no upper shadows

**Exit Rules:**
- LONG: Exit on first red candle or when stop loss/take profit is hit
- SHORT: Exit on first green candle or when stop loss/take profit is hit

## Project Structure

```
.
├── main.py              # Main execution script
├── config.py            # Configuration settings
├── heikin_ashi.py       # Heikin Ashi candle calculations
├── data_loader.py       # Data loading and generation
├── strategy.py          # Trading strategy implementation
├── backtest_engine.py   # Backtesting engine
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Using Real Data

To backtest with real market data:

1. Prepare a CSV file with the following format:
```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,2000.50,2001.20,1999.80,2000.90,500
2024-01-01 00:01:00,2000.90,2002.00,2000.50,2001.50,650
...
```

2. Modify `main.py` to load from CSV:
```python
from data_loader import load_csv_data

# Replace generate_sample_data with:
df = load_csv_data('your_data.csv')
```

## Customizing the Strategy

To create your own strategy:

1. Create a new strategy class in `strategy.py` or a new file
2. Implement the `generate_signals(df)` method
3. Implement `calculate_stop_loss()` and `calculate_take_profit()` methods
4. Update `main.py` to use your strategy

## Disclaimer

This is a smoke code for educational and demonstration purposes only. It is not financial advice. Always perform thorough testing and validation before using any trading strategy with real money.

## License

MIT License - See LICENSE file for details
