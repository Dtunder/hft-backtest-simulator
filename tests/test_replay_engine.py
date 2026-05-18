import pytest
from src.replay_engine import HistoricalReplayEngine

def test_replay_engine_merging():
    engine = HistoricalReplayEngine()

    feed1 = [
        {'timestamp': 1000, 'type': 'order'},
        {'timestamp': 1005, 'type': 'cancel'}
    ]
    feed2 = [
        {'timestamp': 1002, 'type': 'order'},
        {'timestamp': 1004, 'type': 'execution'}
    ]
    feed3 = [
        {'timestamp': 1001, 'type': 'order'},
        {'timestamp': 1003, 'type': 'cancel'}
    ]

    engine.add_feed(feed1)
    engine.add_feed(feed2)
    engine.add_feed(feed3)

    events = list(engine.replay())

    assert len(events) == 6
    timestamps = [e['timestamp'] for e in events]
    assert timestamps == [1000, 1001, 1002, 1003, 1004, 1005]

def test_verify_against_trade_prints():
    engine = HistoricalReplayEngine()

    executions = [
        {'timestamp': 1000, 'price': 100.0, 'size': 10},
        {'timestamp': 1005, 'price': 101.0, 'size': 5}
    ]

    trade_prints_match = [
        {'timestamp': 1000, 'price': 100.0, 'size': 10},
        {'timestamp': 1005, 'price': 101.0, 'size': 5}
    ]

    trade_prints_mismatch_ts = [
        {'timestamp': 1000, 'price': 100.0, 'size': 10},
        {'timestamp': 1006, 'price': 101.0, 'size': 5}
    ]

    trade_prints_mismatch_price = [
        {'timestamp': 1000, 'price': 100.0, 'size': 10},
        {'timestamp': 1005, 'price': 102.0, 'size': 5}
    ]

    trade_prints_mismatch_size = [
        {'timestamp': 1000, 'price': 100.0, 'size': 10},
        {'timestamp': 1005, 'price': 101.0, 'size': 6}
    ]

    trade_prints_mismatch_count = [
        {'timestamp': 1000, 'price': 100.0, 'size': 10}
    ]

    assert engine.verify_against_trade_prints(executions, trade_prints_match) == True
    assert engine.verify_against_trade_prints(executions, trade_prints_mismatch_ts) == False
    assert engine.verify_against_trade_prints(executions, trade_prints_mismatch_price) == False
    assert engine.verify_against_trade_prints(executions, trade_prints_mismatch_size) == False
    assert engine.verify_against_trade_prints(executions, trade_prints_mismatch_count) == False
