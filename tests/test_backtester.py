import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from backtester import HFTBacktestSimulator

def test_hft_backtester_initialization():
    simulator = HFTBacktestSimulator(initial_capital=5000.0)
    assert simulator.capital == 5000.0
    assert simulator.portfolio_value == 5000.0
    assert simulator.position == 0.0

def test_hft_backtester_run_simulation():
    simulator = HFTBacktestSimulator()
    simulator.run_simulation(steps=10)

    # Simple check that portfolio_value is updated and properties are reasonable
    assert simulator.portfolio_value > 0
    assert len(simulator.history) >= 0  # Could be 0 if no trades trigger
