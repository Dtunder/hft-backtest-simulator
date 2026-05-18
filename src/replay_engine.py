import heapq

class HistoricalReplayEngine:
    """
    Ultra-performance replay system that streams historical L3 message logs
    through the simulator, handling sub-microsecond timestamp alignment across
    multiple exchange feeds chronologically using K-way merge.
    """
    def __init__(self):
        self.feeds = []

    def add_feed(self, feed):
        """
        Adds a historical L3 message feed.
        `feed` should be an iterable of dictionaries, each containing a 'timestamp' key.
        """
        self.feeds.append(feed)

    def replay(self):
        """
        Streams events chronologically based on 'timestamp' across all feeds.
        Yields sub-microsecond aligned events.
        """
        # Perform K-way merge based on timestamp
        merged = heapq.merge(*self.feeds, key=lambda x: x['timestamp'])
        for event in merged:
            yield event

    def verify_against_trade_prints(self, executions, trade_prints):
        """
        Validates the simulator's executions against historic trade prints.
        """
        if len(executions) != len(trade_prints):
            print(f"[REPLAY] Execution count mismatch: {len(executions)} != {len(trade_prints)}")
            return False

        for i, (exec_event, print_event) in enumerate(zip(executions, trade_prints)):
            if exec_event['timestamp'] != print_event['timestamp']:
                print(f"[REPLAY] Timestamp mismatch at {i}: {exec_event['timestamp']} != {print_event['timestamp']}")
                return False
            if exec_event.get('price') != print_event.get('price'):
                print(f"[REPLAY] Price mismatch at {i}")
                return False
            if exec_event.get('size') != print_event.get('size'):
                print(f"[REPLAY] Size mismatch at {i}")
                return False

        return True
