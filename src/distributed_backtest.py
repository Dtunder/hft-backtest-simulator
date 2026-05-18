import time
import os
import csv
import ray
from src.backtester import HFTBacktestSimulator

@ray.remote
def run_single_simulation(steps=1000):
    sim = HFTBacktestSimulator()
    sim.run_simulation(steps=steps)

    # We want to return the final portfolio value, net yield, and number of executed trades
    final_yield = ((sim.portfolio_value - 1000.0) / 1000.0) * 100.0
    return {
        "final_portfolio_value": sim.portfolio_value,
        "net_yield": final_yield,
        "executed_trades": sim.trades
    }

def run_sequential(num_iterations, steps=1000):
    results = []
    start_time = time.time()
    for _ in range(num_iterations):
        sim = HFTBacktestSimulator()
        sim.run_simulation(steps=steps)
        final_yield = ((sim.portfolio_value - 1000.0) / 1000.0) * 100.0
        results.append({
            "final_portfolio_value": sim.portfolio_value,
            "net_yield": final_yield,
            "executed_trades": sim.trades
        })
    end_time = time.time()
    return results, end_time - start_time

def run_distributed(num_iterations, steps=1000):
    start_time = time.time()

    # Submit tasks to Ray
    futures = [run_single_simulation.remote(steps) for _ in range(num_iterations)]

    # Retrieve results
    results = ray.get(futures)

    end_time = time.time()
    return results, end_time - start_time

def main():
    num_iterations = 10000
    steps = 1000

    print("Initializing Ray...")
    ray.init(ignore_reinit_error=True)

    # For fair speedup comparison, we might want to do a smaller test for sequential
    # But since the task requires a 10,000 iteration simulation and speedup factor,
    # we'll do both (or scale the sequential if it's too slow).
    # Since 100 iterations took ~0.13s, 10,000 should take ~13s, which is perfectly runnable.

    print(f"Running {num_iterations} sequential simulations...")
    _, seq_time = run_sequential(num_iterations, steps)
    print(f"Sequential execution time: {seq_time:.2f} seconds")

    print(f"Running {num_iterations} distributed simulations...")
    results, dist_time = run_distributed(num_iterations, steps)
    print(f"Distributed execution time: {dist_time:.2f} seconds")

    speedup = seq_time / dist_time if dist_time > 0 else float('inf')
    print(f"Speedup factor: {speedup:.2f}x")

    # Save results to logs/distributed_monte_carlo.csv
    os.makedirs("logs", exist_ok=True)
    csv_file = "logs/distributed_monte_carlo.csv"

    with open(csv_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["final_portfolio_value", "net_yield", "executed_trades"])
        writer.writeheader()
        for res in results:
            writer.writerow(res)

    print(f"Results saved to {csv_file}")

    ray.shutdown()

if __name__ == "__main__":
    main()
