import heapq

class HistoricalReplayEngine:
    def __init__(self):
        self.feeds = []
        self.trade_prints = []

    def load_feed(self, feed_name, messages):
        """
        Load a historical L3 message feed.
        messages should be an iterable of tuples (timestamp, message_type, data)
        where timestamp is in sub-microseconds.
        """
        self.feeds.append(iter(messages))

    def load_trade_prints(self, prints):
        """
        Load historic trade prints for validation.
        prints should be a list of (timestamp, price, quantity)
        """
        self.trade_prints = sorted(prints, key=lambda x: x[0])

    def stream_messages(self):
        """
        Yields messages chronologically from all loaded feeds using K-way merge.
        """
        # heapq.merge performs K-way merge on sorted iterables
        # Assuming each feed is already sorted by timestamp (the first element of the tuple)
        merged_feed = heapq.merge(*self.feeds, key=lambda x: x[0])
        for msg in merged_feed:
            yield msg

    def verify_against_trade_prints(self, simulated_trades):
        """
        Validates simulated trades against historic trade prints.
        simulated_trades: list of (timestamp, price, quantity)
        Returns True if matched, False otherwise.
        """
        if len(simulated_trades) != len(self.trade_prints):
            return False

        simulated_trades = sorted(simulated_trades, key=lambda x: x[0])

        for sim_trade, hist_trade in zip(simulated_trades, self.trade_prints):
            # timestamp, price, qty
            if sim_trade != hist_trade:
                return False
        return True
