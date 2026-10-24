# v0.1.0 — offline collection scoring and price tracking

Draft release notes prepared on 2026-10-24. The release has not been created.

Demo data: synthetic fixtures

Research scoring model. Not investment advice.

This initial release provides four explained scoring components, a >= 7.00
candidate gate, primary-fixture provenance, and a retrospective tracker at twelve
targets through day 30. The generated scorecards cover a strong collection, a
borderline rejection, and a failed collection.

Local verification: 78 tests passed on Python 3.13.15 with pytest 9.1.1. The
repository includes a real regression/fix trace for missing output disclosures.
The author delegates implementation to agents and accepts it by verification;
Codex as an independent auditor is the workflow role.

Limits: all market, trading-summary, and contract-review inputs are fictional.
The model is heuristic; no raw-ledger wash-trade reconstruction, external source
authentication, contract execution, or live trading is performed. CI on Ubuntu /
Python 3.11 is configured but has not run on GitHub as of this draft. Update the
hosted verification status from actual results before publishing the release.
