"""
Trading Strategy Module

Implements a basic Heikin Ashi-based trading strategy.
"""

import pandas as pd
from heikin_ashi import get_candle_color, has_lower_shadow, has_upper_shadow


class HeikinAshiStrategy:
    """
    Simple Heikin Ashi trading strategy.
    
    Entry Rules:
    - LONG: Current and previous candle are green (2nd and 3rd in sequence), 
            and the candle before that was not green (transition to uptrend)
    - SHORT: Current and previous candle are red (2nd and 3rd in sequence),
             and the candle before that was not red (transition to downtrend)
    
    Exit Rules:
    - LONG: First red candle or stop loss/take profit
    - SHORT: First green candle or stop loss/take profit
    """
    
    def __init__(self, stop_loss_pips=50, take_profit_pips=100):
        """
        Initialize strategy.
        
        Args:
            stop_loss_pips: Stop loss distance in pips
            take_profit_pips: Take profit distance in pips
        """
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.pip_value = 0.01  # For XAUUSD, 1 pip = 0.01
    
    def generate_signals(self, df):
        """
        Generate trading signals based on Heikin Ashi candles.
        
        Args:
            df: DataFrame with Heikin Ashi OHLC data
            
        Returns:
            DataFrame with added 'signal' column (1=buy, -1=sell, 0=hold)
        """
        df = df.copy()
        df['color'] = df.apply(get_candle_color, axis=1)
        df['signal'] = 0
        
        for i in range(2, len(df)):
            current_color = df.iloc[i]['color']
            prev_color = df.iloc[i-1]['color']
            prev_prev_color = df.iloc[i-2]['color']
            
            # Check for long entry: 2 consecutive green candles
            if (current_color == 'green' and 
                prev_color == 'green' and
                prev_prev_color != 'green'):
                
                # Additional filter: no lower shadow on current candle
                if not has_lower_shadow(df.iloc[i], threshold=0.1):
                    df.loc[df.index[i], 'signal'] = 1  # Buy signal
            
            # Check for short entry: 2 consecutive red candles
            elif (current_color == 'red' and 
                  prev_color == 'red' and
                  prev_prev_color != 'red'):
                
                # Additional filter: no upper shadow on current candle
                if not has_upper_shadow(df.iloc[i], threshold=0.1):
                    df.loc[df.index[i], 'signal'] = -1  # Sell signal
        
        return df
    
    def calculate_stop_loss(self, entry_price, position_type):
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price of the trade
            position_type: 'long' or 'short'
            
        Returns:
            Stop loss price
        """
        sl_distance = self.stop_loss_pips * self.pip_value
        
        if position_type == 'long':
            return entry_price - sl_distance
        else:  # short
            return entry_price + sl_distance
    
    def calculate_take_profit(self, entry_price, position_type):
        """
        Calculate take profit price.
        
        Args:
            entry_price: Entry price of the trade
            position_type: 'long' or 'short'
            
        Returns:
            Take profit price
        """
        tp_distance = self.take_profit_pips * self.pip_value
        
        if position_type == 'long':
            return entry_price + tp_distance
        else:  # short
            return entry_price - tp_distance
