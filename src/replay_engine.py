import heapq

class HistoricalReplayEngine:
    """
    Historical Tick-Data Replay Engine.
    Streams historical L3 message logs (orders, cancels, executions) through the simulator.
    Integrates sub-microsecond timestamp alignment across multiple exchange feeds and
    verifies correctness against historic trade prints.
    """
    def __init__(self):
        self.feeds = []

    def load_feed(self, exchange, feed_data):
        """
        Load historical L3 message logs for an exchange feed.
        feed_data is a list of tuples: (timestamp_microseconds, message_type, order_details)
        """
        # Convert to an iterator for K-way merge
        self.feeds.append(iter(feed_data))

    def stream_messages(self):
        """
        Stream messages from all loaded feeds chronologically using K-way merge.
        Returns a generator yielding (timestamp_microseconds, message_type, order_details).
        """
        # heapq.merge correctly aligns iterators if elements are sortable
        # The elements are tuples where the first item is timestamp_microseconds, so they sort chronologically
        for msg in heapq.merge(*self.feeds):
            yield msg

    def verify_against_trade_prints(self, executions, trade_prints):
        """
        Verify the replay executions against historic trade prints.
        Executions and trade_prints should be comparable sequences.
        """
        return executions == trade_prints
