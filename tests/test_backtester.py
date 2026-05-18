import pytest
from src.backtester import HFTBacktestSimulator
from src.replay_engine import HistoricalReplayEngine

def test_backtester_initialization():
    simulator = HFTBacktestSimulator(initial_capital=2000.0)
    assert simulator.capital == 2000.0
    assert simulator.portfolio_value == 2000.0
    assert simulator.position == 0.0
    assert simulator.trades == 0

def test_backtester_simulation_runs():
    simulator = HFTBacktestSimulator()
    simulator.run_simulation(steps=50)
    assert simulator.portfolio_value > 0.0

def test_backtester_replay():
    simulator = HFTBacktestSimulator()
    engine = HistoricalReplayEngine()
    engine.load_feed("feed_1", [
        {"timestamp": 1, "type": "order", "price": 101.0},
        {"timestamp": 3, "type": "cancel", "price": 102.0}
    ])
    simulator.run_replay(engine)
    # Basic check to ensure it ran without crashing
    assert simulator.portfolio_value > 0.0
