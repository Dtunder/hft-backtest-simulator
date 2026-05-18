import pytest
from src.replay_engine import HistoricalReplayEngine

def test_kway_merge():
    feed1 = [{'timestamp': 1.0, 'data': 'A'}, {'timestamp': 3.0, 'data': 'C'}]
    feed2 = [{'timestamp': 2.0, 'data': 'B'}, {'timestamp': 4.0, 'data': 'D'}]

    engine = HistoricalReplayEngine()
    result = list(engine.stream_feeds([feed1, feed2]))

    assert [m['data'] for m in result] == ['A', 'B', 'C', 'D']

def test_verify_against_trade_prints():
    engine = HistoricalReplayEngine()
    simulated = [{'id': 1}, {'id': 2}]
    historic = [{'id': 1}, {'id': 2}]

    assert engine.verify_against_trade_prints(simulated, historic) is True

    historic_wrong = [{'id': 1}, {'id': 3}]
    assert engine.verify_against_trade_prints(simulated, historic_wrong) is False

    historic_len = [{'id': 1}]
    assert engine.verify_against_trade_prints(simulated, historic_len) is False
