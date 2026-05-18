import heapq

class HistoricalReplayEngine:
    def __init__(self):
        self.message_streams = []

    def load_feed(self, feed_name, messages):
        """
        Loads a stream of historical L3 messages for a specific exchange/feed.
        Each message should be a dict or tuple containing a 'timestamp' field.
        Format expected: (timestamp, feed_name, message_data)
        """
        # Ensure messages are sorted by timestamp
        sorted_messages = sorted(messages, key=lambda x: x[0])
        self.message_streams.append(iter(sorted_messages))

    def stream_historical_l3_messages(self):
        """
        Streams historical L3 messages (orders, cancels, executions) chronologically
        using K-way merge for sub-microsecond timestamp alignment across multiple feeds.
        """
        merged_stream = heapq.merge(*self.message_streams, key=lambda x: x[0])
        for msg in merged_stream:
            yield msg

    def verify_against_trade_prints(self, simulated_trades, historical_trade_prints):
        """
        Verifies simulated executions against historic trade prints.
        Returns a boolean indicating if verification passed, or a report.
        """
        print("[REPLAY ENGINE] Verifying simulated executions against historic trade prints...")

        if len(simulated_trades) != len(historical_trade_prints):
            print(f"[REPLAY ENGINE] Mismatch in trade count: {len(simulated_trades)} simulated vs {len(historical_trade_prints)} historical.")
            return False

        # Ensure trades are sorted by timestamp for comparison
        sorted_simulated = sorted(simulated_trades, key=lambda x: x[0])
        sorted_historical = sorted(historical_trade_prints, key=lambda x: x[0])

        verified = True
        for sim, hist in zip(sorted_simulated, sorted_historical):
            sim_ts, sim_feed, sim_data = sim
            hist_ts, hist_feed, hist_data = hist

            # Verify timestamp, feed, type, price, and qty
            if sim_ts != hist_ts or sim_feed != hist_feed or \
               sim_data.get("type") != hist_data.get("type") or \
               sim_data.get("price") != hist_data.get("price") or \
               sim_data.get("qty") != hist_data.get("qty"):
                print(f"[REPLAY ENGINE] Mismatch detected: \nSimulated: {sim}\nHistorical: {hist}")
                verified = False

        if verified:
            print("[REPLAY ENGINE] Verification successful! All trades match.")

        return verified
