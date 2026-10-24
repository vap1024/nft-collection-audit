# Retrospective price tracker

Targets are exactly 1/30/60/180/240/360 minutes and 1/2/3/7/14/30 days after
mint. For a strictly positive mint price:

```text
change_pct = (sample_price - mint_price) / mint_price * 100
```

Timezone-aware observations may arrive in any order. The tracker normalizes to
UTC, ignores pre-mint observations, and chooses the closest post-mint sample.
Equal-distance ties select the earlier observation. Duplicate timestamps are
rejected. Zero observed prices are valid (-100%); a zero baseline is undefined.

This is retrospective matching: a later observation may be selected and one
observation may serve several targets. The table prints target time, actual
sample time, signed offset, price, and change. The default has no distance limit;
call `track_prices(..., max_distance=timedelta(minutes=1))` to reject distant
samples. Empty inputs and rejected observations retain the scheduled rows with
`unavailable` values.

The demo deliberately uses nonzero timestamp offsets and uneven increasing
prices. The tracker shows changes from mint price, excluding fees and execution
costs; it is not executable trading performance.
