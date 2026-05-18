from src.replay_engine import HistoricalReplayEngine

def test_stream_merged_ticks():
    engine = HistoricalReplayEngine()

    feed1 = [
        {"timestamp": 10.1, "msg": "A"},
        {"timestamp": 10.3, "msg": "B"},
        {"timestamp": 10.5, "msg": "C"}
    ]

    feed2 = [
        {"timestamp": 10.2, "msg": "D"},
        {"timestamp": 10.4, "msg": "E"}
    ]

    engine.load_feed(feed1)
    engine.load_feed(feed2)

    merged = list(engine.stream_merged_ticks())

    assert len(merged) == 5
    assert merged[0]["msg"] == "A"
    assert merged[1]["msg"] == "D"
    assert merged[2]["msg"] == "B"
    assert merged[3]["msg"] == "E"
    assert merged[4]["msg"] == "C"

def test_stream_merged_ticks_same_timestamp():
    engine = HistoricalReplayEngine()

    feed1 = [
        {"timestamp": 10.1, "msg": "A"}
    ]

    feed2 = [
        {"timestamp": 10.1, "msg": "B"}
    ]

    engine.load_feed(feed1)
    engine.load_feed(feed2)

    merged = list(engine.stream_merged_ticks())
    assert len(merged) == 2
    assert merged[0]["timestamp"] == 10.1
    assert merged[1]["timestamp"] == 10.1
    # order may depend on insertion index, which is handled correctly by heapq tuple

def test_verify_against_trade_prints_success():
    engine = HistoricalReplayEngine()

    sim = [{"price": 100, "qty": 10}, {"price": 101, "qty": 5}]
    hist = [{"price": 100, "qty": 10}, {"price": 101, "qty": 5}]

    assert engine.verify_against_trade_prints(sim, hist) is True

def test_verify_against_trade_prints_fail_length():
    engine = HistoricalReplayEngine()

    sim = [{"price": 100, "qty": 10}]
    hist = [{"price": 100, "qty": 10}, {"price": 101, "qty": 5}]

    assert engine.verify_against_trade_prints(sim, hist) is False

def test_verify_against_trade_prints_fail_value():
    engine = HistoricalReplayEngine()

    sim = [{"price": 100, "qty": 10}]
    hist = [{"price": 100, "qty": 15}]

    assert engine.verify_against_trade_prints(sim, hist) is False
