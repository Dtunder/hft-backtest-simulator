# 📊 HFT Backtest Simulator
*Event-Driven Tick-Level Historical Simulation Suite*

> [!NOTE]
> This module manages event-driven backtesting using historical tick-level datasets, calculating critical mechatronic evaluation metrics (Sharpe ratio, drawdowns, win rate, and total yield).

## 📊 Backtester Engine
- **Event-Driven Loop:** Simulates incoming raw market ticks exactly as if they are live WebSocket events.
- **Precision Matching:** Executes limit and market orders using simulated historical bid/ask order book depth.
- **Statistical Analytics:** Compares strategy yield vs. baseline buy-and-hold returns.

---

## ⚡ Execution Instructions
To run a backtest simulation on historical tick-level dummy data:
```bash
python src/backtester.py
```
