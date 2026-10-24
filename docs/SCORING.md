# Scoring model v1

Research scoring model. Not investment advice.

Each component is clamped to 0..10 and receives a 25% weight. The final score is
the arithmetic mean, rounded to two decimal places with decimal half-up rounding.
The hard gate applies to that published score: >= 7.00 is CANDIDATE; otherwise
REJECTED. Candidate status requests human review and predicts neither safety nor
future prices.

| Component | Exact rules before clamping |
| --- | --- |
| Liquidity and floor | +4 for a positive primary floor, +4 for positive primary 24h volume, +2 if both exist. Deduct 4 if a loud claim accompanies an absent/zero field. A loud claim is high_liquidity=true or claimed volume >= 1000 DEMO. Deduct another 2 if claimed volume exceeds twice a present primary volume. |
| Mint terms | +3 for price, +2 for stage count, +1 for explicit allowlist policy, +2 for transparent terms, +2 for unchanged terms. Deduct 5 for hidden terms and 4 for changing terms. |
| Wash-trading risk | Start at 10 only if both trade shares exist; otherwise 0. Deduct min(8, max(0, (top share - 0.30) * 20)) and min(10, circular share * 30). |
| Contract risk | +4 for verified source and +6 more for a verified standard/seadrop mint. Deduct 4 for custom/opaque mint. A method name without verified source earns no points. |

The constants are explicit demonstration heuristics, not empirically calibrated
predictors. `top_wallet_volume_share` is the fraction attributed to the small
dominant group in the supplied fixture summary. The model does not reconstruct
trade cycles from raw trades. `source_verified` is the local fixture review's
finding, rather than independent code or on-chain verification.

Missing evidence earns no positive points, but there are no hidden eligibility
rules beyond the published score gate. A missing component does not automatically
veto an otherwise qualifying average. Pre-mint collections with no resale data
receive a conservative liquidity component. Marketing claims never fill a missing
primary field.
