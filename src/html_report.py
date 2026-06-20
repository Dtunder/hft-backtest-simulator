class HTMLReportGenerator:
    """
    Generates a single-file HTML report for backtest results.
    """

    def _generate_sparkline(self, equity_curve):
        """
        Generates an ASCII sparkline from the equity curve.
        """
        if not equity_curve:
            return ""

        chars = " ▂▃▄▅▆▇█"
        min_val = min(equity_curve)
        max_val = max(equity_curve)
        range_val = max_val - min_val

        if range_val == 0:
            return chars[0] * len(equity_curve)

        sparkline = ""
        for val in equity_curve:
            normalized = (val - min_val) / range_val
            idx = int(normalized * (len(chars) - 1))
            sparkline += chars[idx]

        return sparkline

    def generate(self, metrics, trade_log, equity_curve, output_path="report.html"):
        """
        Writes the HTML report to output_path.

        metrics: dict with keys Sharpe, Max Drawdown, Calmar, Win Rate, PnL
        trade_log: list of dicts with keys 'type' (BUY/SELL), 'price', 'qty', 'pnl' (optional)
        equity_curve: list of floats
        """
        sparkline = self._generate_sparkline(equity_curve)

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>HFT Backtest Report</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        background-color: #f4f4f9;
        color: #333;
        margin: 40px;
    }}
    .container {{
        background: #fff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    h1 {{
        color: #2c3e50;
    }}
    .metrics-board {{
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
    }}
    .metric {{
        background: #e2e8f0;
        padding: 15px;
        border-radius: 6px;
        flex: 1;
        text-align: center;
    }}
    .metric-title {{
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .metric-value {{
        font-size: 24px;
        font-weight: bold;
        color: #1e293b;
        margin-top: 5px;
    }}
    .sparkline-container {{
        background: #1e293b;
        color: #10b981;
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 20px;
        overflow-x: auto;
    }}
    pre {{
        margin: 0;
        font-size: 16px;
        letter-spacing: 2px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }}
    th, td {{
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #cbd5e1;
    }}
    th {{
        background-color: #f8fafc;
        color: #475569;
    }}
    .row-buy {{
        background-color: #ecfdf5;
    }}
    .row-sell {{
        background-color: #fef2f2;
    }}
</style>
</head>
<body>
<div class="container">
    <h1>HFT Backtest Report</h1>

    <div class="metrics-board">
        <div class="metric">
            <div class="metric-title">Sharpe Ratio</div>
            <div class="metric-value">{metrics.get('Sharpe', 'N/A')}</div>
        </div>
        <div class="metric">
            <div class="metric-title">Max Drawdown</div>
            <div class="metric-value">{metrics.get('Max Drawdown', 'N/A')}</div>
        </div>
        <div class="metric">
            <div class="metric-title">Calmar Ratio</div>
            <div class="metric-value">{metrics.get('Calmar', 'N/A')}</div>
        </div>
        <div class="metric">
            <div class="metric-title">Win Rate</div>
            <div class="metric-value">{metrics.get('Win Rate', 'N/A')}</div>
        </div>
        <div class="metric">
            <div class="metric-title">Total PnL</div>
            <div class="metric-value">{metrics.get('PnL', 'N/A')}</div>
        </div>
    </div>

    <h2>Equity Curve</h2>
    <div class="sparkline-container">
        <pre>{sparkline}</pre>
    </div>

    <h2>Trade Log</h2>
    <table>
        <thead>
            <tr>
                <th>Type</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>PnL</th>
            </tr>
        </thead>
        <tbody>
"""
        for trade in trade_log:
            trade_type = trade.get('type', '')
            row_class = 'row-buy' if trade_type.upper() == 'BUY' else 'row-sell' if trade_type.upper() == 'SELL' else ''

            html += f"""            <tr class="{row_class}">
                <td>{trade_type}</td>
                <td>{trade.get('price', '')}</td>
                <td>{trade.get('qty', '')}</td>
                <td>{trade.get('pnl', '')}</td>
            </tr>
"""
        html += """        </tbody>
    </table>
</div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Report generated at {output_path}")
