import pytest
import numpy as np
from src.backtester import HFTBacktestSimulator

def test_simulate_latency_bounds_and_variance():
    simulator = HFTBacktestSimulator()
    latencies = [simulator.simulate_latency() for _ in range(1000)]

    # Check bounds
    assert all(10 <= l <= 50 for l in latencies), "Latencies out of bounds [10, 50]"

    # Check variance to ensure it's not returning a constant value
    variance = np.var(latencies)
    assert variance > 10.0, f"Variance too low: {variance}"

def test_calculate_slippage():
    simulator = HFTBacktestSimulator()

    # Example 1: 10 volume, 1000 depth -> 1% consumed -> 10 bps slippage -> 0.001
    slippage1 = simulator.calculate_slippage(10.0, 1000.0)
    assert pytest.approx(slippage1, 0.0001) == 0.001

    # Example 2: 50 volume, 1000 depth -> 5% consumed -> 50 bps slippage -> 0.005
    slippage2 = simulator.calculate_slippage(50.0, 1000.0)
    assert pytest.approx(slippage2, 0.0001) == 0.005

    # Example 3: slippage increases with volume
    slippage3 = simulator.calculate_slippage(100.0, 1000.0)
    assert slippage3 > slippage2 > slippage1
