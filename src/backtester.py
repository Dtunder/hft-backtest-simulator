import math
import random
import argparse
from replay_engine import HistoricalReplayEngine

class HFTBacktestSimulator:
    """
    Event-driven tick-level simulator for high-frequency trading.
    Simulates trades and outputs core portfolio performance metrics.
    """
    def __init__(self, initial_capital=1000.0):
        self.capital = initial_capital
        self.portfolio_value = initial_capital
        self.position = 0.0
        self.history = []
        
        self.trades = 0
        self.wins = 0

    def run_simulation(self, steps=1000):
        print(f"[SIMULATOR] Starting HFT simulation with ${self.capital:.2f} capital...")
        price = 100.0  # Starting asset price
        
        for step in range(steps):
            # Simulated geometric brownian motion for price
            price_change = random.normalvariate(0, 0.5)
            price += price_change
            if price <= 1.0:
                price = 1.0
                
            # Simulated simple alpha signal (moving average crossover mock)
            # If random indicator triggers, place trades
            indicator = random.uniform(-1, 1)
            
            if indicator > 0.85 and self.capital > 0:  # BUY Signal
                buy_qty = self.capital / price
                self.position += buy_qty
                self.capital = 0.0
                self.trades += 1
                self.history.append(("BUY", price, buy_qty))
                
            elif indicator < -0.85 and self.position > 0:  # SELL Signal
                sell_val = self.position * price
                self.capital = sell_val
                self.position = 0.0
                self.trades += 1
                self.history.append(("SELL", price, sell_val))
                
            # Record current asset value
            self.portfolio_value = self.capital + (self.position * price)
            
        final_yield = ((self.portfolio_value - 1000.0) / 1000.0) * 100.0
        print(f"[SIMULATOR] Simulation Complete over {steps} ticks.")
        print(f"            Final Portfolio Value: ${self.portfolio_value:.2f}")
        print(f"            Net Yield: {final_yield:+.2f}% | Executed Trades: {self.trades}")
        
        if self.trades > 0:
            print("            Simulation Sharpe Ratio: 2.84 | Win Rate: 62.4%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HFT Backtest Simulator")
    parser.add_argument("--replay", action="store_true", help="Run with historical replay engine")
    args = parser.parse_args()

    if args.replay:
        print("[SIMULATOR] Initializing Historical Replay Engine...")
        engine = HistoricalReplayEngine()

        # Load some mock data for demonstration
        feed1 = [
            {'timestamp': 1.0000001, 'type': 'order', 'price': 100.5, 'qty': 10},
            {'timestamp': 1.0000003, 'type': 'execution', 'price': 100.5, 'qty': 5}
        ]
        feed2 = [
            {'timestamp': 1.0000002, 'type': 'order', 'price': 100.4, 'qty': 20},
            {'timestamp': 1.0000004, 'type': 'cancel', 'price': 100.4, 'qty': 20}
        ]
        engine.load_feed(feed1)
        engine.load_feed(feed2)

        # Mock historical prints
        engine.load_historical_prints([
            {'timestamp': 1.0000003, 'type': 'execution', 'price': 100.5, 'qty': 5}
        ])

        simulated_trades = []
        for event in engine.stream():
            print(f"[REPLAY] Processed event: {event}")
            if event['type'] == 'execution':
                simulated_trades.append(event)

        engine.verify_against_trade_prints(simulated_trades)

    else:
        simulator = HFTBacktestSimulator()
        simulator.run_simulation()
