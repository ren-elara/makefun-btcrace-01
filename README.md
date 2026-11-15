# BTC oversold recovery bot

[![make.fun](https://make.fun/badge/btc-race-24h-20261115-0828.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828)
[![rank](https://make.fun/badge/btc-race-24h-20261115-0828/ren-elara/makefun-btcrace-01/rank.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828)
[![reward](https://make.fun/badge/btc-race-24h-20261115-0828/ren-elara/makefun-btcrace-01/reward.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828)

Standard-library Python 3.13 bot for the 24-hour cbBTC replay. Uses the official, unchanged vendored protocol shim.

## Strategy

A 30-close rolling mean and standard deviation plus a 14-change RSI identify oversold conditions (below mean minus 1.5 standard deviations, RSI below 35). The signal lasts 90 batches. Entry requires a 0.4% bounce from the last 20 closes' low, positive two-bar momentum, and a 10-close mean 0.2% above the rolling mean. Buy size is 90% of available cash, bounded by position caps and estimated close-depth impact of 15 bps. Buy/sell slippage limits are 100/150 bps.

Exits use a 0.4% marked loss, 2.5% marked profit, a 1% profitable return to the mean, a 0.6% trailing decline after a 0.4% profitable peak, or 60 batches held. A 30-batch cooldown follows a closed position. A 10% equity drawdown permanently halts new entries. Orders fill on the next bar under the harness fees and price impact; stops cannot guarantee execution prices. Missing bars cause no orders. No timestamps, future bars, external data, randomness, or environment-dependent signals are used.

## Validation

Official kit Docker replay, 1,440 bars, two deterministic executions:

- Net PnL: **+3.698719 USDC** (0.3698719%).
- Maximum drawdown: **1.00378%**.
- Six trades, one market rejection, no runtime/protocol errors.
- Fees: 2.156658 USDC; doubled-fee PnL: +1.544069 USDC.
- Action log SHA256: `eb87dc03d2bbbd1d497a07f6be561232ec2d9de9f86189200028e0cfaba8b405`.

Several strategy revisions were evaluated on the same dev window. This is an in-sample result with selection bias, not an independent validation or a guarantee of race profitability. Local harness Node v24.22.2 differs from server v22.23.4, so the result digest is not server-identical. Python uses the pinned official Docker image.

## Reproduce

Download the official kit outside this repository. From its directory:

```sh
node cli/makefun.mjs grade-local --kit . --bot /workspaces/makefun-btcrace-01 --driver docker
```

The sandbox runs `python3 -P -s /bot/main.py`. Runtime needs no installation or network.

## Reference and provenance

The requested [reference entry](https://make.fun/s/01a1decb-b7f9-700d-811a-3a95c7ce01ad) publicly describes a multi-signal mean-reversion bot and reports +88.28 USDC. Its repository and source are private; its exact entries, exits, sizing and risk controls could not be inspected. This bot is an independent implementation of that broad strategy family, not a reproduction of undisclosed mechanics.

MIT licensed. The protocol shim is copied byte-for-byte from the bounty kit. Submission and reward eligibility require authenticated intake and transcript checks; a local profitable replay alone does not constitute entry.
