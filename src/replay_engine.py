import heapq

class HistoricalReplayEngine:
    """
    Historical Tick-Data Replay Engine.
    Streams historical L3 message logs (orders, cancels, executions) through the simulator.
    Uses K-way merge for sub-microsecond timestamp alignment across multiple exchange feeds.
    """
    def __init__(self):
        self.streams = []

    def add_feed(self, feed):
        """
        Adds an L3 message feed stream to the replay engine.
        Each feed should be an iterable of messages (e.g. tuples like (timestamp, exchange, message_type, data)).
        """
        # Convert feed to an iterator and get the first item if available
        iterator = iter(feed)
        try:
            first_item = next(iterator)
            # Push (timestamp, index, first_item, iterator) to ensure stability in heapq
            # index is to avoid comparing items directly when timestamps are identical
            heapq.heappush(self.streams, (first_item[0], len(self.streams), first_item, iterator))
        except StopIteration:
            pass

    def stream(self):
        """
        Streams chronologically aligned L3 messages across multiple exchange feeds.
        """
        while self.streams:
            timestamp, index, item, iterator = heapq.heappop(self.streams)
            yield item
            try:
                next_item = next(iterator)
                heapq.heappush(self.streams, (next_item[0], index, next_item, iterator))
            except StopIteration:
                pass

    def verify_against_trade_prints(self, executions, trade_prints):
        """
        Verifies execution sequence against historic trade prints.
        Executions and trade_prints should be iterables of (timestamp, ...).
        Returns True if they match, False otherwise.
        """
        executions_list = list(executions)
        trade_prints_list = list(trade_prints)

        if len(executions_list) != len(trade_prints_list):
            return False

        for exec_item, print_item in zip(executions_list, trade_prints_list):
            if exec_item != print_item:
                return False

        return True
