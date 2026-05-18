import pytest
from src.backtester import HFTBacktestSimulator

def test_latency_variance():
    sim = HFTBacktestSimulator()
    sim.place_order('BUY', 10, 100.0)

    order = sim.pending_orders[0]

    assert 10.0 <= order['latency_ms'] <= 50.0
    assert order['execution_time'] == sim.current_time_ms + order['latency_ms']

def test_slippage_calculation():
    sim = HFTBacktestSimulator()
    sim.current_time_ms = 100

    # Force a specific latency and execution time
    sim.pending_orders.append({
        'type': 'BUY',
        'qty': 1000, # Large quantity to ensure slippage
        'queued_price': 100.0,
        'execution_time': 100,
        'latency_ms': 20.0
    })

    sim.process_orders(100.0)
    assert len(sim.history) == 1

    trade = sim.history[0]
    # Trade history format: ("BUY", exec_price, qty, latency_ms, slippage_pct)
    assert trade[0] == "BUY"
    assert trade[1] > 100.0 # exec_price > current_price due to slippage
    assert trade[4] > 0.0   # slippage_pct > 0
