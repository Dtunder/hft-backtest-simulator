import heapq

class HistoricalReplayEngine:
    """
    Ultra-performance replay system that streams historical L3 message logs
    (orders, cancels, executions) through the simulator.
    """
    def __init__(self):
        self.feeds = []

    def load_feed(self, feed):
        """
        Loads a feed, which should be an iterable of dictionaries representing L3 messages.
        Each message must have a 'timestamp' key representing sub-microsecond time.
        """
        self.feeds.append(feed)

    def stream_merged_ticks(self):
        """
        Uses heapq for K-way merge to handle sub-microsecond timestamp alignment
        of multiple historical L3 message feeds chronologically.
        """
        iterators = [iter(feed) for feed in self.feeds]

        heap = []
        for i, it in enumerate(iterators):
            try:
                first_item = next(it)
                # Store (timestamp, index, item) to ensure items with same timestamp
                # are ordered by index, and to avoid comparing dicts directly.
                heapq.heappush(heap, (first_item['timestamp'], i, first_item))
            except StopIteration:
                pass

        while heap:
            timestamp, i, item = heapq.heappop(heap)
            yield item

            try:
                next_item = next(iterators[i])
                heapq.heappush(heap, (next_item['timestamp'], i, next_item))
            except StopIteration:
                pass

    def verify_against_trade_prints(self, simulated_trades, historical_prints):
        """
        Verifies correctness against historic trade prints.
        """
        if len(simulated_trades) != len(historical_prints):
            print(f"[REPLAY VERIFY] Length mismatch: {len(simulated_trades)} vs {len(historical_prints)}")
            return False

        for i, (sim, hist) in enumerate(zip(simulated_trades, historical_prints)):
            # Assuming dictionaries with matching keys for comparison
            for key in hist:
                if sim.get(key) != hist[key]:
                    print(f"[REPLAY VERIFY] Mismatch at index {i}: sim {key}={sim.get(key)}, hist {key}={hist[key]}")
                    return False

        print("[REPLAY VERIFY] Verification against historic trade prints successful.")
        return True
