import pytest
from src.replay_engine import HistoricalReplayEngine

def test_historical_replay_engine_stream_merge():
    engine = HistoricalReplayEngine()

    feed1 = [
        {'timestamp': 1.0000001, 'type': 'order', 'price': 100.5, 'qty': 10},
        {'timestamp': 1.0000003, 'type': 'execution', 'price': 100.5, 'qty': 5}
    ]
    feed2 = [
        {'timestamp': 1.0000002, 'type': 'order', 'price': 100.4, 'qty': 20},
        {'timestamp': 1.0000004, 'type': 'cancel', 'price': 100.4, 'qty': 20}
    ]
    feed3 = [
        {'timestamp': 1.00000005, 'type': 'order', 'price': 100.6, 'qty': 5}
    ]

    engine.load_feed(feed1)
    engine.load_feed(feed2)
    engine.load_feed(feed3)

    events = list(engine.stream())

    assert len(events) == 5
    assert events[0]['timestamp'] == 1.00000005
    assert events[1]['timestamp'] == 1.0000001
    assert events[2]['timestamp'] == 1.0000002
    assert events[3]['timestamp'] == 1.0000003
    assert events[4]['timestamp'] == 1.0000004

def test_historical_replay_engine_verify_against_trade_prints():
    engine = HistoricalReplayEngine()

    historical_prints = [
        {'timestamp': 1.0000003, 'type': 'execution', 'price': 100.5, 'qty': 5},
        {'timestamp': 1.0000005, 'type': 'execution', 'price': 100.6, 'qty': 10}
    ]
    engine.load_historical_prints(historical_prints)

    # Correct simulated trades
    simulated_trades_success = [
        {'timestamp': 1.0000003, 'type': 'execution', 'price': 100.5, 'qty': 5},
        {'timestamp': 1.0000005, 'type': 'execution', 'price': 100.6, 'qty': 10}
    ]
    assert engine.verify_against_trade_prints(simulated_trades_success) == True

    # Incorrect simulated trades (length mismatch)
    simulated_trades_fail_len = [
        {'timestamp': 1.0000003, 'type': 'execution', 'price': 100.5, 'qty': 5}
    ]
    assert engine.verify_against_trade_prints(simulated_trades_fail_len) == False

    # Incorrect simulated trades (data mismatch)
    simulated_trades_fail_data = [
        {'timestamp': 1.0000003, 'type': 'execution', 'price': 100.5, 'qty': 5},
        {'timestamp': 1.0000005, 'type': 'execution', 'price': 100.6, 'qty': 5} # Wrong qty
    ]
    assert engine.verify_against_trade_prints(simulated_trades_fail_data) == False
