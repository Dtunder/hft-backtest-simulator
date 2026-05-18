import heapq

class HistoricalReplayEngine:
    """
    Ultra-performance replay system that streams historical L3 message logs
    (orders, cancels, executions) through the simulator.
    Uses heapq for K-way merge to handle sub-microsecond timestamp alignment
    of multiple historical L3 message feeds chronologically.
    """
    def __init__(self):
        self.feeds = []
        self.trade_prints = []

    def load_feed(self, feed_name, messages):
        """
        Load an L3 message feed.
        messages: list of dictionaries, each having a 'timestamp' key.
        """
        sorted_messages = sorted(messages, key=lambda x: x['timestamp'])
        self.feeds.append({
            'name': feed_name,
            'messages': sorted_messages
        })

    def load_trade_prints(self, prints):
        """
        Load historical trade prints for validation.
        """
        self.trade_prints = sorted(prints, key=lambda x: x['timestamp'])

    def stream_messages(self):
        """
        Stream historical L3 message logs using K-way merge.
        Yields messages chronologically aligned across multiple exchange feeds.
        """
        queue = []

        for idx, feed in enumerate(self.feeds):
            if feed['messages']:
                first_msg = feed['messages'][0]
                # (timestamp, feed_idx, msg_idx, msg)
                heapq.heappush(queue, (first_msg['timestamp'], idx, 0, first_msg))

        while queue:
            timestamp, feed_idx, msg_idx, msg = heapq.heappop(queue)
            yield msg

            next_msg_idx = msg_idx + 1
            if next_msg_idx < len(self.feeds[feed_idx]['messages']):
                next_msg = self.feeds[feed_idx]['messages'][next_msg_idx]
                heapq.heappush(queue, (next_msg['timestamp'], feed_idx, next_msg_idx, next_msg))

    def verify_against_trade_prints(self, executions):
        """
        Verify the simulated executions against the historical trade prints.
        executions: list of simulated execution messages.
        Returns True if executions match historical prints.
        """
        if len(executions) != len(self.trade_prints):
            print(f"Mismatch in length: simulated {len(executions)}, historical {len(self.trade_prints)}")
            return False

        for sim_exec, hist_print in zip(executions, self.trade_prints):
            if sim_exec.get('timestamp') != hist_print.get('timestamp') or \
               sim_exec.get('price') != hist_print.get('price') or \
               sim_exec.get('qty') != hist_print.get('qty'):
                print(f"Mismatch found: {sim_exec} != {hist_print}")
                return False
        return True
