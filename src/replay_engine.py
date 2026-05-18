import heapq

class HistoricalReplayEngine:
    def __init__(self):
        pass

    def stream_feeds(self, feeds):
        """
        Stream historical L3 message logs from multiple feeds using K-way merge
        for sub-microsecond timestamp alignment.
        feeds is a list of iterables of messages.
        Each message is expected to be a dictionary with a 'timestamp' key.
        """
        iters = [iter(f) for f in feeds]
        pq = []
        for i, it in enumerate(iters):
            try:
                msg = next(it)
                heapq.heappush(pq, (msg['timestamp'], i, msg))
            except StopIteration:
                pass

        while pq:
            timestamp, i, msg = heapq.heappop(pq)
            yield msg

            try:
                next_msg = next(iters[i])
                heapq.heappush(pq, (next_msg['timestamp'], i, next_msg))
            except StopIteration:
                pass

    def verify_against_trade_prints(self, simulated_trades, historical_prints):
        """
        Verify generated simulated trades against historic trade prints.
        Returns True if they match, False otherwise.
        """
        if len(simulated_trades) != len(historical_prints):
            return False

        for sim, hist in zip(simulated_trades, historical_prints):
            if sim != hist:
                return False

        return True
