# nft-collection-audit

An offline, reproducible pre-mint NFT collection audit and post-mint price
tracker, built with Codex. Python 3.11+; the application uses only the standard
library. The only test dependency is pytest.

Codex acts as an **independent auditor**: it separates collection claims from
primary records, checks the provenance and completeness of those records,
explains deductions, and accepts a result only after verification. This demo
uses synthetic primary-record fixtures. It checks those local records, rather
than independently fetching or verifying external facts.

## Run the demo in three commands

Open a terminal in this project folder with Python 3.11+ selected. These same
commands work in PowerShell and a POSIX shell:

```text
python -m pip install -r requirements.txt
python examples/run_demo.py
python -m pytest
```

The demo prints three complete Markdown collection cards and a 12-row tracker.
No installation is needed to run the demo alone. To also save its report:

```text
python examples/run_demo.py --output demo-output/report.md
```

All input data is fictional, and prices are in fictional `DEMO` units.
The application has no networking, wallet operations, transactions, or mint
execution. A candidate status is an analysis gate for human review.

## Evidence and input format

`data/collections.json` contains three collections. Each declares
`synthetic: true`, identifies separate promotional `claims`, and maps four
`evidence_refs` to named entries in `sources`. Each source must also declare
`synthetic: true` and have the appropriate `kind`:

| Reference | Source kind | Evidence fields |
| --- | --- | --- |
| market | market_snapshot | floor_price, volume_24h |
| mint | mint_terms | price, stages, allowlist, terms_disclosed, terms_changed |
| trading | trade_summary | top_wallet_volume_share, circular_trade_share |
| contract | contract_review | source_verified, mint_method |

The extractor resolves record identifiers and kinds. Missing references or
wrong-kind records yield missing evidence and a warning. Claims never substitute
for primary fields. A source identifier is fixture provenance, not proof of
authenticity outside this demo. Trade shares are supplied summary measurements;
this project does not infer cycles from raw trades or validate the summaries
against a ledger. `source_verified` is the synthetic review's recorded finding.

Null means missing. Numbers must be finite and nonnegative; shares must be in
0..1. Stages must be an integer in 1..20, and flags must be actual booleans.
Explicit `allowlist: false` means a disclosed public policy and earns the same
disclosure point as `true`. A disclosed zero mint price represents a free mint.
Missing values never imply a favorable finding.

## Scoring model v1

Each component is clamped to 0..10 and receives a 25% weight. The final score is
the arithmetic mean, rounded to two decimal places using decimal half-up
rounding. The hard gate applies to that published final score:
**score >= 7.00 means CANDIDATE; anything lower is REJECTED**.

| Component | Exact rules before clamping |
| --- | --- |
| Liquidity and floor | +4 for a positive primary floor, +4 for positive primary 24h volume, +2 if both exist. Deduct 4 if a loud claim accompanies an absent/zero field. A loud claim is high_liquidity=true or claimed volume >= 1000 DEMO. Deduct another 2 if claimed volume exceeds twice a present primary volume. |
| Mint terms | +3 for price, +2 for stage count, +1 for explicit allowlist policy, +2 for transparent terms, +2 for unchanged terms. Deduct 5 for hidden terms and 4 for changing terms. |
| Wash-trading risk | Start at 10 only if both trade shares exist; otherwise score 0. Deduct min(8, max(0, (top share - 0.30) * 20)) and min(10, circular share * 30). |
| Contract risk | +4 for verified source and +6 more for a verified standard/seadrop mint. Deduct 4 for a custom/opaque mint. A method name without verified source earns no points. |

`top_wallet_volume_share` is the fraction attributed to the small group of
dominant participants in the fixture summary. The constants above are explicit
demo heuristics, not empirically calibrated predictors. Missing market evidence
cannot be rescued by a marketplace claim. Pre-mint collections without resale
evidence therefore receive a conservative liquidity score.

| Fictional collection | Final score | Gate |
| --- | ---: | --- |
| Aurora Gardens (strong) | 9.85 | CANDIDATE |
| Mist Arcade (gray) | 6.55 | REJECTED |
| Paper Comets (scam) | 0.00 | REJECTED |

Each card includes component scores, deductions, and resolved source identifiers.
A score is not a guarantee of contract safety or a price forecast.

## Price tracker

Targets are exactly **1/30/60/180/240/360 minutes** and
**1/2/3/7/14/30 days** after mint. The baseline is the positive mint price:

```text
change_pct = (sample_price - mint_price) / mint_price * 100
```

The tracker accepts timezone-aware observations in any order, normalizes them
to UTC, and chooses the closest observation at or after mint for each target.
An equal-distance tie selects the earlier observation. Duplicate timestamps are
rejected. Zero observed prices are allowed (-100%); a zero mint baseline is not.

This is retrospective nearest-point matching: a later observation can be chosen,
and a sample may serve multiple targets. The table shows both timestamps and
the signed offset in seconds so sparse data remains visible. The default has no
distance limit. Call `track_prices(..., max_distance=timedelta(minutes=1))` to
reject distant samples; empty inputs or rejected samples produce `unavailable`
rows. The demo uses small, deliberately nonzero offsets to demonstrate matching.

## How Codex is used in this workflow

1. Review the supplied claims against the synthetic primary records; identify
   missing evidence, changing mint terms, trading patterns, and contract findings.
2. Extract features and apply the documented model without ad hoc score changes.
3. Inspect each card and the tracker sampling offsets.
4. Run the tests and the demo; accept the local result only when both pass.

Changes to heuristics must update the explanation, expected fixture scores, and
tests together. All fixtures remain synthetic, with no external accounts or
production integrations.

## Project structure

```text
nft-collection-audit/
  README.md, LICENSE, .gitignore, requirements.txt, pytest.ini
  src/nft_audit/
    __init__.py
    features.py       # typed evidence extraction and validation
    scoring.py        # components, normalization, hard gate
    tracker.py        # schedule, nearest samples, percentage changes
    card.py           # Markdown cards with score explanations
  data/
    collections.json  # strong, gray, and scam fixtures
    price_series.json # synthetic post-mint observations
  examples/run_demo.py
  tests/test_scoring.py
  tests/test_tracker.py
```

## License

MIT. See `LICENSE`.
