# Evidence and input format

Demo data: synthetic fixtures

`data/collections.json` contains three fictional collections, each with
`synthetic: true`, promotional `claims`, typed `sources`, and `evidence_refs`.
References resolve named primary fixture entries. Missing or wrong-kind entries
yield missing evidence and a warning; their claims cannot substitute for records.

| Reference | Required source kind | Fields |
| --- | --- | --- |
| market | market_snapshot | floor_price, volume_24h |
| mint | mint_terms | price, stages, allowlist, terms_disclosed, terms_changed |
| trading | trade_summary | top_wallet_volume_share, circular_trade_share |
| contract | contract_review | source_verified, mint_method |

Every referenced source explicitly declares `synthetic: true`. A source ID is
local provenance, not proof of authenticity outside the demo. All prices and
volume values use fictional DEMO units.

Null means missing. Numbers must be finite and nonnegative; shares are in 0..1.
Stages are an integer from 1 through 20. Flags are actual booleans. An explicit
`allowlist: false` is a disclosed public policy and earns the same disclosure
point as `true`. A disclosed zero mint price denotes a free mint.

Aurora Gardens has complete favorable records; Mist Arcade has changing terms
and enough trading concentration to fall just short of the gate; Paper Comets
combines loud claims, empty market fields, opaque mint terms, a risky contract
finding, and severe concentration. The date and price series are fictional and
retrospective.
