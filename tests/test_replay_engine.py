import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from replay_engine import HistoricalReplayEngine

def test_stream_messages_chronological_alignment():
    engine = HistoricalReplayEngine()
    feed1 = [
        (10.5, "ORDER", {}),
        (12.1, "EXEC", {}),
        (15.0, "CANCEL", {})
    ]
    feed2 = [
        (10.2, "ORDER", {}),
        (11.9, "ORDER", {}),
        (16.5, "EXEC", {})
    ]
    engine.load_feed("EXCH_1", feed1)
    engine.load_feed("EXCH_2", feed2)

    messages = list(engine.stream_messages())
    expected_timestamps = [10.2, 10.5, 11.9, 12.1, 15.0, 16.5]
    actual_timestamps = [msg[0] for msg in messages]

    assert actual_timestamps == expected_timestamps, "Messages should be strictly chronologically aligned"

def test_verify_against_trade_prints():
    engine = HistoricalReplayEngine()
    executions = [
        (12.1, "EXEC", {"price": 100, "qty": 10}),
        (16.5, "EXEC", {"price": 101, "qty": 5})
    ]
    trade_prints_match = [
        (12.1, "EXEC", {"price": 100, "qty": 10}),
        (16.5, "EXEC", {"price": 101, "qty": 5})
    ]
    trade_prints_mismatch = [
        (12.1, "EXEC", {"price": 100, "qty": 10}),
        (16.5, "EXEC", {"price": 101, "qty": 6})
    ]

    assert engine.verify_against_trade_prints(executions, trade_prints_match) is True
    assert engine.verify_against_trade_prints(executions, trade_prints_mismatch) is False
