import heapq
from typing import Iterable, Dict, Any, Generator, Tuple

class HistoricalReplayEngine:
    """
    Sub-microsecond timestamp alignment replay engine for multiple historical L3 message feeds.
    """
    def __init__(self):
        self.feeds = []

    def add_feed(self, exchange: str, feed_iterator: Iterable[Dict[str, Any]]):
        """
        Add a feed generator/iterator for a specific exchange.
        Each message in the feed should be a dictionary with a 'timestamp' key (sub-microsecond precision).
        """
        iterator = iter(feed_iterator)
        try:
            first_msg = next(iterator)
            # Tuple: (timestamp, counter, exchange, msg, iterator)
            # Use a counter to prevent comparing dictionaries if timestamps are equal
            counter = len(self.feeds)
            heapq.heappush(self.feeds, (first_msg['timestamp'], counter, exchange, first_msg, iterator))
        except StopIteration:
            pass

    def stream(self) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
        """
        Generator that yields messages from all feeds in chronological order.
        Yields (exchange, message).
        """
        while self.feeds:
            timestamp, counter, exchange, msg, iterator = heapq.heappop(self.feeds)

            yield exchange, msg

            try:
                next_msg = next(iterator)
                heapq.heappush(self.feeds, (next_msg['timestamp'], counter, exchange, next_msg, iterator))
            except StopIteration:
                pass

    def verify_against_trade_prints(self, simulated_trades: Iterable[Dict[str, Any]], historical_prints: Iterable[Dict[str, Any]]) -> bool:
        """
        Verify correctness of simulated trades against historical trade prints.
        Returns True if they match, False otherwise.
        """
        sim_iter = iter(simulated_trades)
        hist_iter = iter(historical_prints)

        while True:
            try:
                sim = next(sim_iter)
            except StopIteration:
                sim = None

            try:
                hist = next(hist_iter)
            except StopIteration:
                hist = None

            if sim is None and hist is None:
                return True
            if sim is None or hist is None:
                return False

            # Check basic trade attributes: price, quantity, side
            if sim.get('price') != hist.get('price'):
                return False
            if sim.get('quantity') != hist.get('quantity'):
                return False
            if sim.get('side') != hist.get('side'):
                return False

        return True
