import pytest
from src.replay_engine import HistoricalReplayEngine

def test_chronological_alignment():
    engine = HistoricalReplayEngine()

    feed1 = [
        {"timestamp": 1000, "type": "order", "price": 100.5},
        {"timestamp": 1005, "type": "cancel", "price": 100.5},
        {"timestamp": 1010, "type": "order", "price": 101.0}
    ]

    feed2 = [
        {"timestamp": 1002, "type": "order", "price": 100.6},
        {"timestamp": 1008, "type": "execute", "price": 100.6}
    ]

    engine.load_feed("feed_A", feed1)
    engine.load_feed("feed_B", feed2)

    streamed_messages = list(engine.stream_messages())

    timestamps = [msg["timestamp"] for msg in streamed_messages]

    assert timestamps == [1000, 1002, 1005, 1008, 1010], "Messages are not chronologically aligned."

def test_verify_against_trade_prints_success():
    engine = HistoricalReplayEngine()

    historical_prints = [
        {"timestamp": 1000, "price": 100.5, "qty": 10},
        {"timestamp": 1008, "price": 100.6, "qty": 5}
    ]

    engine.load_trade_prints(historical_prints)

    simulated_executions = [
        {"timestamp": 1000, "price": 100.5, "qty": 10, "type": "execute"},
        {"timestamp": 1008, "price": 100.6, "qty": 5, "type": "execute"}
    ]

    assert engine.verify_against_trade_prints(simulated_executions) == True

def test_verify_against_trade_prints_failure():
    engine = HistoricalReplayEngine()

    historical_prints = [
        {"timestamp": 1000, "price": 100.5, "qty": 10},
        {"timestamp": 1008, "price": 100.6, "qty": 5}
    ]

    engine.load_trade_prints(historical_prints)

    simulated_executions = [
        {"timestamp": 1000, "price": 100.5, "qty": 10, "type": "execute"},
        {"timestamp": 1008, "price": 100.7, "qty": 5, "type": "execute"}  # Price mismatch
    ]

    assert engine.verify_against_trade_prints(simulated_executions) == False

def test_verify_against_trade_prints_length_mismatch():
    engine = HistoricalReplayEngine()

    historical_prints = [
        {"timestamp": 1000, "price": 100.5, "qty": 10}
    ]

    engine.load_trade_prints(historical_prints)

    simulated_executions = [
        {"timestamp": 1000, "price": 100.5, "qty": 10, "type": "execute"},
        {"timestamp": 1008, "price": 100.6, "qty": 5, "type": "execute"}
    ]

    assert engine.verify_against_trade_prints(simulated_executions) == False
