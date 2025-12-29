"""
Backtesting Engine Module

Core backtesting engine for trading strategies on Heikin Ashi candles.
"""

import pandas as pd
import numpy as np
from datetime import datetime


class BacktestEngine:
    """
    Backtesting engine for trading strategies.
    """
    
    def __init__(self, initial_capital=10000.0, position_size=0.1):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital in USD
            position_size: Position size in lots
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.current_capital = initial_capital
        self.trades = []
        self.current_position = None
    
    def run_backtest(self, df, strategy):
        """
        Run backtest on provided data with given strategy.
        
        Args:
            df: DataFrame with Heikin Ashi OHLC data
            strategy: Strategy object with generate_signals method
            
        Returns:
            Dictionary with backtest results
        """
        # Generate signals
        df = strategy.generate_signals(df)
        
        # Reset state
        self.current_capital = self.initial_capital
        self.trades = []
        self.current_position = None
        
        # Iterate through data
        for i in range(len(df)):
            current_row = df.iloc[i]
            
            # Check for exit conditions if in position
            if self.current_position is not None:
                self._check_exit(current_row, df.index[i])
            
            # Check for entry signal if no position
            if self.current_position is None and current_row['signal'] != 0:
                self._enter_position(current_row, df.index[i], strategy)
        
        # Close any open position at end
        if self.current_position is not None:
            last_row = df.iloc[-1]
            self._exit_position(last_row, df.index[-1], 'end_of_data')
        
        # Calculate results
        results = self._calculate_results()
        
        return results
    
    def _enter_position(self, row, timestamp, strategy):
        """
        Enter a new position.
        
        Args:
            row: Current data row
            timestamp: Current timestamp
            strategy: Strategy object
        """
        signal = row['signal']
        entry_price = row['ha_close']
        
        position_type = 'long' if signal == 1 else 'short'
        
        stop_loss = strategy.calculate_stop_loss(entry_price, position_type)
        take_profit = strategy.calculate_take_profit(entry_price, position_type)
        
        self.current_position = {
            'type': position_type,
            'entry_time': timestamp,
            'entry_price': entry_price,
            'size': self.position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        }
    
    def _check_exit(self, row, timestamp):
        """
        Check if position should be exited.
        
        Args:
            row: Current data row
            timestamp: Current timestamp
        """
        if self.current_position is None:
            return
        
        exit_reason = None
        exit_price = None
        
        # Check stop loss
        if self.current_position['type'] == 'long':
            if row['ha_low'] <= self.current_position['stop_loss']:
                exit_reason = 'stop_loss'
                exit_price = self.current_position['stop_loss']
            elif row['ha_high'] >= self.current_position['take_profit']:
                exit_reason = 'take_profit'
                exit_price = self.current_position['take_profit']
            elif row['color'] == 'red':
                exit_reason = 'signal_exit'
                exit_price = row['ha_close']
        else:  # short
            if row['ha_high'] >= self.current_position['stop_loss']:
                exit_reason = 'stop_loss'
                exit_price = self.current_position['stop_loss']
            elif row['ha_low'] <= self.current_position['take_profit']:
                exit_reason = 'take_profit'
                exit_price = self.current_position['take_profit']
            elif row['color'] == 'green':
                exit_reason = 'signal_exit'
                exit_price = row['ha_close']
        
        if exit_reason:
            self._exit_position(row, timestamp, exit_reason, exit_price)
    
    def _exit_position(self, row, timestamp, reason, exit_price=None):
        """
        Exit current position.
        
        Args:
            row: Current data row
            timestamp: Current timestamp
            reason: Exit reason
            exit_price: Exit price (uses ha_close if not provided)
        """
        if self.current_position is None:
            return
        
        if exit_price is None:
            exit_price = row['ha_close']
        
        # Calculate profit/loss
        if self.current_position['type'] == 'long':
            pnl = (exit_price - self.current_position['entry_price']) * self.position_size * 100
        else:  # short
            pnl = (self.current_position['entry_price'] - exit_price) * self.position_size * 100
        
        # Update capital
        self.current_capital += pnl
        
        # Record trade
        trade = {
            'entry_time': self.current_position['entry_time'],
            'exit_time': timestamp,
            'type': self.current_position['type'],
            'entry_price': self.current_position['entry_price'],
            'exit_price': exit_price,
            'size': self.current_position['size'],
            'pnl': pnl,
            'exit_reason': reason
        }
        
        self.trades.append(trade)
        self.current_position = None
    
    def _calculate_results(self):
        """
        Calculate backtest results and statistics.
        
        Returns:
            Dictionary with results
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'final_capital': self.initial_capital,
                'return_pct': 0.0,
                'trades': []
            }
        
        trades_df = pd.DataFrame(self.trades)
        
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        total_trades = len(trades_df)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = trades_df['pnl'].sum()
        return_pct = (total_pnl / self.initial_capital * 100)
        
        results = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'final_capital': round(self.current_capital, 2),
            'return_pct': round(return_pct, 2),
            'avg_win': round(trades_df[trades_df['pnl'] > 0]['pnl'].mean(), 2) if winning_trades > 0 else 0,
            'avg_loss': round(trades_df[trades_df['pnl'] < 0]['pnl'].mean(), 2) if losing_trades > 0 else 0,
            'trades': self.trades
        }
        
        return results
