import heapq

class HistoricalReplayEngine:
    """
    Historical Tick-Data Replay Engine.
    Streams historical L3 message logs (orders, cancels, executions) through the simulator.
    Integrates sub-microsecond timestamp alignment across multiple exchange feeds.
    """
    def __init__(self):
        self.feeds = []
        self.historical_prints = []

    def load_feed(self, feed):
        """
        Loads a feed. A feed is a list of events.
        Each event is expected to be a dictionary with a 'timestamp' key (float).
        """
        self.feeds.append(feed)

    def load_historical_prints(self, prints):
        """
        Loads historical trade prints for verification.
        """
        self.historical_prints = prints

    def stream(self):
        """
        Uses heapq for K-way merge to handle sub-microsecond timestamp alignment
        of multiple historical L3 message feeds chronologically.
        """
        heap = []
        for i, feed in enumerate(self.feeds):
            if feed:
                # Store (timestamp, feed_index, event_index, event)
                heapq.heappush(heap, (feed[0]['timestamp'], i, 0, feed[0]))

        while heap:
            ts, feed_idx, event_idx, event = heapq.heappop(heap)
            yield event

            next_idx = event_idx + 1
            if next_idx < len(self.feeds[feed_idx]):
                next_event = self.feeds[feed_idx][next_idx]
                heapq.heappush(heap, (next_event['timestamp'], feed_idx, next_idx, next_event))

    def verify_against_trade_prints(self, simulated_trades):
        """
        Validates simulated executions against historic trade prints.
        """
        if len(simulated_trades) != len(self.historical_prints):
            print(f"[REPLAY] Verification failed: {len(simulated_trades)} simulated vs {len(self.historical_prints)} historical prints.")
            return False

        for sim, hist in zip(simulated_trades, self.historical_prints):
            if sim != hist:
                print(f"[REPLAY] Verification failed at trade: sim={sim}, hist={hist}")
                return False

        print("[REPLAY] Verification against historic trade prints successful.")
        return True
