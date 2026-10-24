# Synthetic NFT collection audit

Demo data: synthetic fixtures

All prices use fictional DEMO units.

## Aurora Gardens (strong fixture)

Synthetic collection: `synthetic-aurora-gardens`
Demo data: synthetic fixtures

**Score: 9.78/10 - CANDIDATE** (candidate gate: >= 7.00).
Research scoring model. Not investment advice.

| Component | Points / 10 | Weight |
| --- | ---: | ---: |
| Liquidity and floor | 10.00 | 25% |
| Mint terms | 10.00 | 25% |
| Wash-trading risk | 9.13 | 25% |
| Contract risk | 10.00 | 25% |

### Score explanation

- **Liquidity and floor:** Positive primary floor: +4. Positive primary 24h volume: +4. Both market fields are present and positive: +2.
- **Mint terms:** Mint price disclosed (including a free mint): +3. Stage count disclosed: +2. Allowlist policy explicitly disclosed: +1. Terms transparent: +2. Terms unchanged in the fixture review: +2.
- **Wash-trading risk:** Complete primary trade summary: +10 before risk deductions. Concentrated volume penalty: -0.00. Circular-trade penalty: -0.87.
- **Contract risk:** Source verified in the primary fixture review: +4. Verified source and standard mint method: +6.

### Primary fixture references

- market: `aurora-market-v1`
- mint: `aurora-terms-v1`
- trading: `aurora-trades-v1`
- contract: `aurora-review-v1`

Offline model output; candidate status requests human review.

## Mist Arcade (gray fixture)

Synthetic collection: `synthetic-mist-arcade`
Demo data: synthetic fixtures

**Score: 6.95/10 - REJECTED** (candidate gate: >= 7.00).
Research scoring model. Not investment advice.

| Component | Points / 10 | Weight |
| --- | ---: | ---: |
| Liquidity and floor | 10.00 | 25% |
| Mint terms | 4.00 | 25% |
| Wash-trading risk | 3.79 | 25% |
| Contract risk | 10.00 | 25% |

### Score explanation

- **Liquidity and floor:** Positive primary floor: +4. Positive primary 24h volume: +4. Both market fields are present and positive: +2.
- **Mint terms:** Mint price disclosed (including a free mint): +3. Stage count disclosed: +2. Allowlist policy explicitly disclosed: +1. Terms transparent: +2. Terms unchanged in the fixture review: +0. Changing terms: -4.
- **Wash-trading risk:** Complete primary trade summary: +10 before risk deductions. Concentrated volume penalty: -4.86. Circular-trade penalty: -1.35.
- **Contract risk:** Source verified in the primary fixture review: +4. Verified source and standard mint method: +6.

### Primary fixture references

- market: `mist-market-v1`
- mint: `mist-terms-v1`
- trading: `mist-trades-v1`
- contract: `mist-review-v1`

Offline model output; candidate status requests human review.

## Paper Comets (scam fixture)

Synthetic collection: `synthetic-paper-comets`
Demo data: synthetic fixtures

**Score: 0.22/10 - REJECTED** (candidate gate: >= 7.00).
Research scoring model. Not investment advice.

| Component | Points / 10 | Weight |
| --- | ---: | ---: |
| Liquidity and floor | 0.00 | 25% |
| Mint terms | 0.00 | 25% |
| Wash-trading risk | 0.89 | 25% |
| Contract risk | 0.00 | 25% |

### Score explanation

- **Liquidity and floor:** Missing or zero primary floor: +0. Missing or zero primary 24h volume: +0. Loud liquidity claim with incomplete primary market data: -4.
- **Mint terms:** Mint price disclosed (including a free mint): +0. Stage count disclosed: +0. Allowlist policy explicitly disclosed: +0. Terms transparent: +0. Terms unchanged in the fixture review: +0. Hidden terms: -5. Changing terms: -4.
- **Wash-trading risk:** Complete primary trade summary: +10 before risk deductions. Concentrated volume penalty: -8.00. Circular-trade penalty: -1.11.
- **Contract risk:** Source verification absent or negative: +0. Custom or opaque mint method: -4.

### Primary fixture references

- market: `comets-market-v1`
- mint: `comets-terms-v1`
- trading: `comets-trades-v1`
- contract: `comets-review-v1`

Offline model output; candidate status requests human review.

## Post-mint price tracker

Demo data: synthetic fixtures

Collection: `synthetic-aurora-gardens`. Mint price: 1.0300 DEMO.

Nearest post-mint samples; positive offsets mean observations after the target time.

| Target | Target time (UTC) | Sample time (UTC) | Offset (s) | Price (DEMO) | Change vs mint |
| --- | --- | --- | ---: | ---: | ---: |
| 1m | 2026-09-17T09:24:41+00:00 | 2026-09-17T09:24:46+00:00 | +5 | 1.0410 | +1.07% |
| 30m | 2026-09-17T09:53:41+00:00 | 2026-09-17T09:53:31+00:00 | -10 | 1.0790 | +4.76% |
| 60m | 2026-09-17T10:23:41+00:00 | 2026-09-17T10:24:01+00:00 | +20 | 1.1370 | +10.39% |
| 180m | 2026-09-17T12:23:41+00:00 | 2026-09-17T12:23:51+00:00 | +10 | 1.1830 | +14.85% |
| 240m | 2026-09-17T13:23:41+00:00 | 2026-09-17T13:23:21+00:00 | -20 | 1.2190 | +18.35% |
| 360m | 2026-09-17T15:23:41+00:00 | 2026-09-17T15:24:11+00:00 | +30 | 1.2810 | +24.37% |
| 1d | 2026-09-18T09:23:41+00:00 | 2026-09-18T09:23:51+00:00 | +10 | 1.3590 | +31.94% |
| 2d | 2026-09-19T09:23:41+00:00 | 2026-09-19T09:23:31+00:00 | -10 | 1.4310 | +38.93% |
| 3d | 2026-09-20T09:23:41+00:00 | 2026-09-20T09:24:01+00:00 | +20 | 1.4870 | +44.37% |
| 7d | 2026-09-24T09:23:41+00:00 | 2026-09-24T09:23:51+00:00 | +10 | 1.6130 | +56.60% |
| 14d | 2026-10-01T09:23:41+00:00 | 2026-10-01T09:23:31+00:00 | -10 | 1.7910 | +73.88% |
| 30d | 2026-10-17T09:23:41+00:00 | 2026-10-17T09:24:11+00:00 | +30 | 1.9970 | +93.88% |
