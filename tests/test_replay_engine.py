import pytest
from src.replay_engine import HistoricalReplayEngine

def test_stream_merges_chronologically():
    feed1 = [
        {"timestamp": 1.0, "type": "order", "id": 1},
        {"timestamp": 3.5, "type": "cancel", "id": 1},
        {"timestamp": 4.1, "type": "order", "id": 3},
    ]

    feed2 = [
        {"timestamp": 0.5, "type": "order", "id": 2},
        {"timestamp": 3.0, "type": "cancel", "id": 2},
        {"timestamp": 5.0, "type": "order", "id": 4},
    ]

    engine = HistoricalReplayEngine()
    engine.add_feed("NYSE", feed1)
    engine.add_feed("NASDAQ", feed2)

    streamed = list(engine.stream())

    # Check total length
    assert len(streamed) == 6

    # Check chronological order
    expected_order = [
        ("NASDAQ", feed2[0]), # 0.5
        ("NYSE", feed1[0]),   # 1.0
        ("NASDAQ", feed2[1]), # 3.0
        ("NYSE", feed1[1]),   # 3.5
        ("NYSE", feed1[2]),   # 4.1
        ("NASDAQ", feed2[2]), # 5.0
    ]

    assert streamed == expected_order

def test_stream_handles_equal_timestamps():
    feed1 = [
        {"timestamp": 1.0, "data": "A"},
    ]
    feed2 = [
        {"timestamp": 1.0, "data": "B"},
    ]

    engine = HistoricalReplayEngine()
    engine.add_feed("EX1", feed1)
    engine.add_feed("EX2", feed2)

    streamed = list(engine.stream())

    assert len(streamed) == 2
    assert streamed[0][1]['timestamp'] == 1.0
    assert streamed[1][1]['timestamp'] == 1.0

def test_verify_against_trade_prints():
    engine = HistoricalReplayEngine()

    sim_trades = [
        {"price": 100.5, "quantity": 10, "side": "buy", "internal_id": "a"},
        {"price": 101.0, "quantity": 5, "side": "sell", "internal_id": "b"},
    ]

    historical_prints = [
        {"price": 100.5, "quantity": 10, "side": "buy", "trade_id": "T1"},
        {"price": 101.0, "quantity": 5, "side": "sell", "trade_id": "T2"},
    ]

    assert engine.verify_against_trade_prints(sim_trades, historical_prints) == True

    # Test mismatch price
    bad_price_sim = [
        {"price": 100.5, "quantity": 10, "side": "buy"},
        {"price": 102.0, "quantity": 5, "side": "sell"},
    ]
    assert engine.verify_against_trade_prints(bad_price_sim, historical_prints) == False

    # Test mismatch length
    short_sim = [
        {"price": 100.5, "quantity": 10, "side": "buy"},
    ]
    assert engine.verify_against_trade_prints(short_sim, historical_prints) == False
