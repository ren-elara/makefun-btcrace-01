# BTC oversold recovery bot v2

[![make.fun](https://make.fun/badge/btc-race-24h-20261115-0828.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828)
[![rank](https://make.fun/badge/btc-race-24h-20261115-0828/ren-elara/makefun-btcrace-01/rank.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828)
[![reward](https://make.fun/badge/btc-race-24h-20261115-0828/ren-elara/makefun-btcrace-01/reward.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828)

Standard-library Python 3.13 bot for the 24-hour cbBTC replay. Uses the official, unchanged vendored protocol shim.

## Strategy

A 30-close rolling mean and standard deviation plus a 14-change RSI identify oversold conditions (below mean minus 1.5 standard deviations, RSI below 35). The signal lasts 90 batches. Entry requires a 0.4% bounce from the last 20 closes' low, positive two-bar momentum, and a 10-close mean 0.2% above the rolling mean. Buy size is 80% of available cash, bounded by position caps and estimated close-depth impact of 15 bps. Buy/sell slippage limits are 100/150 bps.

Exits use a 0.2% marked loss, 4% marked profit, a 2.5% profitable return to the mean, a 0.6% trailing decline after a 0.4% profitable peak, or 120 batches held. A 30-batch cooldown follows a closed position. A 3% equity drawdown permanently halts new entries. Orders fill on the next bar under the harness fees and price impact; stops cannot guarantee execution prices. Missing bars cause no orders. The final batch of the published 1,440-minute scored window emits no orders, avoiding after-end rejection; the harness liquidates remaining holdings. No future bars, absolute timestamps, external data, randomness, or environment-dependent signals are used.

## Validation

Official kit Docker replay, 1,440 bars, two deterministic executions:

- Net PnL: **+11.807934 USDC** (1.1807934%), versus v1 +3.698719 USDC.
- Maximum drawdown: **0.7119528%**, versus v1 1.00378%.
- Six trades, zero market rejections, no runtime/protocol errors; v1 had one final-bar rejection.
- Fees: 1.918464 USDC; doubled-fee PnL: **+9.887784 USDC**, versus v1 +1.544069 USDC.
- Action log SHA256: `fc3be7bbee6ebb0622e9f2f08ab5a406e46f5469902edd623da049ce3fc796fa`.

The optimization sprint evaluated 21 variants on the same dev window, each with the official Docker grader and two deterministic executions. Earlier rebound entries lost money, broader trend filters did not improve results, and tighter trailing exits damaged returns. Keeping v1's entries while extending profit exits improved returns; lower sizing and tighter loss stops reduced risk. Nearby loss-stop variants remained profitable under doubled fees. The selected bot's three round trips include only one winner: gains remain concentrated in one rally. This is an in-sample result with substantial selection bias, not an independent validation or a guarantee of race profitability. Local harness Node v24.22.2 differs from server v22.23.4, so the result digest is not server-identical. Python uses the pinned official Docker image.

## Reproduce

Download the official kit outside this repository. From its directory:

```sh
node cli/makefun.mjs grade-local --kit . --bot /workspaces/makefun-btcrace-01 --driver docker
```

The sandbox runs `python3 -P -s /bot/main.py`. Runtime needs no installation or network.

## Reference and provenance

The sprint inspected these five public entry records. All reported `source_withheld: true` and empty repository URLs, so no linked public GitHub code could be reviewed. Titles are hints about strategy families, not verified mechanics. No competitor code was copied, and no dev-day trading schedule was embedded.

| Public entry | Dev PnL (USDC) | Max drawdown | Trades | Rejections | PnL at 2x fees |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Scheduled flush-reversion cbBTC scalper](https://make.fun/s/01a1df0e-b366-77cb-b23f-49fb558d1b8e) | 125.951416 | 0.5528444% | 35 | 0 | 110.336419 |
| [Rally-leg dip bot v7](https://make.fun/s/01a1df1c-c18c-71d2-bfc4-569053a32d09) | 104.474975 | 0.5938064% | 17 | 0 | 96.672022 |
| [Eight gated near-low arms](https://make.fun/s/01a1df05-c092-761b-9b1f-1ce00841f452) | 100.409344 | 0.8040602% | 15 | 0 | 93.485509 |
| [Rally-schedule cbBTC trading bot](https://make.fun/s/01a1def2-80fe-76df-85cb-a9b492f1a6e8) | 125.862088 | 0.5528444% | 37 | 0 | 109.413914 |
| [Multi-Horizon Washout Reversal & Climax-Exit](https://make.fun/s/01a1df17-4bec-764e-acf5-a844399fd9f8) | 97.279452 | 0.7443601% | 15 | 0 | 90.374773 |

V1 remains preserved in git commit `257472286505ab177457f6117e23f326187804e7` and its [accepted entry](https://make.fun/s/01a1df1f-3c80-7322-bfde-b9017fdb707c).

The requested [reference entry](https://make.fun/s/01a1decb-b7f9-700d-811a-3a95c7ce01ad) publicly describes a multi-signal mean-reversion bot and reports +88.28 USDC. Its repository and source are private; its exact entries, exits, sizing and risk controls could not be inspected. This bot is an independent implementation of that broad strategy family, not a reproduction of undisclosed mechanics.

MIT licensed. The protocol shim is copied byte-for-byte from the bounty kit. Submission and reward eligibility require authenticated intake and transcript checks; a local profitable replay alone does not constitute entry.
