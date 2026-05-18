import pytest
from src.replay_engine import HistoricalReplayEngine

def test_k_way_merge():
    engine = HistoricalReplayEngine()
    feed1 = [(1000, "ORDER", {"price": 10}), (1005, "EXEC", {"price": 10})]
    feed2 = [(999, "ORDER", {"price": 9}), (1001, "CANCEL", {"id": 1})]
    feed3 = [(1003, "ORDER", {"price": 11})]

    engine.load_feed("FEED1", feed1)
    engine.load_feed("FEED2", feed2)
    engine.load_feed("FEED3", feed3)

    stream = list(engine.stream_messages())
    expected = [
        (999, "ORDER", {"price": 9}),
        (1000, "ORDER", {"price": 10}),
        (1001, "CANCEL", {"id": 1}),
        (1003, "ORDER", {"price": 11}),
        (1005, "EXEC", {"price": 10}),
    ]

    assert stream == expected

def test_verify_against_trade_prints():
    engine = HistoricalReplayEngine()

    trade_prints = [
        (1000, 10.0, 100),
        (1005, 10.5, 50),
        (1010, 10.2, 200)
    ]
    engine.load_trade_prints(trade_prints)

    # Matching trades but out of order
    simulated_trades = [
        (1010, 10.2, 200),
        (1000, 10.0, 100),
        (1005, 10.5, 50)
    ]
    assert engine.verify_against_trade_prints(simulated_trades) == True

    # Missing trade
    simulated_trades_missing = [
        (1000, 10.0, 100),
        (1005, 10.5, 50)
    ]
    assert engine.verify_against_trade_prints(simulated_trades_missing) == False

    # Mismatched price
    simulated_trades_mismatched = [
        (1000, 10.0, 100),
        (1005, 11.5, 50),
        (1010, 10.2, 200)
    ]
    assert engine.verify_against_trade_prints(simulated_trades_mismatched) == False
