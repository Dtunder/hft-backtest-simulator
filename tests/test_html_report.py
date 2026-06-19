import os
import pytest
from src.html_report import HTMLReportGenerator

def test_html_report_generator():
    generator = HTMLReportGenerator("test_report.html")
    metrics = {"Sharpe": 1.5, "Max Drawdown": "-5.0%"}
    equity_curve = [100.0, 102.0, 101.5, 105.0]

    output_path = generator.generate(metrics, equity_curve)

    assert output_path == "test_report.html"
    assert os.path.exists(output_path)

    with open(output_path, "r") as f:
        content = f.read()

    assert "<title>Backtest Report</title>" in content
    assert "<td>Sharpe</td><td>1.5</td>" in content
    assert "<td>Max Drawdown</td><td>-5.0%</td>" in content
    assert "<pre>" in content
    assert "</pre>" in content
    assert "*" in content  # Since equity curve is not flat

    os.remove(output_path)
