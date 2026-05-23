import math
import random
import statistics
import json
import os

class MonteCarloSimulator:
    def __init__(self, n_simulations=1000, initial_capital=50.0, target_capital=50000.0, ruin_threshold=0.20):
        self.n_simulations = n_simulations
        self.initial_capital = initial_capital
        self.target_capital = target_capital
        self.ruin_threshold = ruin_threshold

    def _run_simulations(self, path_generator_func, days):
        ruined_paths = 0
        target_reached = 0
        final_capitals = []
        days_to_target = []
        max_drawdowns = []

        for _ in range(self.n_simulations):
            capital = self.initial_capital
            peak_capital = self.initial_capital
            max_drawdown_pct = 0.0
            ruined = False
            reached_target = False
            days_taken = 0

            for day in range(days):
                capital = path_generator_func(capital)

                # Update peak and max drawdown
                if capital > peak_capital:
                    peak_capital = capital

                if peak_capital > 0:
                    current_drawdown = (peak_capital - capital) / peak_capital
                    if current_drawdown > max_drawdown_pct:
                        max_drawdown_pct = current_drawdown

                if capital <= self.initial_capital * (1.0 - self.ruin_threshold):
                    ruined = True
                    break

                if not reached_target and capital >= self.target_capital:
                    reached_target = True
                    days_taken = day + 1
                    # Can continue the path, or stop? The prompt says: "Track: did path reach target_capital? did path hit ruin_threshold?"
                    # Usually, we might just track it. If it hits ruin, we stop. Let's continue simulating to get final capital.

            if ruined:
                ruined_paths += 1
            if reached_target:
                target_reached += 1
                days_to_target.append(days_taken)

            final_capitals.append(capital)
            max_drawdowns.append(max_drawdown_pct)

        final_capitals.sort()

        return {
            "probability_of_ruin": ruined_paths / self.n_simulations,
            "probability_of_target": target_reached / self.n_simulations,
            "median_final_capital": statistics.median(final_capitals) if final_capitals else 0.0,
            "p10_final": final_capitals[int(0.10 * self.n_simulations)] if final_capitals else 0.0,
            "p90_final": final_capitals[int(0.90 * self.n_simulations)] if final_capitals else 0.0,
            "expected_days_to_target": statistics.mean(days_to_target) if days_to_target else 0.0,
            "max_drawdown_avg": statistics.mean(max_drawdowns) if max_drawdowns else 0.0
        }

    def simulate_from_trade_stats(self, win_rate: float, avg_win_pct: float, avg_loss_pct: float, trades_per_day: int, days: int = 365) -> dict:
        def path_generator(current_capital):
            cap = current_capital
            for _ in range(trades_per_day):
                if random.random() < win_rate:
                    cap *= (1.0 + avg_win_pct)
                else:
                    cap *= (1.0 - avg_loss_pct)
            return cap

        results = self._run_simulations(path_generator, days)
        results["params"] = {
            "win_rate": win_rate,
            "avg_win": avg_win_pct,
            "avg_loss": avg_loss_pct,
            "trades_per_day": trades_per_day
        }
        return results

    def print_report(self, result: dict):
        ruin_pct = result["probability_of_ruin"] * 100
        target_pct = result["probability_of_target"] * 100
        median_cap = result["median_final_capital"]
        p10 = result["p10_final"]
        p90 = result["p90_final"]
        days_to_target = result["expected_days_to_target"]

        verdict = "ACCEPTABLE RISK PROFILE" if ruin_pct <= (self.ruin_threshold * 100) else "HIGH RISK PROFILE"

        print("================================================")
        print(f"MONTE CARLO SIMULATION — {self.n_simulations} paths, 365 days")
        print("================================================")
        print(f"Risk of Ruin (lose >{int(self.ruin_threshold*100)}%):      {ruin_pct:.1f}%")
        print(f"Probability of Reaching {int(self.target_capital//1000)}k:   {target_pct:.1f}%")
        print(f"Median Final Capital:          ${median_cap:,.0f}")
        print(f"10th Percentile:               ${p10:,.0f}")
        print(f"90th Percentile:               ${p90:,.0f}")
        print(f"Expected Days to {int(self.target_capital//1000)}k:          {days_to_target:.0f} days")
        print("================================================")
        print(f"VERDICT: {verdict}")
        print("================================================")

    def save_report(self, result: dict, path: str = "data/monte_carlo_report.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(result, f, indent=4)

    def simulate_from_equity_curve(self, equity_curve: list, days: int = 365) -> dict:
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i-1] > 0:
                returns.append((equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1])
            else:
                returns.append(0.0)

        def path_generator(current_capital):
            if not returns:
                return current_capital
            daily_return = random.choice(returns)
            return current_capital * (1.0 + daily_return)

        results = self._run_simulations(path_generator, days)
        results["params"] = {
            "source": "equity_curve",
            "samples": len(returns)
        }
        return results

if __name__ == "__main__":
    mc = MonteCarloSimulator(n_simulations=500, initial_capital=50.0, target_capital=50000.0)

    # Scenario 1: Conservative (typical HFT stats)
    result1 = mc.simulate_from_trade_stats(
        win_rate=0.55, avg_win_pct=0.008, avg_loss_pct=0.005,
        trades_per_day=20, days=365)
    print("SCENARIO 1: Conservative")
    mc.print_report(result1)

    # Scenario 2: Aggressive with leverage
    result2 = mc.simulate_from_trade_stats(
        win_rate=0.52, avg_win_pct=0.020, avg_loss_pct=0.015,
        trades_per_day=10, days=365)
    print("SCENARIO 2: Aggressive")
    mc.print_report(result2)

    mc.save_report(result1, "data/monte_carlo_conservative.json")
    mc.save_report(result2, "data/monte_carlo_aggressive.json")
