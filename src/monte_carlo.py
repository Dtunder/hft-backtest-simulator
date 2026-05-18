import os
import csv
import numpy as np
from backtester import HFTBacktestSimulator
from market_impact import MarketImpactModel

def run_monte_carlo(num_simulations=1000):
    print(f"Running {num_simulations} Monte Carlo simulations...")
    sharpe_ratios = []
    results = []

    impact_model = MarketImpactModel()

    for i in range(num_simulations):
        simulator = HFTBacktestSimulator(impact_model=impact_model)
        sharpe, final_val, trades = simulator.run_simulation(steps=1000, verbose=False)
        sharpe_ratios.append(sharpe)
        results.append({
            'simulation': i + 1,
            'sharpe_ratio': sharpe,
            'final_value': final_val,
            'trades': trades
        })

        if (i + 1) % 100 == 0:
            print(f"Completed {i + 1} simulations...")

    # Calculate 5th percentile worst-case Sharpe ratio
    percentile_5_sharpe = np.percentile(sharpe_ratios, 5)
    print(f"5th Percentile Worst-Case Sharpe Ratio: {percentile_5_sharpe:.4f}")

    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)

    # Save results to CSV
    csv_file = 'logs/monte_carlo_report.csv'
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['simulation', 'sharpe_ratio', 'final_value', 'trades'])
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {csv_file}")

    # Add a summary row or a separate file for the aggregate stats if needed.
    # For now, it just calculates and prints it, but let's append it to the CSV as well
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([])
        writer.writerow(['5th Percentile Sharpe Ratio', percentile_5_sharpe])

if __name__ == "__main__":
    run_monte_carlo(1000)
