import os

class HTMLReportGenerator:
    def __init__(self, output_path="report.html"):
        self.output_path = output_path

    def _generate_ascii_curve(self, data: list[float], height: int = 15, width: int = 80) -> str:
        if not data:
            return ""

        min_val = min(data)
        max_val = max(data)

        if max_val == min_val:
            return "\n".join([" " * width] * (height // 2) + ["-" * width] + [" " * width] * (height - height // 2 - 1))

        # simple ascii plot
        plot = [[" " for _ in range(width)] for _ in range(height)]

        for i in range(width):
            data_idx = int(i / (width - 1) * (len(data) - 1)) if width > 1 else 0
            val = data[data_idx]

            y = int((val - min_val) / (max_val - min_val) * (height - 1))
            # Invert y because index 0 is top
            y = height - 1 - y

            plot[y][i] = "*"

        return "\n".join("".join(row) for row in plot)

    def generate(self, metrics: dict, equity_curve: list[float]) -> str:
        ascii_curve = self._generate_ascii_curve(equity_curve)

        metrics_rows = ""
        for key, value in metrics.items():
            metrics_rows += f"<tr><td>{key}</td><td>{value}</td></tr>\n"

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Backtest Report</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
        pre {{ background-color: #222; color: #0f0; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Backtest Report</h1>

    <h2>Metrics</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        {metrics_rows}
    </table>

    <h2>Equity Curve</h2>
    <pre>
{ascii_curve}
    </pre>
</body>
</html>"""

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return self.output_path
