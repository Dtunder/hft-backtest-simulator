import json
import random
import os
import math
import datetime
import time
import requests
from src.metrics import PerformanceMetrics
from src.monte_carlo import MonteCarloSimulator

class HFTBacktestSimulator:
    """
    Event-driven tick-level simulator for high-frequency trading.
    Simulates trades, calculates metrics, runs 50-cents-to-50k challenge, and outputs results.
    """
    def __init__(self, data_path="data/btc_1m.json"):
        self.data_path = data_path
        self.initial_capital = 0.50
        self.leverage = 100
        self.capital = self.initial_capital
        self.target_capital = 50000.0
        self.position = 0.0
        self.position_type = None
        self.entry_price = 0.0
        self.equity_curve = [self.initial_capital]
        self.pnl_list = []
        self.trades = 0
        self.liquidation_threshold = 0.005 # 0.5% price move against 100x leverage = liquidation
        self.liquidated = False

        self._ensure_data()
        with open(data_path, "r") as f:
            self.data = json.load(f)

    def _ensure_data(self):
        if not os.path.exists(self.data_path):
            print(f"Data file {self.data_path} not found. Fetching from Binance...")
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

            endpoint = "https://api.binance.com/api/v3/klines"
            now_dt = datetime.datetime.now(datetime.timezone.utc)
            now = int(now_dt.timestamp() * 1000)
            start_time = now - (30 * 24 * 60 * 60 * 1000)

            all_klines = []
            current_start = start_time

            while current_start < now:
                params = {
                    "symbol": "BTCUSDT",
                    "interval": "1m",
                    "startTime": current_start,
                    "endTime": now,
                    "limit": 1000
                }
                try:
                    response = requests.get(endpoint, params=params)
                    response.raise_for_status()
                    data = response.json()
                    if not data:
                        break
                    all_klines.extend(data)
                    current_start = data[-1][0] + 1
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Error fetching data: {e}")
                    break
            
            with open(self.data_path, "w") as f:
                json.dump(all_klines, f)
            print(f"Fetched {len(all_klines)} candles and saved to {self.data_path}")

    def run_simulation(self):
        print(f"Loaded {len(self.data)} candles. Starting 50-cents-to-50k challenge backtest...")

        current_price = float(self.data[0][4])

        for i in range(1, len(self.data)):
            if self.liquidated:
                break

            candle = self.data[i]
            prev_candle = self.data[i-1]

            close = float(candle[4])
            prev_close = float(prev_candle[4])
            price_change_pct = (close - prev_close) / prev_close

            # OBI Signal Simulation (proxy using price momentum and noise)
            obi_signal = price_change_pct + random.normalvariate(0, 0.001)

            # Entry Logic with SOR proxy
            if self.position == 0 and self.capital > 0:
                if obi_signal > 0.001: # Buy signal
                    notional_size = self.capital * self.leverage
                    self.position = notional_size / close
                    self.entry_price = close
                    self.position_type = "LONG"
                    self.entry_portfolio_value = self.capital
                elif obi_signal < -0.001: # Sell signal
                    notional_size = self.capital * self.leverage
                    self.position = notional_size / close
                    self.entry_price = close
                    self.position_type = "SHORT"
                    self.entry_portfolio_value = self.capital

            # Exit logic / DDL Risk Check (Liquidation check)
            elif self.position > 0:
                high = float(candle[2])
                low = float(candle[3])

                liquidation_price_long = self.entry_price * (1 - self.liquidation_threshold)
                liquidation_price_short = self.entry_price * (1 + self.liquidation_threshold)

                if self.position_type == "LONG" and low <= liquidation_price_long:
                    trade_pct = -1.0 # 100% loss of capital due to liquidation
                    self.capital = 0
                    self.position = 0
                    self.liquidated = True
                    self.pnl_list.append(-self.equity_curve[-1])
                    if not hasattr(self, 'trade_returns'): self.trade_returns = []
                    self.trade_returns.append(trade_pct)
                    self.equity_curve.append(0)
                    self.trades += 1
                    continue
                elif self.position_type == "SHORT" and high >= liquidation_price_short:
                    trade_pct = -1.0 # 100% loss of capital due to liquidation
                    self.capital = 0
                    self.position = 0
                    self.liquidated = True
                    self.pnl_list.append(-self.equity_curve[-1])
                    if not hasattr(self, 'trade_returns'): self.trade_returns = []
                    self.trade_returns.append(trade_pct)
                    self.equity_curve.append(0)
                    self.trades += 1
                    continue

                # Take profit / Signal reversal exit
                if (self.position_type == "LONG" and obi_signal < -0.0005) or \
                   (self.position_type == "SHORT" and obi_signal > 0.0005):

                   if self.position_type == "LONG":
                       pnl = (close - self.entry_price) * self.position
                   else:
                       pnl = (self.entry_price - close) * self.position

                   fees = (self.position * close) * 0.0004 * 2 # simple fee model
                   net_pnl = pnl - fees

                   trade_pct = net_pnl / self.entry_portfolio_value if self.entry_portfolio_value > 0 else 0
                   if not hasattr(self, 'trade_returns'): self.trade_returns = []
                   self.trade_returns.append(trade_pct)
                   self.capital += net_pnl
                   self.pnl_list.append(net_pnl)
                   self.position = 0
                   self.trades += 1

            # Update equity curve
            current_portfolio_value = self.capital
            if self.position > 0:
                if self.position_type == "LONG":
                    unrealized_pnl = (close - self.entry_price) * self.position
                else:
                    unrealized_pnl = (self.entry_price - close) * self.position
                current_portfolio_value += unrealized_pnl

            self.equity_curve.append(current_portfolio_value)

            if current_portfolio_value >= self.target_capital:
                print("Target reached!")
                break

        self.generate_results()

    def generate_results(self):
        metrics = PerformanceMetrics()
        sharpe = metrics.sharpe_ratio(self.equity_curve)
        mdd = metrics.max_drawdown(self.equity_curve) * 100
        win_rate = metrics.win_rate(self.pnl_list) if self.trades > 0 else 0

        # Monte Carlo for Probability of reaching 50k
        mc = MonteCarloSimulator(n_simulations=1000, initial_capital=0.50, target_capital=50000.0, ruin_threshold=1.0)

        avg_win_pct = 0.0
        avg_loss_pct = 0.0

        if self.trades > 0:
            if hasattr(self, 'trade_returns'):
                win_pcts = [pct for pct in self.trade_returns if pct > 0]
                loss_pcts = [abs(pct) for pct in self.trade_returns if pct <= 0]

                if win_pcts:
                    avg_win_pct = sum(win_pcts) / len(win_pcts)
                if loss_pcts:
                    avg_loss_pct = sum(loss_pcts) / len(loss_pcts)

        trades_per_day = self.trades / 30 if self.trades > 0 else 0

        if self.trades > 0 and win_rate > 0 and avg_win_pct > 0 and avg_loss_pct > 0:
            mc_results = mc.simulate_from_trade_stats(
                win_rate=win_rate,
                avg_win_pct=avg_win_pct,
                avg_loss_pct=avg_loss_pct,
                trades_per_day=max(1, int(trades_per_day)),
                days=30
            )
            prob_target = mc_results["probability_of_target"]
        else:
            prob_target = 0.0

        final_capital = self.equity_curve[-1]

        results = {
            "Final Capital": final_capital,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": mdd,
            "Total Trades": self.trades,
            "Win Rate": win_rate,
            "Probability of Reaching 50k": prob_target
        }

        with open("backtest_results.json", "w") as f:
            json.dump(results, f, indent=4)

        print("Backtest results written to backtest_results.json")
        print(json.dumps(results, indent=4))

if __name__ == "__main__":
    simulator = HFTBacktestSimulator()
    simulator.run_simulation()
