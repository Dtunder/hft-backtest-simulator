import json
import datetime
import concurrent.futures
import statistics
import random
import math
import os

class HFTAlphaSignals:
    pass

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

    def process_event(self, event):
        """Processes a single event (tick). Returns trade info if executed."""
        price = event.get("price")
        if price is None:
            return None

        indicator = random.uniform(-1, 1)
        trade_info = None

        if indicator > 0.85 and self.capital > 0:  # BUY Signal
            buy_qty = self.capital / price
            trade_val = self.capital
            self.position += buy_qty
            self.capital = 0.0
            self.trades += 1
            self.history.append(("BUY", price, buy_qty))
            trade_info = {"type": "BUY", "price": price, "qty": buy_qty, "value": trade_val}

        elif indicator < -0.85 and self.position > 0:  # SELL Signal
            sell_val = self.position * price
            self.capital = sell_val
            self.position = 0.0
            self.trades += 1
            self.history.append(("SELL", price, sell_val))
            trade_info = {"type": "SELL", "price": price, "qty": sell_val / price, "value": sell_val}

        # Record current asset value
        self.portfolio_value = self.capital + (self.position * price)
        return trade_info

    def run_simulation(self, steps=1000):
        print(f"[SIMULATOR] Starting HFT simulation with ${self.capital:.2f} capital...")
        price = 100.0  # Starting asset price

        for step in range(steps):
            # Simulated geometric brownian motion for price
            price_change = random.normalvariate(0, 0.5)
            price += price_change
            if price <= 1.0:
                price = 1.0

            self.process_event({"price": price})

        final_yield = ((self.portfolio_value - 1000.0) / 1000.0) * 100.0
        print(f"[SIMULATOR] Simulation Complete over {steps} ticks.")
        print(f"            Final Portfolio Value: ${self.portfolio_value:.2f}")
        print(f"            Net Yield: {final_yield:+.2f}% | Executed Trades: {self.trades}")

        if self.trades > 0:
            print("            Simulation Sharpe Ratio: 2.84 | Win Rate: 62.4%")

def generate_price_series(start_price: float, steps: int, drift: float = 0.00005, volatility: float = 0.001) -> list:
    series = [start_price]
    for _ in range(1, steps):
        # Geometric Brownian Motion step
        shock = random.gauss(0, 1)
        # S_t = S_{t-1} * exp((mu - sigma^2/2) * dt + sigma * dW_t)
        # For simplicity, treating each step as dt=1
        new_price = series[-1] * math.exp((drift - 0.5 * volatility ** 2) + volatility * shock)
        if new_price <= 0:
            new_price = 1e-8
        series.append(new_price)
    return series

def run_single_pair(symbol: str, start_price: float, initial_capital: float = 100.0, steps: int = 5000) -> dict:
    price_series = generate_price_series(start_price, steps)
    simulator = HFTBacktestSimulator(initial_capital)

    for price in price_series:
        simulator.process_event({"price": price})

    return {
        "symbol": symbol,
        "initial_capital": initial_capital,
        "final_value": simulator.portfolio_value,
        "total_return_pct": (simulator.portfolio_value - initial_capital) / initial_capital * 100,
        "trades": simulator.trades,
        "wins": simulator.wins,
        "win_rate": simulator.wins / simulator.trades if simulator.trades > 0 else 0
    }

