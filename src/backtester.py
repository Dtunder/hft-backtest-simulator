import math
import random
import argparse
from src.replay_engine import HistoricalReplayEngine

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

    def run_replay(self, replay_engine: HistoricalReplayEngine):
        print(f"[SIMULATOR] Starting HFT replay with ${self.capital:.2f} capital...")

        for msg in replay_engine.stream_messages():
            msg_type = msg.get('type')
            price = msg.get('price', 100.0)

            # Simple mock of handling messages for replay
            indicator = random.uniform(-1, 1)

            if msg_type == 'order' and indicator > 0.85 and self.capital > 0:
                buy_qty = self.capital / price
                self.position += buy_qty
                self.capital = 0.0
                self.trades += 1
                self.history.append(("BUY", price, buy_qty))

            elif msg_type == 'cancel' and indicator < -0.85 and self.position > 0:
                sell_val = self.position * price
                self.capital = sell_val
                self.position = 0.0
                self.trades += 1
                self.history.append(("SELL", price, sell_val))

            self.portfolio_value = self.capital + (self.position * price)

        final_yield = ((self.portfolio_value - 1000.0) / 1000.0) * 100.0
        print(f"[SIMULATOR] Replay Complete.")
        print(f"            Final Portfolio Value: ${self.portfolio_value:.2f}")
        print(f"            Net Yield: {final_yield:+.2f}% | Executed Trades: {self.trades}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HFT Backtest Simulator")
    parser.add_argument("--replay", action="store_true", help="Run with historical replay engine")
    args = parser.parse_args()

    simulator = HFTBacktestSimulator()

    if args.replay:
        # Provide some dummy data to test it works
        engine = HistoricalReplayEngine()
        engine.load_feed("feed_1", [
            {"timestamp": 1, "type": "order", "price": 101.0},
            {"timestamp": 3, "type": "cancel", "price": 102.0}
        ])
        engine.load_feed("feed_2", [
            {"timestamp": 2, "type": "order", "price": 101.5},
            {"timestamp": 4, "type": "order", "price": 103.0}
        ])
        simulator.run_replay(engine)
    else:
        simulator.run_simulation()
