import os
from src.html_report import HTMLReportGenerator

def test_html_report_generation(tmp_path):
    generator = HTMLReportGenerator()

    metrics = {
        "Sharpe": "2.1",
        "Max Drawdown": "-5.4%",
        "Calmar": "1.5",
        "Win Rate": "55%",
        "PnL": "$12,000"
    }

    trade_log = [
        {"type": "BUY", "price": 100.5, "qty": 10, "pnl": ""},
        {"type": "SELL", "price": 102.5, "qty": 10, "pnl": "$20"}
    ]

    equity_curve = [1000, 1010, 1005, 1020, 1030, 1015, 1050]

    output_file = tmp_path / "test_report.html"

    generator.generate(metrics, trade_log, equity_curve, output_path=str(output_file))

    assert os.path.exists(output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<!DOCTYPE html>" in content
    assert "Sharpe Ratio" in content
    assert "2.1" in content
    assert "Max Drawdown" in content
    assert "-5.4%" in content
    assert "row-buy" in content
    assert "row-sell" in content
    assert "<pre>" in content
