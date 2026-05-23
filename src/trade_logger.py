import sqlite3
import datetime
import json
import os
import typing

class TradeLogger:
    def __init__(self, db_path='data/trades.db'):
        dir_name = os.path.dirname(db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        # Enable returning dicts for rows
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                qty REAL NOT NULL,
                pnl REAL,
                capital_after REAL NOT NULL,
                signal TEXT,
                obi REAL,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT PRIMARY KEY,
                starting_capital REAL,
                ending_capital REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                total_pnl REAL,
                max_drawdown_pct REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equity_curve (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                equity REAL NOT NULL,
                capital REAL NOT NULL,
                position_qty REAL NOT NULL
            )
        ''')

        self.conn.commit()

    def log_trade(self, symbol: str, side: str, price: float, qty: float,
                  capital_after: float, pnl: float = None,
                  signal: str = None, obi: float = None, notes: dict = None):
        cursor = self.conn.cursor()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        notes_str = json.dumps(notes) if notes is not None else None

        cursor.execute('''
            INSERT INTO trades (
                timestamp, symbol, side, price, qty, pnl, capital_after, signal, obi, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, symbol, side, price, qty, pnl, capital_after, signal, obi, notes_str))
        self.conn.commit()

    def log_equity(self, equity: float, capital: float, position_qty: float):
        cursor = self.conn.cursor()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor.execute('''
            INSERT INTO equity_curve (timestamp, equity, capital, position_qty)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, equity, capital, position_qty))
        self.conn.commit()

    def update_daily_summary(self, date: str, starting_capital: float,
                             ending_capital: float, total_trades: int,
                             winning_trades: int, total_pnl: float,
                             max_drawdown_pct: float):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summary (
                date, starting_capital, ending_capital, total_trades,
                winning_trades, total_pnl, max_drawdown_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, starting_capital, ending_capital, total_trades, winning_trades, total_pnl, max_drawdown_pct))
        self.conn.commit()

    def get_daily_summary(self, date: str) -> typing.Optional[dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM daily_summary WHERE date = ?', (date,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def export_equity_curve(self) -> typing.List[dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM equity_curve ORDER BY id')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_trade_count(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM trades')
        return cursor.fetchone()[0]

    def close(self):
        self.conn.commit()
        self.conn.close()

if __name__ == '__main__':
    logger = TradeLogger(db_path='data/test_trades.db')

    # Log 3 fake trades (2 BUY, 1 SELL with PnL)
    logger.log_trade(symbol='BTCUSD', side='BUY', price=50000.0, qty=1.0, capital_after=50000.0, signal='BUY', notes={'reason': 'macd'})
    logger.log_trade(symbol='ETHUSD', side='BUY', price=3000.0, qty=5.0, capital_after=35000.0)
    logger.log_trade(symbol='BTCUSD', side='SELL', price=51000.0, qty=1.0, capital_after=86000.0, pnl=1000.0, obi=0.8)

    # Log 5 equity points
    logger.log_equity(equity=100000.0, capital=100000.0, position_qty=0.0)
    logger.log_equity(equity=100000.0, capital=50000.0, position_qty=1.0)
    logger.log_equity(equity=101000.0, capital=50000.0, position_qty=1.0)
    logger.log_equity(equity=101000.0, capital=86000.0, position_qty=0.0)
    logger.log_equity(equity=102000.0, capital=86000.0, position_qty=0.0)

    # Export and print equity curve
    curve = logger.export_equity_curve()
    print("Equity Curve:")
    for point in curve:
        print(point)

    # Print trade count
    print(f"Total trades: {logger.get_trade_count()}")

    logger.close()
