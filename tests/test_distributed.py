import os
import pytest
import ray
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.distributed_backtest import run_single_simulation, run_distributed

@pytest.fixture(scope="module")
def ray_setup():
    ray.init(ignore_reinit_error=True)
    yield
    ray.shutdown()

def test_run_single_simulation_returns_correct_keys(ray_setup):
    future = run_single_simulation.remote(steps=10)
    result = ray.get(future)

    assert isinstance(result, dict)
    assert "final_portfolio_value" in result
    assert "net_yield" in result
    assert "executed_trades" in result

def test_run_distributed_returns_correct_number_of_results(ray_setup):
    num_iterations = 5
    results, exec_time = run_distributed(num_iterations, steps=10)

    assert isinstance(results, list)
    assert len(results) == num_iterations
    assert exec_time > 0

    for res in results:
        assert "final_portfolio_value" in res
        assert "net_yield" in res
        assert "executed_trades" in res
