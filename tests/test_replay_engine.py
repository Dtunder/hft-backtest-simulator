import pytest
from src.replay_engine import HistoricalReplayEngine

def test_replay_engine_stream_alignment():
    engine = HistoricalReplayEngine()

    feed1 = [
        (1.0, 'EXC1', 'ORDER', {'id': 1}),
        (1.5, 'EXC1', 'CANCEL', {'id': 1}),
        (2.0, 'EXC1', 'ORDER', {'id': 3}),
    ]

    feed2 = [
        (0.5, 'EXC2', 'ORDER', {'id': 2}),
        (1.2, 'EXC2', 'EXEC', {'id': 2}),
    ]

    feed3 = [
        (1.2, 'EXC3', 'ORDER', {'id': 4}), # Same timestamp as feed2's exec
    ]

    engine.add_feed(feed1)
    engine.add_feed(feed2)
    engine.add_feed(feed3)

    streamed = list(engine.stream())

    assert len(streamed) == 6
    assert streamed[0] == (0.5, 'EXC2', 'ORDER', {'id': 2})
    assert streamed[1] == (1.0, 'EXC1', 'ORDER', {'id': 1})

    # 1.2 timestamp from feed2 and feed3
    assert streamed[2][0] == 1.2
    assert streamed[3][0] == 1.2

    assert streamed[4] == (1.5, 'EXC1', 'CANCEL', {'id': 1})
    assert streamed[5] == (2.0, 'EXC1', 'ORDER', {'id': 3})


def test_verify_against_trade_prints_success():
    engine = HistoricalReplayEngine()

    executions = [
        (1.0, 'EXEC', 100),
        (1.5, 'EXEC', 50),
        (2.0, 'EXEC', 200)
    ]

    trade_prints = [
        (1.0, 'EXEC', 100),
        (1.5, 'EXEC', 50),
        (2.0, 'EXEC', 200)
    ]

    assert engine.verify_against_trade_prints(executions, trade_prints) == True


def test_verify_against_trade_prints_failure_mismatch():
    engine = HistoricalReplayEngine()

    executions = [
        (1.0, 'EXEC', 100),
        (1.5, 'EXEC', 50),
        (2.0, 'EXEC', 200)
    ]

    trade_prints = [
        (1.0, 'EXEC', 100),
        (1.6, 'EXEC', 50), # Mismatch
        (2.0, 'EXEC', 200)
    ]

    assert engine.verify_against_trade_prints(executions, trade_prints) == False


def test_verify_against_trade_prints_failure_length():
    engine = HistoricalReplayEngine()

    executions = [
        (1.0, 'EXEC', 100),
        (1.5, 'EXEC', 50),
    ]

    trade_prints = [
        (1.0, 'EXEC', 100),
        (1.5, 'EXEC', 50),
        (2.0, 'EXEC', 200)
    ]

    assert engine.verify_against_trade_prints(executions, trade_prints) == False
