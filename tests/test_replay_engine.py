import pytest
from src.replay_engine import HistoricalReplayEngine

def test_stream_historical_l3_messages():
    engine = HistoricalReplayEngine()

    feed_a = [
        (1.0, "FEED_A", {"type": "ORDER", "price": 100.5, "qty": 10}),
        (1.5, "FEED_A", {"type": "EXECUTION", "price": 100.5, "qty": 5}),
        (2.0, "FEED_A", {"type": "CANCEL", "price": 100.5, "qty": 5})
    ]

    feed_b = [
        (0.8, "FEED_B", {"type": "ORDER", "price": 100.4, "qty": 15}),
        (1.2, "FEED_B", {"type": "ORDER", "price": 100.6, "qty": 20}),
        (1.8, "FEED_B", {"type": "EXECUTION", "price": 100.6, "qty": 20})
    ]

    engine.load_feed("FEED_A", feed_a)
    engine.load_feed("FEED_B", feed_b)

    streamed_messages = list(engine.stream_historical_l3_messages())

    assert len(streamed_messages) == 6
    assert streamed_messages[0][0] == 0.8
    assert streamed_messages[1][0] == 1.0
    assert streamed_messages[2][0] == 1.2
    assert streamed_messages[3][0] == 1.5
    assert streamed_messages[4][0] == 1.8
    assert streamed_messages[5][0] == 2.0

def test_verify_against_trade_prints():
    engine = HistoricalReplayEngine()

    simulated_trades = [
        (1.5, "FEED_A", {"type": "EXECUTION", "price": 100.5, "qty": 5}),
        (1.8, "FEED_B", {"type": "EXECUTION", "price": 100.6, "qty": 20})
    ]

    historical_trade_prints = [
        (1.5, "FEED_A", {"type": "EXECUTION", "price": 100.5, "qty": 5}),
        (1.8, "FEED_B", {"type": "EXECUTION", "price": 100.6, "qty": 20})
    ]

    assert engine.verify_against_trade_prints(simulated_trades, historical_trade_prints) == True

    mismatched_historical_trade_prints = [
        (1.5, "FEED_A", {"type": "EXECUTION", "price": 100.5, "qty": 5})
    ]

    assert engine.verify_against_trade_prints(simulated_trades, mismatched_historical_trade_prints) == False
