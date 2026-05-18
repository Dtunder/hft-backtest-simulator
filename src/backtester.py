import math
import random

from market_impact import MarketImpactModel
import numpy as np

class HFTBacktestSimulator:
    """
    Event-driven tick-level simulator for high-frequency trading.
    Simulates trades and outputs core portfolio performance metrics.
    """
    def __init__(self, initial_capital=1000.0, impact_model=None):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.portfolio_value = initial_capital
        self.position = 0.0
        self.history = []
        self.impact_model = impact_model
        
        self.trades = 0
        self.wins = 0
        self.returns = []
        self.portfolio_values = [initial_capital]

    def run_simulation(self, steps=1000, verbose=True):
        if verbose:
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
                # Iteratively calculate buy qty with market impact
                base_buy_qty = self.capital / price
                fill_price = self.impact_model.get_fill_price(price, base_buy_qty, is_buy=True) if self.impact_model else price
                buy_qty = self.capital / fill_price

                self.position += buy_qty
                self.capital = 0.0
                self.trades += 1
                self.history.append(("BUY", fill_price, buy_qty))
                
            elif indicator < -0.85 and self.position > 0:  # SELL Signal
                sell_qty = self.position
                fill_price = self.impact_model.get_fill_price(price, sell_qty, is_buy=False) if self.impact_model else price
                sell_val = sell_qty * fill_price

                self.capital = sell_val
                self.position = 0.0
                self.trades += 1
                self.history.append(("SELL", fill_price, sell_qty))
                
            # Record current asset value
            prev_value = self.portfolio_value
            self.portfolio_value = self.capital + (self.position * price)
            self.portfolio_values.append(self.portfolio_value)
            
            step_return = (self.portfolio_value - prev_value) / prev_value if prev_value > 0 else 0
            self.returns.append(step_return)

        final_yield = ((self.portfolio_value - self.initial_capital) / self.initial_capital) * 100.0
        
        # Calculate Sharpe Ratio
        if len(self.returns) > 0 and np.std(self.returns) > 0:
            sharpe_ratio = np.mean(self.returns) / np.std(self.returns) * np.sqrt(252 * 23400) # Assuming 1-sec ticks, 6.5 hours/day
        else:
            sharpe_ratio = 0.0

        if verbose:
            print(f"[SIMULATOR] Simulation Complete over {steps} ticks.")
            print(f"            Final Portfolio Value: ${self.portfolio_value:.2f}")
            print(f"            Net Yield: {final_yield:+.2f}% | Executed Trades: {self.trades}")
            if self.trades > 0:
                print(f"            Simulation Sharpe Ratio: {sharpe_ratio:.4f}")

        return sharpe_ratio, self.portfolio_value, self.trades

if __name__ == "__main__":
    simulator = HFTBacktestSimulator()
    simulator.run_simulation()
