import math
import statistics
import random

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

if __name__ == "__main__":
    random.seed(42)

    # Generate fake equity curve
    equity_curve = [1000.0]
    for _ in range(251):
        # trending up slightly with noise
        change = random.normalvariate(0.0005, 0.01)
        next_value = equity_curve[-1] * (1 + change)
        equity_curve.append(next_value)

    # Generate 50 fake PnL values
    pnl_list = [random.normalvariate(10, 50) for _ in range(50)]

    metrics = PerformanceMetrics()
    report = metrics.full_report(equity_curve, pnl_list)

    print("Performance Report:")
    for key, value in report.items():
        print(f"{key}: {value}")
