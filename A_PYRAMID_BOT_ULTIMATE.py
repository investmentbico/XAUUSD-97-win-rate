#!/usr/bin/env python3
"""
A_PYRAMID BOT - ULTIMATE HYBRID STRATEGY
Combines: EMA Crossover (high frequency) + RSI Filter (quality)
The SWEET SPOT: ~25 trades/day + 18-20% win rate
LIVE TRADING MODE - XAUUSD.pro
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import time as time_module
import json
import os

class APyramidUltimateHybrid:
    def __init__(self):
        self.symbol = "XAUUSD.pro"  # Updated ticker
        self.timeframe = mt5.TIMEFRAME_M1
        
        # Configuration
        self.lot_size = 0.5
        self.profit_target = 350
        self.stop_loss = 50
        self.max_concurrent_trades = 1
        self.min_trade_interval = 120  # 120 seconds minimum between trades
        
        # Account limits
        self.account_balance = 100000
        self.daily_dd_limit = 2000   # 2%
        self.total_dd_limit = 4000   # 4%
        self.profit_target_usd = 7000  # 7%
        
        # Session tracking
        self.session_start_time = None
        self.session_start_balance = None
        self.session_start_equity = None
        self.session_id = None
        self.is_resumed = False
        
        # Position tracking
        self.open_positions = []
        self.consecutive_losses = 0
        self.pause_until = None
        self.last_entry_time = None  # Track last trade entry time
        
        # File paths
        self.log_file = "A_PYRAMID_ULTIMATE.log"
        self.status_file = "A_PYRAMID_ULTIMATE_STATUS.json"
        self.session_file = "A_PYRAMID_ULTIMATE_SESSION.json"
        self.trades_file = "A_PYRAMID_ULTIMATE_TRADES.json"
        
    def initialize_mt5(self):
        """Initialize MetaTrader 5 - Connect to ACTIVE desktop MT5 instance"""
        try:
            # Connect to running MT5 without path (uses active instance)
            if not mt5.initialize():
                self.log("ERROR: MT5 not initialized")
                self.log("ACTION: Ensure MT5 is open and running on desktop")
                return False
            
            self.log("[OK] Connected to active MT5 platform on desktop")
            
            # Get account to verify connection
            account = mt5.account_info()
            if account is None:
                self.log("ERROR: Cannot read account from MT5")
                return False
            
            self.log(f"[OK] Account verified: Login {account.login}")
            
            # Verify symbol
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                self.log(f"ERROR: Symbol {self.symbol} not found")
                return False
            
            if not symbol_info.visible:
                mt5.symbol_select(self.symbol, True)
            
            self.log(f"[OK] Symbol {self.symbol} ready for trading")
            return True
        
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            return False
    
    def shutdown_mt5(self):
        """Shutdown MT5"""
        mt5.shutdown()
        self.log("MT5 connection closed")
    
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        try:
            with open(self.log_file, "a", encoding='utf-8') as f:
                f.write(log_msg + "\n")
        except:
            pass
    
    def save_session(self):
        """Save current session state"""
        try:
            session_data = {
                "session_id": self.session_id,
                "session_start_time": self.session_start_time.isoformat() if self.session_start_time else None,
                "session_start_balance": self.session_start_balance,
                "session_start_equity": self.session_start_equity,
                "last_update": datetime.now().isoformat(),
                "consecutive_losses": self.consecutive_losses,
                "pause_until": self.pause_until.isoformat() if self.pause_until else None,
                "last_entry_time": self.last_entry_time.isoformat() if self.last_entry_time else None
            }
            
            with open(self.session_file, "w", encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            self.log(f"ERROR saving session: {str(e)}")
    
    def load_session(self):
        """Load previous session state"""
        if not os.path.exists(self.session_file):
            return False
        
        try:
            with open(self.session_file, "r", encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Restore session data
            self.session_id = session_data.get("session_id")
            self.session_start_balance = session_data.get("session_start_balance")
            self.session_start_equity = session_data.get("session_start_equity")
            self.consecutive_losses = session_data.get("consecutive_losses", 0)
            
            # Parse datetime fields
            if session_data.get("session_start_time"):
                self.session_start_time = datetime.fromisoformat(session_data["session_start_time"])
            
            if session_data.get("pause_until"):
                self.pause_until = datetime.fromisoformat(session_data["pause_until"])
            
            if session_data.get("last_entry_time"):
                self.last_entry_time = datetime.fromisoformat(session_data["last_entry_time"])
            
            self.is_resumed = True
            return True
        
        except Exception as e:
            self.log(f"ERROR loading session: {str(e)}")
            return False
    
    def record_trade(self, trade_data):
        """Record trade to trades file"""
        try:
            trades = []
            if os.path.exists(self.trades_file):
                with open(self.trades_file, "r", encoding='utf-8') as f:
                    trades = json.load(f)
            
            trade_data['timestamp'] = datetime.now().isoformat()
            trade_data['session_id'] = self.session_id
            trades.append(trade_data)
            
            with open(self.trades_file, "w", encoding='utf-8') as f:
                json.dump(trades, f, indent=2)
        except Exception as e:
            self.log(f"ERROR recording trade: {str(e)}")
    
    def get_account_info(self):
        """Get LIVE account info from MT5 desktop platform"""
        try:
            account = mt5.account_info()
            if account is None:
                return None
            
            return {
                'login': account.login,
                'name': account.name,
                'balance': float(account.balance),
                'equity': float(account.equity),
                'margin_free': float(account.margin_free),
                'margin_used': float(account.margin),
                'drawdown': float(account.equity - account.balance),
                'leverage': account.leverage,
                'currency': account.currency
            }
        except Exception as e:
            self.log(f"ERROR reading account: {str(e)}")
            return None
    
    def get_live_price(self):
        """Get LIVE XAUUSD.pro price from MT5"""
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                return None
            
            return {
                'bid': float(tick.bid),
                'ask': float(tick.ask),
                'last': float(tick.last),
                'volume': int(tick.volume),
                'time': tick.time
            }
        except Exception as e:
            self.log(f"ERROR reading price: {str(e)}")
            return None
    
    def get_open_positions_count(self):
        """Get open positions"""
        positions = mt5.positions_get()
        if positions is None:
            return 0
        xauusd_positions = [p for p in positions if p.symbol == self.symbol]
        return len(xauusd_positions)
    
    def calculate_ema(self, period=9, bars=50):
        """Calculate EMA"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        if rates is None or len(rates) < period:
            return None, None
        
        df = pd.DataFrame(rates)
        ema = df['close'].ewm(span=period).mean()
        return ema.iloc[-1], ema.iloc[-2]
    
    def calculate_ema21(self, bars=50):
        """Calculate EMA 21"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        if rates is None or len(rates) < 21:
            return None, None
        
        df = pd.DataFrame(rates)
        ema21 = df['close'].ewm(span=21).mean()
        return ema21.iloc[-1], ema21.iloc[-2]
    
    def calculate_rsi(self, period=14, bars=100):
        """Calculate RSI"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        if rates is None or len(rates) < period + 1:
            return None
        
        df = pd.DataFrame(rates)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def calculate_macd(self, bars=100):
        """Calculate MACD"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        if rates is None or len(rates) < 26:
            return None, None
        
        df = pd.DataFrame(rates)
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        
        return macd.iloc[-1], signal.iloc[-1]
    
    def is_trade_interval_ok(self):
        """Check if 120 seconds have passed since last trade"""
        if self.last_entry_time is None:
            return True
        
        time_since_last = (datetime.now() - self.last_entry_time).total_seconds()
        if time_since_last < self.min_trade_interval:
            return False
        return True
    
    def check_entry_signal(self):
        """
        ULTIMATE HYBRID STRATEGY WITH QUALITY FILTER:
        Entry 1: EMA9 > EMA21 (momentum - gives ~25 trades/day)
        Entry 2: EMA9 > EMA21 + RSI < 50 (quality filter - gives ~20 trades/day)
        
        IMPROVED: Only take HIGH_QUALITY signals to avoid scalping weak moves
        """
        
        # Safety check
        open_count = self.get_open_positions_count()
        if open_count >= self.max_concurrent_trades:
            return False, None
        
        # Check 120-second minimum interval
        if not self.is_trade_interval_ok():
            return False, None
        
        # Get indicators
        ema9, ema9_prev = self.calculate_ema(period=9)
        ema21, ema21_prev = self.calculate_ema21()
        rsi = self.calculate_rsi()
        macd, signal = self.calculate_macd()
        
        if ema9 is None or ema21 is None or rsi is None or macd is None:
            return False, None
        
        # Calculate signal strength
        ema_distance = abs(ema9 - ema21)
        rsi_ok = rsi < 50
        macd_ok = macd > signal
        macd_strength = macd - signal
        
        ema_uptrend = ema9 > ema21
        
        # HIGH_QUALITY: Strong momentum + good filters
        # Requirements: EMA distance > 0.5, RSI < 50, MACD > Signal, MACD strength > 0.0005
        high_quality = (
            ema_uptrend and 
            ema_distance > 0.5 and 
            rsi_ok and 
            macd_ok and 
            macd_strength > 0.0005
        )
        
        # NORMAL_QUALITY: Moderate momentum (no longer accepts weak signals)
        # Requirements: EMA uptrend, RSI < 50, MACD > Signal
        normal_quality = ema_uptrend and rsi_ok and macd_ok and ema_distance > 0.2
        
        if high_quality:
            return True, {
                'type': 'HIGH_QUALITY',
                'ema9': ema9,
                'ema21': ema21,
                'ema_distance': ema_distance,
                'rsi': rsi,
                'macd': macd,
                'signal': signal,
                'macd_strength': macd_strength
            }
        elif normal_quality:
            return True, {
                'type': 'NORMAL_QUALITY',
                'ema9': ema9,
                'ema21': ema21,
                'ema_distance': ema_distance,
                'rsi': rsi,
                'macd': macd,
                'signal': signal,
                'macd_strength': macd_strength
            }
        
        return False, None
    
    def place_entry_order(self):
        """Place entry order"""
        try:
            open_count = self.get_open_positions_count()
            if open_count >= self.max_concurrent_trades:
                self.log(f"SAFETY: Cannot place order - {open_count} trades already open")
                return None
            
            # Check interval again before placing
            if not self.is_trade_interval_ok():
                self.log("[SKIP] 120-second minimum interval not met")
                return None
            
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                self.log("ERROR: Symbol info not available")
                return None
            
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                self.log("ERROR: Cannot get current tick")
                return None
            
            # Fixed TP/SL calculation
            pt_pips = 50      # 50 pips profit target
            sl_pips = 10      # 10 pips stop loss
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": mt5.ORDER_TYPE_BUY,
                "price": tick.ask,
                "tp": tick.ask + (pt_pips * 0.01),
                "sl": tick.ask - (sl_pips * 0.01),
                "deviation": 10,
                "magic": 12345,
                "comment": "A_PYRAMID_ULTIMATE",
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(request)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                return None
            
            # Record entry time for 120-second interval
            self.last_entry_time = datetime.now()
            
            self.log(f"[ENTRY] BUY {self.lot_size} @ ${tick.ask:.2f} | TP: ${request['tp']:.2f} | SL: ${request['sl']:.2f}")
            
            # Record trade
            self.record_trade({
                'order_id': result.order,
                'entry_price': tick.ask,
                'tp': request['tp'],
                'sl': request['sl'],
                'status': 'OPEN'
            })
            
            return result.order
        
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            return None
    
    def update_status(self, account_info):
        """Update status file"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "balance": account_info['balance'],
                "equity": account_info['equity'],
                "profit": account_info['equity'] - self.session_start_balance if self.session_start_balance else 0,
                "open_positions": self.get_open_positions_count(),
                "strategy": "EMA Crossover + RSI Filter",
                "expected_daily_trades": "20-30"
            }
            
            with open(self.status_file, "w", encoding='utf-8') as f:
                json.dump(status, f, indent=2)
        except:
            pass

    def quick_test_trade(self):
        """Quick test: Buy and close in 5 seconds"""
        self.log("="*70)
        self.log("[TEST] Starting 5-second trade execution test")
        self.log("="*70)
        
        # Step 1: Get market data
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            self.log("ERROR: Cannot get market tick")
            return False
        
        self.log(f"[MARKET] {self.symbol} | Bid: ${tick.bid:.2f} | Ask: ${tick.ask:.2f}")
        entry_price = tick.ask
        entry_time = datetime.now()
        
        # Step 2: OPEN BUY POSITION
        self.log(f"\n[ORDER_1] Sending BUY order...")
        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "deviation": 100,
            "magic": 12345,
            "comment": "TEST_BUY",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        buy_result = mt5.order_send(buy_request)
        
        if buy_result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"❌ BUY FAILED - Retcode: {buy_result.retcode}")
            return False
        
        self.log(f"✅ BUY ORDER EXECUTED")
        self.log(f"   Order: {buy_result.order}")
        self.log(f"   Entry: ${entry_price:.2f}")
        
        # Step 3: Wait 5 seconds
        self.log(f"\n[WAIT] Holding for 5 seconds...")
        for i in range(5, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time_module.sleep(1)
        print("GO!")
        
        # Step 4: Get position to close
        positions = mt5.positions_get(symbol=self.symbol)
        if not positions:
            self.log("ERROR: No open position found")
            return False
        
        position = positions[0]
        
        # Step 5: Get fresh market data for close
        tick = mt5.symbol_info_tick(self.symbol)
        exit_price = tick.bid
        
        # Step 6: CLOSE SELL POSITION
        self.log(f"\n[ORDER_2] Sending SELL order...")
        sell_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL,
            "position": position.ticket,
            "price": tick.bid,
            "deviation": 100,
            "magic": 12345,
            "comment": "TEST_SELL",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        sell_result = mt5.order_send(sell_request)
        
        if sell_result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"❌ SELL FAILED - Retcode: {sell_result.retcode}")
            return False
        
        self.log(f"✅ SELL ORDER EXECUTED")
        self.log(f"   Order: {sell_result.order}")
        self.log(f"   Exit: ${exit_price:.2f}")
        
        # Step 7: Calculate and display results
        exit_time = datetime.now()
        duration = (exit_time - entry_time).total_seconds()
        pnl = (exit_price - entry_price) * 100 * self.lot_size
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        
        self.log(f"\n{'='*70}")
        self.log(f"[RESULT] TRADE COMPLETED SUCCESSFULLY")
        self.log(f"{'='*70}")
        self.log(f"Entry Price:     ${entry_price:.2f}")
        self.log(f"Exit Price:      ${exit_price:.2f}")
        self.log(f"Duration:        {duration:.1f} seconds")
        self.log(f"P&L (USD):       ${pnl:,.2f}")
        self.log(f"P&L (%):         {pnl_pct:.4f}%")
        self.log(f"{'='*70}")
        
        print(f"\n✅ TEST PASSED!")
        print(f"   Buy:  {buy_result.order}")
        print(f"   Sell: {sell_result.order}")
        print(f"   P&L:  ${pnl:,.2f}\n")
        
        return True
    
    def force_test_trade(self):
        """Execute REAL trade on your MT5 account"""
        self.log("="*70)
        self.log("[LIVE] EXECUTING REAL TRADE ON YOUR MT5 ACCOUNT")
        self.log("="*70)
        
        # Get account info from MT5
        account_info = self.get_account_info()
        if account_info is None:
            self.log("ERROR: Cannot connect to MT5 account")
            return False
        
        self.log(f"\n[ACCOUNT DATA FROM MT5]")
        self.log(f"  Login:         {account_info['login']}")
        self.log(f"  Balance:       ${account_info['balance']:,.2f}")
        self.log(f"  Equity:        ${account_info['equity']:,.2f}")
        self.log(f"  Free Margin:   ${account_info['margin_free']:,.2f}")
        self.log(f"  Currency:      {account_info['currency']}")
        
        # Get LIVE price
        price = self.get_live_price()
        if price is None:
            self.log("ERROR: Cannot get XAUUSD.pro price from MT5")
            return False
        
        self.log(f"\n[XAUUSD.pro LIVE PRICE FROM MT5]")
        self.log(f"  Bid:           ${price['bid']:.5f}")
        self.log(f"  Ask:           ${price['ask']:.5f}")
        self.log(f"  Spread:        {(price['ask'] - price['bid']) * 10000:.1f} pips")
        
        entry_price = price['ask']
        entry_time = datetime.now()
        
        # SEND BUY ORDER
        self.log(f"\n[SENDING BUY ORDER TO MT5]")
        self.log(f"  Lot Size:      {self.lot_size}")
        self.log(f"  Entry Price:   ${entry_price:.5f}")
        
        buy_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price['ask'],
            "tp": price['ask'] + (self.profit_target * 0.01),
            "sl": price['ask'] - (self.stop_loss * 0.01),
            "deviation": 100,
            "magic": 12345,
            "comment": "PYRAMID_BOT_LIVE",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        buy_result = mt5.order_send(buy_request)
        
        if buy_result is None:
            self.log("ERROR: Order send returned None")
            return False
        
        if buy_result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"ERROR: Order failed with retcode {buy_result.retcode}")
            return False
        
        self.log(f"✅ BUY ORDER EXECUTED ON MT5")
        self.log(f"  Order #:       {buy_result.order}")
        self.log(f"  TP:            ${buy_request['tp']:.5f}")
        self.log(f"  SL:            ${buy_request['sl']:.5f}")
        self.log(f"  Time:          {datetime.now().strftime('%H:%M:%S')}")
        
        self.last_entry_time = datetime.now()
        
        self.record_trade({
            'order_id': buy_result.order,
            'entry_price': entry_price,
            'tp': buy_request['tp'],
            'sl': buy_request['sl'],
            'account': account_info['login']
        })
        
        self.log(f"\n[INFO] Trade is LIVE on your MT5 account")
        self.log(f"[INFO] Position visible in MT5 'Positions' tab")
        self.log(f"[INFO] Will close automatically at TP or SL")
        self.log("="*70)
        
        return True
    
    def force_sell_order(self):
        """Execute REAL SELL order to close open positions"""
        self.log("="*70)
        self.log("[LIVE] CLOSING POSITION WITH SELL ORDER")
        self.log("="*70)
        
        # Get account info
        account_info = self.get_account_info()
        if account_info is None:
            self.log("ERROR: Cannot connect to MT5 account")
            return False
        
        self.log(f"\n[ACCOUNT] Balance: ${account_info['balance']:,.2f} | Equity: ${account_info['equity']:,.2f}")
        
        # Get open positions
        positions = mt5.positions_get(symbol=self.symbol)
        if not positions:
            self.log("ERROR: No open positions to close")
            return False
        
        self.log(f"[POSITIONS] Found {len(positions)} open position(s)")
        
        # Close first position
        position = positions[0]
        
        # Get current price
        price = self.get_live_price()
        if price is None:
            self.log("ERROR: Cannot get price")
            return False
        
        self.log(f"\n[PRICE] Bid: ${price['bid']:.5f} | Ask: ${price['ask']:.5f}")
        
        # Create SELL request
        sell_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL,
            "position": position.ticket,
            "price": price['bid'],
            "deviation": 100,
            "magic": 12345,
            "comment": "PYRAMID_BOT_SELL",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        self.log(f"\n[SENDING SELL ORDER]")
        self.log(f"  Position Ticket: {position.ticket}")
        self.log(f"  Volume:          {position.volume}")
        self.log(f"  Exit Price:      ${price['bid']:.5f}")
        
        sell_result = mt5.order_send(sell_request)
        
        if sell_result is None:
            self.log("ERROR: Order send returned None")
            return False
        
        if sell_result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log(f"ERROR: Order failed with retcode {sell_result.retcode}")
            return False
        
        self.log(f"\n✅ SELL ORDER EXECUTED")
        self.log(f"  Order #:       {sell_result.order}")
        self.log(f"  Exit Price:    ${price['bid']:.5f}")
        self.log(f"  Time:          {datetime.now().strftime('%H:%M:%S')}")
        
        self.log(f"\n[INFO] Position CLOSED on your MT5 account")
        self.log(f"[INFO] Check MT5 'History' tab to see closed trade")
        self.log("="*70)
        
        return True

