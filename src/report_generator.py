import math
import statistics
import random
import os
import datetime

class PerformanceMetrics:
    def __init__(self, risk_free_rate_annual: float = 0.04):
        self.risk_free_rate_annual = risk_free_rate_annual
        self.risk_free_rate_daily = (1 + risk_free_rate_annual) ** (1/252) - 1

    def calculate_returns(self, equity_curve: list) -> list:
        if not equity_curve or len(equity_curve) < 2:
            return []
        return [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] for i in range(1, len(equity_curve))]

    def sharpe_ratio(self, equity_curve: list, periods_per_year: int = 252) -> float:
        returns = self.calculate_returns(equity_curve)
        if len(returns) < 2:
            return 0.0

        excess_returns = [r - self.risk_free_rate_daily for r in returns]
        try:
            stdev = statistics.stdev(excess_returns)
            if stdev == 0:
                return 0.0
            sharpe = statistics.mean(excess_returns) / stdev * math.sqrt(periods_per_year)
            return round(sharpe, 4)
        except statistics.StatisticsError:
            return 0.0

    def sortino_ratio(self, equity_curve: list, periods_per_year: int = 252) -> float:
        returns = self.calculate_returns(equity_curve)
        if len(returns) < 2:
            return 0.0

        downside = [r for r in returns if r < self.risk_free_rate_daily]
        if not downside:
            return 0.0

        excess_returns = [r - self.risk_free_rate_daily for r in returns]
        downside_dev = statistics.stdev(downside) if len(downside) > 1 else abs(downside[0])

        if downside_dev == 0:
            return 0.0

        sortino = statistics.mean(excess_returns) / downside_dev * math.sqrt(periods_per_year)
        return sortino

    def max_drawdown(self, equity_curve: list) -> float:
        if not equity_curve or len(equity_curve) < 2:
            return 0.0

        mdd = 0.0
        peak = equity_curve[0]

        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > mdd:
                mdd = dd

        return mdd

    def calmar_ratio(self, equity_curve: list, periods_per_year: int = 252) -> float:
        if not equity_curve or len(equity_curve) < 2:
            return 0.0

        annual_return = (equity_curve[-1] / equity_curve[0]) ** (periods_per_year / len(equity_curve)) - 1
        mdd = self.max_drawdown(equity_curve)

        if mdd > 0:
            return annual_return / mdd
        return 0.0

    def win_rate(self, pnl_list: list) -> float:
        if not pnl_list:
            return 0.0
        wins = sum(1 for pnl in pnl_list if pnl > 0)
        return wins / len(pnl_list)

    def profit_factor(self, pnl_list: list) -> float:
        if not pnl_list:
            return 0.0
        gross_profit = sum(p for p in pnl_list if p > 0)
        gross_loss = abs(sum(p for p in pnl_list if p < 0))
        if gross_loss > 0:
            return gross_profit / gross_loss
        return 0.0

    def full_report(self, equity_curve: list, pnl_list: list = None) -> dict:
        if not equity_curve:
            return {}

        wr = self.win_rate(pnl_list) if pnl_list is not None else 0.0
        pf = self.profit_factor(pnl_list) if pnl_list is not None else 0.0

        return {
            "sharpe": self.sharpe_ratio(equity_curve),
            "sortino": self.sortino_ratio(equity_curve),
            "max_drawdown_pct": self.max_drawdown(equity_curve) * 100,
            "calmar": self.calmar_ratio(equity_curve),
            "win_rate": wr,
            "profit_factor": pf,
            "total_return_pct": (equity_curve[-1] / equity_curve[0] - 1) * 100,
            "num_periods": len(equity_curve)
        }