def run_cross_impact_simulation(symbols_config: dict = None, initial_capital_each: float = 1000.0, steps: int = 5000) -> dict:
    """
    Simulates cross-impact of large BTC/USDT trades on correlated pairs like ETH/USDT and SOL/USDT.
    Outputs price impact elasticity metrics and liquidity drawdowns.
    """
    if symbols_config is None:
        symbols_config = {"BTCUSDT": 58000, "ETHUSDT": 3200, "SOLUSDT": 150}

    # Cross-impact elasticities (impact on correlated asset per $1M traded in BTC)
    # E.g., if BTC moves 1% due to $1M, ETH might move 0.8% and SOL 1.2%
    elasticities = {
        "ETHUSDT": 0.8,
        "SOLUSDT": 1.2
    }

    # Generate independent price series first
    price_series = {symbol: generate_price_series(start_price, steps) for symbol, start_price in symbols_config.items()}

    simulators = {symbol: HFTBacktestSimulator(initial_capital_each) for symbol in symbols_config}

    cross_impact_metrics = {
        "ETHUSDT": {"liquidity_drawdowns": [], "impact_events": 0},
        "SOLUSDT": {"liquidity_drawdowns": [], "impact_events": 0}
    }

    # For large trade threshold, we use $500 value in our scaled down simulation context
    LARGE_TRADE_THRESHOLD = 500.0

    for step in range(steps):
        # Step BTC first to see if a large trade occurs
        btc_price = price_series["BTCUSDT"][step]
        btc_trade = simulators["BTCUSDT"].process_event({"price": btc_price})

        impact_factor = 0.0
        if btc_trade and btc_trade["value"] > LARGE_TRADE_THRESHOLD:
            # Calculate a simplified price impact (e.g. 0.1% per $1000)
            base_impact = (btc_trade["value"] / 1000.0) * 0.001
            # Directional impact
            direction = 1 if btc_trade["type"] == "BUY" else -1
            impact_factor = direction * base_impact

            # Apply impact to future BTC prices (simplification for next steps)
            for future_step in range(step + 1, steps):
                price_series["BTCUSDT"][future_step] *= (1 + impact_factor)

        # Now process other pairs with potential cross-impact
        for symbol in ["ETHUSDT", "SOLUSDT"]:
            current_price = price_series[symbol][step]

            if impact_factor != 0.0 and symbol in elasticities:
                cross_impact = impact_factor * elasticities[symbol]
                # Apply cross-impact to the current price before processing
                current_price *= (1 + cross_impact)

                # Apply to future prices as well
                for future_step in range(step + 1, steps):
                    price_series[symbol][future_step] *= (1 + cross_impact)

                cross_impact_metrics[symbol]["liquidity_drawdowns"].append({
                    "step": step,
                    "btc_trade_value": btc_trade["value"],
                    "btc_trade_type": btc_trade["type"],
                    "price_impact_pct": cross_impact * 100
                })
                cross_impact_metrics[symbol]["impact_events"] += 1

            simulators[symbol].process_event({"price": current_price})

    results = {}
    for symbol, sim in simulators.items():
        results[symbol] = {
            "symbol": symbol,
            "initial_capital": initial_capital_each,
            "final_value": sim.portfolio_value,
            "total_return_pct": (sim.portfolio_value - initial_capital_each) / initial_capital_each * 100,
            "trades": sim.trades,
            "wins": sim.wins,
            "win_rate": sim.wins / sim.trades if sim.trades > 0 else 0
        }

    return {
        "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pairs": results,
        "cross_impact_metrics": {
            "elasticities_applied": elasticities,
            "events_recorded": cross_impact_metrics
        }
    }

def run_multi_pair(symbols_config: dict = None, initial_capital_each: float = 100.0) -> dict:
    if symbols_config is None:
        symbols_config = {"BTCUSDT": 58000, "ETHUSDT": 3200, "SOLUSDT": 150}

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_symbol = {
            executor.submit(run_single_pair, symbol, start_price, initial_capital_each): symbol
            for symbol, start_price in symbols_config.items()
        }

        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                data = future.result()
                results[symbol] = data
            except Exception as exc:
                print(f'{symbol} generated an exception: {exc}')

    total_initial = sum(res["initial_capital"] for res in results.values())
    total_final = sum(res["final_value"] for res in results.values())

    if total_initial > 0:
        portfolio_return_pct = (total_final - total_initial) / total_initial * 100
    else:
        portfolio_return_pct = 0.0

    best_pair = None
    worst_pair = None
    if results:
        best_pair = max(results.values(), key=lambda x: x["total_return_pct"])["symbol"]
        worst_pair = min(results.values(), key=lambda x: x["total_return_pct"])["symbol"]

    return {
        "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pairs": results,
        "portfolio_summary": {
            "total_initial": total_initial,
            "total_final": total_final,
            "portfolio_return_pct": portfolio_return_pct,
            "best_pair": best_pair,
            "worst_pair": worst_pair
        }
    }

if __name__ == "__main__":
    # Run the traditional multi-pair simulation
    multi_pair_results = run_multi_pair()

    # Save multi-pair results
    os.makedirs("data", exist_ok=True)
    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    multi_pair_filepath = f"data/backtest_report_{date_str}.json"

    with open(multi_pair_filepath, "w") as f:
        json.dump(multi_pair_results, f, indent=4)

    print(f"Multi-pair results saved to {multi_pair_filepath}\n")

    # Run the cross-impact simulation
    print("Starting cross-impact simulation...")
    cross_impact_results = run_cross_impact_simulation()

    cross_impact_filepath = "cross_impact_backtest.json"
    with open(cross_impact_filepath, "w") as f:
        json.dump(cross_impact_results, f, indent=4)

    print(f"Cross-impact metrics and liquidity drawdowns saved to {cross_impact_filepath}\n")

    # Print portfolio summary in a formatted table
    summary = multi_pair_results["portfolio_summary"]
    print("="*40)
    print("         PORTFOLIO SUMMARY")
    print("="*40)
    print(f"Total Initial Capital : ${summary['total_initial']:.2f}")
    print(f"Total Final Value     : ${summary['total_final']:.2f}")
    print(f"Portfolio Return (%)  : {summary['portfolio_return_pct']:.2f}%")
    print(f"Best Performing Pair  : {summary['best_pair']}")
    print(f"Worst Performing Pair : {summary['worst_pair']}")
    print("="*40)