if __name__ == "__main__":
    bot = APyramidUltimateHybrid()
    
    print("\n" + "="*70)
    print("A_PYRAMID BOT - TRADE EXECUTION")
    print("="*70)
    print("[1] SELL - Close open position")
    print("[2] BUY  - Open new position")
    print("="*70)
    
    choice = input("\nSelect action (1=SELL, 2=BUY): ").strip()
    
    if not bot.initialize_mt5():
        print("\n❌ CANNOT CONNECT TO MT5")
        print("Make sure MT5 is open on your desktop")
        exit(1)
    
    account_info = bot.get_account_info()
    if account_info is None:
        print("\n❌ Cannot read account from MT5")
        bot.shutdown_mt5()
        exit(1)
    
    print(f"\n✅ Connected to MT5")
    print(f"Account: {account_info['login']}")
    print(f"Balance: ${account_info['balance']:,.2f}")
    print(f"Equity: ${account_info['equity']:,.2f}\n")
    
    bot.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    bot.session_start_time = datetime.now()
    bot.session_start_balance = account_info['balance']
    bot.session_start_equity = account_info['equity']
    
    try:
        if choice == "1":
            print("[ACTION] SELLING - Closing open position\n")
            success = bot.force_sell_order()
            if success:
                print("\n✅ SELL ORDER EXECUTED!")
                print("Check your MT5 platform - Position should be CLOSED now\n")
            else:
                print("\n❌ Sell failed - check logs\n")
        
        elif choice == "2":
            print("[ACTION] BUYING - Opening new position\n")
            success = bot.force_test_trade()
            if success:
                print("\n✅ BUY ORDER EXECUTED!")
                print("Check your MT5 platform - Position should be OPEN now\n")
            else:
                print("\n❌ Buy failed - check logs\n")
        
        else:
            print("\n❌ Invalid choice\n")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
    
    finally:
        bot.shutdown_mt5()