class BacktestReportGenerator:
    def __init__(self, report_dir: str = "reports"):
        self.report_dir = report_dir
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def ascii_equity_chart(self, equity_curve: list, width: int = 40, height: int = 20) -> str:
        if not equity_curve:
            return ""

        min_eq = min(equity_curve)
        max_eq = max(equity_curve)

        if max_eq == min_eq:
            max_eq += 1

        range_eq = max_eq - min_eq

        if len(equity_curve) > width:
            step = len(equity_curve) / width
            resampled = [equity_curve[int(i * step)] for i in range(width)]
        else:
            # Interpolate for better visualization if short
            resampled = []
            for i in range(width):
                if len(equity_curve) == 1:
                    resampled.append(equity_curve[0])
                    continue
                idx = i * (len(equity_curve) - 1) / (width - 1)
                idx_lower = int(math.floor(idx))
                idx_upper = int(math.ceil(idx))
                if idx_lower == idx_upper:
                    resampled.append(equity_curve[idx_lower])
                else:
                    weight = idx - idx_lower
                    val = equity_curve[idx_lower] * (1 - weight) + equity_curve[idx_upper] * weight
                    resampled.append(val)

        lines = []

        # Calculate max label width for proper alignment
        max_label_val = min_eq + ((height - 1 + 0.5) / height) * range_eq
        min_label_val = min_eq + (0.5 / height) * range_eq
        max_label_len = max(len(f"${max_label_val:,.0f}"), len(f"${min_label_val:,.0f}"))

        for row in range(height - 1, -1, -1):
            row_min_val = min_eq + (row / height) * range_eq
            label_val = min_eq + ((row + 0.5) / height) * range_eq

            # Right-align the label
            label = f"${label_val:,.0f}"
            padding = " " * (max_label_len - len(label))
            line = f"{padding}{label} | "

            for val in resampled:
                if val >= row_min_val:
                    line += "█"
                else:
                    line += " "
            lines.append(line)

        padding = " " * max_label_len
        lines.append(padding + "   " + "─" * width)

        return "\n".join(lines)

    def generate_html_report(self, backtest_results: dict, output_filename: str = None) -> str:
        symbol = backtest_results.get("symbol", "UNKNOWN")
        initial_capital = backtest_results.get("initial_capital", 0.0)
        final_capital = backtest_results.get("final_capital", 0.0)
        equity_curve = backtest_results.get("equity_curve", [])
        trades = backtest_results.get("trades", [])
        metrics = backtest_results.get("metrics", {})
        params = backtest_results.get("params", {})
        run_timestamp = backtest_results.get("run_timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())

        total_return_pct = metrics.get("total_return_pct", 0.0)
        if total_return_pct == 0.0 and initial_capital > 0:
            total_return_pct = ((final_capital / initial_capital) - 1) * 100

        sharpe = metrics.get("sharpe", 0.0)
        sortino = metrics.get("sortino", 0.0)
        max_dd = metrics.get("max_drawdown_pct", 0.0) / 100.0  # internal is pct, requirement specifies < 0.20
        win_rate = metrics.get("win_rate", 0.0)
        profit_factor = metrics.get("profit_factor", 0.0)

        if sharpe > 1.5 and max_dd < 0.20:
            verdict_class = "go"
            verdict_text = "GO &mdash; Strategy validated"
        elif sharpe > 1.0:
            verdict_class = "caution"
            verdict_text = "CAUTION &mdash; Strategy shows promise"
        else:
            verdict_class = "no-go"
            verdict_text = "NO-GO &mdash; Strategy needs improvement"

        ascii_chart = self.ascii_equity_chart(equity_curve)

        trades_html = ""
        for trade in trades[-20:]:
            pnl = trade.get("pnl", 0.0)
            row_class = "positive" if pnl >= 0 else "negative"
            trades_html += f'''
            <tr class="{row_class}">
                <td>{trade.get("side", "")}</td>
                <td>{trade.get("price", 0.0):.2f}</td>
                <td>{trade.get("qty", 0.0):.2f}</td>
                <td>{pnl:.2f}</td>
                <td>{trade.get("timestamp", "")}</td>
            </tr>
            '''

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Backtest Report - {symbol}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; color: #333; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .container {{ max-width: 1000px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header-summary {{ display: flex; justify-content: space-between; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .metric-card {{ background: #f1f2f6; padding: 15px; border-radius: 5px; text-align: center; }}
        .metric-card span {{ display: block; font-size: 12px; color: #7f8fa6; text-transform: uppercase; }}
        .metric-card strong {{ font-size: 20px; color: #2f3640; }}
        .ascii-chart {{ background: #2f3640; color: #f5f6fa; padding: 20px; border-radius: 5px; font-family: monospace; white-space: pre; overflow-x: auto; margin-bottom: 30px; line-height: 1.2; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f1f2f6; }}
        tr.positive {{ background-color: #e8f8f5; }}
        tr.negative {{ background-color: #fdedec; }}
        .verdict {{ padding: 20px; border-radius: 5px; text-align: center; font-size: 24px; font-weight: bold; margin-top: 20px; }}
        .go {{ background-color: #2ecc71; color: white; }}
        .caution {{ background-color: #f1c40f; color: #333; }}
        .no-go {{ background-color: #e74c3c; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-summary">
            <div>
                <h1>Backtest Report: {symbol}</h1>
                <p>Run Time: {run_timestamp}</p>
            </div>
            <div style="text-align: right;">
                <p>Initial Capital: <strong>${initial_capital:,.2f}</strong></p>
                <p>Final Capital: <strong>${final_capital:,.2f}</strong></p>
                <p>Total Return: <strong>{total_return_pct:.2f}%</strong></p>
            </div>
        </div>

        <h2>Key Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card"><span>Sharpe Ratio</span><strong>{sharpe:.2f}</strong></div>
            <div class="metric-card"><span>Sortino Ratio</span><strong>{sortino:.2f}</strong></div>
            <div class="metric-card"><span>Max Drawdown</span><strong>{metrics.get("max_drawdown_pct", 0.0):.2f}%</strong></div>
            <div class="metric-card"><span>Win Rate</span><strong>{win_rate*100:.1f}%</strong></div>
            <div class="metric-card"><span>Profit Factor</span><strong>{profit_factor:.2f}</strong></div>
        </div>

        <h2>Equity Curve</h2>
        <div class="ascii-chart">{ascii_chart}</div>

        <h2>Trade Log (Last 20)</h2>
        <table>
            <thead>
                <tr>
                    <th>Side</th>
                    <th>Price</th>
                    <th>Qty</th>
                    <th>PnL</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {trades_html}
            </tbody>
        </table>

        <h2>Verdict</h2>
        <div class="verdict {verdict_class}">
            {verdict_text}
        </div>
    </div>
</body>
</html>
'''
        if output_filename is None:
            timestamp_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_filename = f"backtest_report_{timestamp_str}.html"

        filepath = os.path.join(self.report_dir, output_filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return filepath

if __name__ == "__main__":
    # Generate fake backtest_results
    random.seed(42)

    # 500-point equity curve (GBM from 1000, trending slightly up)
    equity_curve = [1000.0]
    for _ in range(499):
        change = random.normalvariate(0.0002, 0.005)
        next_value = equity_curve[-1] * (1 + change)
        equity_curve.append(next_value)

    # 30 fake trades (mix of wins/losses)
    trades = []
    base_time = datetime.datetime.now(datetime.timezone.utc)
    for i in range(30):
        side = random.choice(["BUY", "SELL"])
        price = random.uniform(100, 200)
        qty = random.uniform(1, 10)
        # Mix of wins and losses
        pnl = random.normalvariate(5, 20)
        trade_time = base_time + datetime.timedelta(minutes=i*15)
        trades.append({
            "side": side,
            "price": price,
            "qty": qty,
            "pnl": pnl,
            "timestamp": trade_time.isoformat()
        })

    # metrics calculated from equity_curve
    metrics_calc = PerformanceMetrics()
    pnl_list = [t["pnl"] for t in trades]
    metrics = metrics_calc.full_report(equity_curve, pnl_list)

    backtest_results = {
        "symbol": "FAKE_BTC_USD",
        "initial_capital": 1000.0,
        "final_capital": equity_curve[-1],
        "equity_curve": equity_curve,
        "trades": trades,
        "metrics": metrics,
        "params": {"trend_period": 20, "vol_period": 14},
        "run_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    gen = BacktestReportGenerator()
    path = gen.generate_html_report(backtest_results)

    print(gen.ascii_equity_chart(equity_curve))
    print(f"\nReport saved to: {path}")