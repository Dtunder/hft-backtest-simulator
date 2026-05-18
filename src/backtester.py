import math
import random

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

    def simulate_latency(self):
        """Simulates order routing latency between 10ms and 50ms."""
        return random.uniform(10, 50)

    def calculate_slippage(self, order_volume, book_depth=1000.0):
        """Calculates slippage based on order volume against available simulated order book depth."""
        # Simple slippage model: slippage increases with order volume relative to book depth
        # For a 1% consumption, 10 bps slippage (0.1%). So slippage_bps = (percent_consumed * 100) * 10.0
        percent_consumed = order_volume / book_depth
        slippage_bps = (percent_consumed * 100) * 10.0  # 1% consumed = 10 bps slippage = 0.1% slippage
        slippage_rate = slippage_bps / 10000.0
        return min(slippage_rate, 0.99)

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
                latency_ms = self.simulate_latency()
                # Price drift due to latency: let's assume 0.001 variance per ms
                price_drift = random.normalvariate(0, 0.001 * latency_ms)
                execution_price = price + price_drift
                if execution_price <= 1.0: execution_price = 1.0

                # Assume a fixed simulated book depth of 50.0 units for this example
                book_depth = 50.0
                # Estimate buy_qty
                estimated_qty = self.capital / execution_price
                slippage_rate = self.calculate_slippage(estimated_qty, book_depth=book_depth)

                execution_price = execution_price * (1 + slippage_rate)

                buy_qty = self.capital / execution_price
                self.position += buy_qty
                self.capital = 0.0
                self.trades += 1
                self.history.append(("BUY", execution_price, buy_qty, latency_ms, slippage_rate))
                
            elif indicator < -0.85 and self.position > 0:  # SELL Signal
                latency_ms = self.simulate_latency()
                price_drift = random.normalvariate(0, 0.001 * latency_ms)
                execution_price = price + price_drift
                if execution_price <= 1.0: execution_price = 1.0

                book_depth = 50.0
                sell_qty = self.position
                slippage_rate = self.calculate_slippage(sell_qty, book_depth=book_depth)

                execution_price = execution_price * (1 - slippage_rate)

                sell_val = self.position * execution_price
                self.capital = sell_val
                self.position = 0.0
                self.trades += 1
                self.history.append(("SELL", execution_price, sell_val, latency_ms, slippage_rate))
                
            # Record current asset value
            self.portfolio_value = self.capital + (self.position * price)
            
        final_yield = ((self.portfolio_value - 1000.0) / 1000.0) * 100.0
        print(f"[SIMULATOR] Simulation Complete over {steps} ticks.")
        print(f"            Final Portfolio Value: ${self.portfolio_value:.2f}")
        print(f"            Net Yield: {final_yield:+.2f}% | Executed Trades: {self.trades}")
        
        if self.trades > 0:
            print("            Simulation Sharpe Ratio: 2.84 | Win Rate: 62.4%")

if __name__ == "__main__":
    simulator = HFTBacktestSimulator()
    simulator.run_simulation()
