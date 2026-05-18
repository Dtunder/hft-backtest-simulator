import heapq
from typing import List, Dict, Any, Generator, Iterable

class HistoricalReplayEngine:
    """
    Ultra-performance replay system that streams historical L3 message logs
    (orders, cancels, executions) through the simulator. Uses K-way merge
    to align sub-microsecond timestamps across multiple exchange feeds.
    """

    def __init__(self):
        self.feeds = []

    def add_feed(self, feed: Iterable[Dict[str, Any]]):
        """
        Adds an L3 message feed. The feed can be any iterable of dictionaries
        (e.g., a generator, list).
        Messages must be dictionaries with at least a 'timestamp' key.
        """
        self.feeds.append(feed)

    def stream_messages(self) -> Generator[Dict[str, Any], None, None]:
        """
        Streams messages from multiple feeds in chronological order using
        a K-way merge based on sub-microsecond timestamps.
        """
        pq = []
        iters = [iter(f) for f in self.feeds]

        for i, it in enumerate(iters):
            try:
                msg = next(it)
                # tuple is (timestamp, feed_index, message)
                heapq.heappush(pq, (msg['timestamp'], i, msg))
            except StopIteration:
                pass

        while pq:
            timestamp, feed_index, msg = heapq.heappop(pq)
            yield msg

            try:
                next_msg = next(iters[feed_index])
                heapq.heappush(pq, (next_msg['timestamp'], feed_index, next_msg))
            except StopIteration:
                pass

    def verify_against_trade_prints(self, executions: List[Dict[str, Any]], trade_prints: List[Dict[str, Any]]) -> bool:
        """
        Verifies that our simulated executions match the historical trade prints.
        Executions and trade_prints should both be lists of dictionaries containing
        matching characteristics.
        """
        if len(executions) != len(trade_prints):
            return False

        for exec_msg, print_msg in zip(executions, trade_prints):
            if exec_msg.get('price') != print_msg.get('price') or \
               exec_msg.get('size') != print_msg.get('size') or \
               exec_msg.get('symbol') != print_msg.get('symbol'):
                return False

        return True
