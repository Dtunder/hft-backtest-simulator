import pytest
from src.replay_engine import HistoricalReplayEngine

def test_k_way_merge():
    engine = HistoricalReplayEngine()

    feed1 = [
        {'timestamp': 1000.5, 'msg': 'A1'},
        {'timestamp': 1002.1, 'msg': 'A2'},
        {'timestamp': 1005.0, 'msg': 'A3'}
    ]

    feed2 = [
        {'timestamp': 1001.0, 'msg': 'B1'},
        {'timestamp': 1001.5, 'msg': 'B2'},
        {'timestamp': 1004.0, 'msg': 'B3'}
    ]

    feed3 = [
        {'timestamp': 1000.1, 'msg': 'C1'},
        {'timestamp': 1003.0, 'msg': 'C2'}
    ]

    engine.add_feed(feed1)
    engine.add_feed(feed2)
    engine.add_feed(feed3)

    merged = list(engine.stream_messages())

    assert len(merged) == 8
    assert merged[0]['msg'] == 'C1'
    assert merged[1]['msg'] == 'A1'
    assert merged[2]['msg'] == 'B1'
    assert merged[3]['msg'] == 'B2'
    assert merged[4]['msg'] == 'A2'
    assert merged[5]['msg'] == 'C2'
    assert merged[6]['msg'] == 'B3'
    assert merged[7]['msg'] == 'A3'

def test_verify_against_trade_prints():
    engine = HistoricalReplayEngine()

    executions = [
        {'symbol': 'AAPL', 'price': 150.0, 'size': 100},
        {'symbol': 'MSFT', 'price': 250.0, 'size': 50}
    ]

    trade_prints_match = [
        {'symbol': 'AAPL', 'price': 150.0, 'size': 100},
        {'symbol': 'MSFT', 'price': 250.0, 'size': 50}
    ]

    trade_prints_mismatch_price = [
        {'symbol': 'AAPL', 'price': 150.0, 'size': 100},
        {'symbol': 'MSFT', 'price': 250.5, 'size': 50}
    ]

    trade_prints_mismatch_size = [
        {'symbol': 'AAPL', 'price': 150.0, 'size': 100},
        {'symbol': 'MSFT', 'price': 250.0, 'size': 51}
    ]

    trade_prints_mismatch_len = [
        {'symbol': 'AAPL', 'price': 150.0, 'size': 100}
    ]

    assert engine.verify_against_trade_prints(executions, trade_prints_match) == True
    assert engine.verify_against_trade_prints(executions, trade_prints_mismatch_price) == False
    assert engine.verify_against_trade_prints(executions, trade_prints_mismatch_size) == False
    assert engine.verify_against_trade_prints(executions, trade_prints_mismatch_len) == False
