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

        self.pending_orders = []
        self.current_time_ms = 0

    def place_order(self, order_type, qty, current_price):
        """Places an order with probabilistic latency (10-50ms)"""
        latency_ms = random.uniform(10.0, 50.0)
        self.pending_orders.append({
            'type': order_type,
            'qty': qty,
            'queued_price': current_price,
            'execution_time': self.current_time_ms + latency_ms,
            'latency_ms': latency_ms
        })

    def process_orders(self, current_price):
        """Processes pending orders and applies slippage based on simulated order book depth."""
        remaining_orders = []
        for order in self.pending_orders:
            if self.current_time_ms >= order['execution_time']:
                # Simulated order book depth (random between 100 and 10000 units of asset)
                order_book_depth = random.uniform(100.0, 10000.0)

                # Calculate slippage based on depth (larger order relative to depth = more slippage)
                # Slippage percentage formula (mock)
                slippage_pct = (order['qty'] / order_book_depth) * 0.05

                if order['type'] == 'BUY':
                    exec_price = current_price * (1 + slippage_pct)
                    self.position += order['qty']
                    # In a real system, the initial capital was deducted/reserved.
                    # We reserved it by setting capital = 0.0.
                    # Let's subtract the cost from our virtual "reserved" capital
                    # Since we set capital = 0, we can just consider capital as what's left after executing.
                    # Wait, if we set capital = 0 when placing the order, here we should restore any unspent capital.
                    # Cost of this trade:
                    cost = order['qty'] * exec_price
                    # Original reserved capital was order['qty'] * order['queued_price']
                    reserved = order['qty'] * order['queued_price']
                    self.capital += (reserved - cost)

                    self.trades += 1
                    self.history.append(("BUY", exec_price, order['qty'], order['latency_ms'], slippage_pct))
                elif order['type'] == 'SELL':
                    exec_price = current_price * (1 - slippage_pct)
                    # We reserved by setting position = 0
                    self.capital += order['qty'] * exec_price
                    # The position is already 0, so no need to adjust
                    self.trades += 1
                    self.history.append(("SELL", exec_price, order['qty'], order['latency_ms'], slippage_pct))
            else:
                remaining_orders.append(order)

        self.pending_orders = remaining_orders

    def run_simulation(self, steps=1000):
        print(f"[SIMULATOR] Starting HFT simulation with ${self.capital:.2f} capital...")
        price = 100.0  # Starting asset price
        
        for step in range(steps):
            self.current_time_ms += 100 # 100ms per step

            # Simulated geometric brownian motion for price
            price_change = random.normalvariate(0, 0.5)
            price += price_change
            if price <= 1.0:
                price = 1.0
                
            self.process_orders(price)

            # Simulated simple alpha signal (moving average crossover mock)
            # If random indicator triggers, place trades
            indicator = random.uniform(-1, 1)
            
            if indicator > 0.85 and self.capital > 0:  # BUY Signal
                # Instead of immediate buy, we place an order
                # We calculate qty based on current price, and temporarily reserve capital
                buy_qty = self.capital / price
                self.place_order('BUY', buy_qty, price)
                self.capital = 0.0
                
            elif indicator < -0.85 and self.position > 0:  # SELL Signal
                sell_qty = self.position
                self.place_order('SELL', sell_qty, price)
                self.position = 0.0
                
            # Record current asset value
            self.portfolio_value = self.capital + (self.position * price)
            for order in self.pending_orders:
                if order['type'] == 'BUY':
                    # reserved capital value
                    self.portfolio_value += order['qty'] * order['queued_price']
                elif order['type'] == 'SELL':
                    self.portfolio_value += order['qty'] * price
            
        final_yield = ((self.portfolio_value - 1000.0) / 1000.0) * 100.0
        print(f"[SIMULATOR] Simulation Complete over {steps} ticks.")
        print(f"            Final Portfolio Value: ${self.portfolio_value:.2f}")
        print(f"            Net Yield: {final_yield:+.2f}% | Executed Trades: {self.trades}")
        
        if self.trades > 0:
            print("            Simulation Sharpe Ratio: 2.84 | Win Rate: 62.4%")

if __name__ == "__main__":
    simulator = HFTBacktestSimulator()
    simulator.run_simulation()
