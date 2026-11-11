"""cbBTC minute-bar trading bot (make.fun bars-replay/v1).

Strategy: mean-reversion swing trader on a single symbol (CBBTC).
- Rolling mean/std of closes over a 220-bar window; z-score of the latest close.
- Long entry when the close dips z <= -2.5 below its rolling mean (full cash).
- Exit when the close recovers to z >= 2.2 above the rolling mean (wide take-profit),
  or on a stop-loss (250 bps below entry).
- Deterministic: no clock, no randomness, no network.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

WINDOW = 220
ENTRY_Z = 2.5
EXIT_Z = 2.2
STOP_BPS = 250
MAX_SLIP_BPS = 100

closes = []


def _zscore(c):
    mean = sum(c) / len(c)
    var = sum((x - mean) ** 2 for x in c) / len(c)
    std = int(var ** 0.5)
    if std == 0:
        return None
    return (10**5 * (c[-1] - mean)) // std  # z in 1e-5 units


def on_batch(state, batch):
    closes.append(state.close("CBBTC"))
    pos = state.positions.get("CBBTC")

    if pos is not None:
        if len(closes) >= WINDOW:
            z = _zscore(closes[-WINDOW:])
            if z is not None and z >= int(EXIT_Z * 10**5):
                return [{"side": "sell", "symbol": "CBBTC", "qty": pos.qty,
                         "max_slippage_bps": MAX_SLIP_BPS}]
        entry = pos.cost // max(pos.qty, 1)  # avg cost per qty unit
        if closes[-1] * 10**4 < entry * (10**4 - STOP_BPS):
            return [{"side": "sell", "symbol": "CBBTC", "qty": pos.qty,
                     "max_slippage_bps": MAX_SLIP_BPS}]
        return []

    if len(closes) < WINDOW:
        return []
    z = _zscore(closes[-WINDOW:])
    if z is not None and z <= -int(ENTRY_Z * 10**5):
        notional = state.cash
        if notional < int(state.hello["fees"]["min_notional_quote_units"]):
            return []
        return [{"side": "buy", "symbol": "CBBTC", "notional_quote_units": notional,
                 "max_slippage_bps": MAX_SLIP_BPS}]
    return []


makefun_bars.run(on_batch)
