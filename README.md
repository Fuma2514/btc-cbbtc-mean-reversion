# cbBTC minute-bar mean-reversion bot

Entry for make.fun [btc-race-24h-20261111-0801](https://make.fun/bounty/btc-race-24h-20261111-0801).

Python 3.13, standard library only (`vendor/makefun_bars.py` is the kit's own shim).

## Strategy
Mean reversion on CBBTC 1-minute bars: buy when the close dips 2.5 std below its
360-bar rolling mean (full cash), exit when it mean-touches (z >= 0.5) or on an
80 bps stop-loss below average cost. Deterministic: no wall clock, no network,
no randomness. Parameters were chosen on the competition's published frozen dev
window only.

## Run
The grader runs `python3 -P -s /bot/main.py` with `PYTHONHASHSEED=0` against the
bars-replay/v1 harness; nothing is installed.

## Dev-window result (kit dataset, local `makefun grade-local`)
- net PnL: **+8.52 USDC** on $1,000 (return +0.85%)
- 6 trades, win rate 2/3, max drawdown 1.4%, 0 rejected orders
- positive even at 2x fees (+6.11)

## License
MIT
