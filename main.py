"""Causal oversold-rebound strategy for the make.fun BTC replay."""
import os
import sys
from collections import deque
from statistics import fmean, pstdev

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars


class Rebound:
    def __init__(self):
        self.prices = deque(maxlen=30)
        self.entry_seq = None
        self.peak = 0
        self.cooldown = -1
        self.high_equity = 0
        self.halted = False
        self.armed_until = -1

    def __call__(self, state, batch):
        # The published scored window is 1,440 minutes; its last orders cannot fill.
        if state.seq >= state.warmup_bars + 1439:
            return []
        bars = [b for b in batch["bars"] if b["symbol"] == "CBBTC"]
        if not bars:
            return []
        price = int(bars[0]["c"])
        self.prices.append(price)
        self.high_equity = max(self.high_equity, state.equity)
        if state.equity * 100 < self.high_equity * 97:
            self.halted = True
        holding = state.positions.get("CBBTC")
        if holding:
            if self.entry_seq is None:
                self.entry_seq = state.seq
                self.peak = price
            self.peak = max(self.peak, price)
            value = state.value("CBBTC", holding.qty)
            profit = value / holding.cost - 1
            recovered = len(self.prices) >= 30 and price >= fmean(self.prices)
            exit_now = (self.halted or profit <= -0.002
                        or profit >= 0.04
                        or (profit >= 0.025 and recovered)
                        or (state.value("CBBTC", holding.qty, self.peak) > holding.cost * 1.004
                            and price < self.peak * 0.994)
                        or state.seq - self.entry_seq >= 120)
            if exit_now:
                return [{"side": "sell", "symbol": "CBBTC",
                         "qty": holding.qty, "max_slippage_bps": 150}]
            return []
        if self.entry_seq is not None:
            self.entry_seq = None
            self.cooldown = state.seq + 30
            self.armed_until = -1
        if self.halted or state.warming_up or state.seq < self.cooldown or len(self.prices) < 30:
            return []
        prices = list(self.prices)
        mean = fmean(prices)
        sigma = pstdev(prices)
        changes = [b - a for a, b in zip(prices[-15:-1], prices[-14:])]
        gains = sum(max(0, c) for c in changes)
        losses = sum(max(0, -c) for c in changes)
        rsi = 100 * gains / (gains + losses) if gains + losses else 50
        oversold = price < mean - 1.5 * sigma and rsi < 35
        # Require an actual bounce after a meaningful displacement, not a flat pool.
        if oversold:
            self.armed_until = state.seq + 90
        rebound = (price > min(prices[-20:]) * 1.004
                   and price > prices[-3] * 1.001
                   and price > prices[-2]
                   and fmean(prices[-10:]) > mean * 1.002)
        amount = min(state.cash * 80 // 100, state.weight_room("CBBTC"))
        impact = state.impact_bps("CBBTC", amount)
        if state.seq <= self.armed_until and rebound and amount >= 1_000_000 and impact is not None and impact <= 15:
            return [{"side": "buy", "symbol": "CBBTC",
                     "notional_quote_units": amount, "max_slippage_bps": 100}]
        return []


if __name__ == "__main__":
    makefun_bars.run(Rebound())