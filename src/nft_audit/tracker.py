"""Retrospective nearest-snapshot tracking, with explicit sampling offsets."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from .features import number

TRACKING_SCHEDULE: tuple[tuple[str, timedelta], ...] = tuple(
    [(f"{minutes}m", timedelta(minutes=minutes)) for minutes in (1, 30, 60, 180, 240, 360)]
    + [(f"{days}d", timedelta(days=days)) for days in (1, 2, 3, 7, 14, 30)]
)


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must include a timezone")
    return value.astimezone(timezone.utc)


def parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamps must be ISO 8601 strings")
    return _utc(datetime.fromisoformat(value.replace("Z", "+00:00")))


@dataclass(frozen=True)
class PricePoint:
    timestamp: datetime
    price: Decimal

    def __post_init__(self) -> None:
        value = number(self.price, "price")
        if value is None:
            raise ValueError("price must be present")
        object.__setattr__(self, "timestamp", _utc(self.timestamp))
        object.__setattr__(self, "price", value)


@dataclass(frozen=True)
class TrackingPoint:
    label: str
    target_time: datetime
    sample_time: datetime | None
    price: Decimal | None
    change_pct: Decimal | None
    offset_seconds: Decimal | None


def load_price_series(payload: Mapping[str, Any]) -> tuple[datetime, Decimal, tuple[PricePoint, ...]]:
    """Read the standalone synthetic fixture format used by the demo."""
    if not isinstance(payload, Mapping) or payload.get("synthetic") is not True:
        raise ValueError("price series must explicitly declare synthetic=true")
    mint_time = parse_timestamp(payload["mint_time"])
    mint_price = number(payload["mint_price"], "mint_price")
    if mint_price is None or mint_price <= 0:
        raise ValueError("mint_price must be positive for percentage calculations")
    points = tuple(
        PricePoint(parse_timestamp(item["time"]), item["price"])
        for item in payload["points"]
    )
    return mint_time, mint_price, points


def track_prices(
    mint_time: datetime,
    mint_price: Decimal | int | float,
    series: Iterable[PricePoint],
    *,
    max_distance: timedelta | None = None,
) -> tuple[TrackingPoint, ...]:
    """Pick the nearest post-mint sample; earlier samples win equal-distance ties.

    The same sample may serve multiple targets. A later sample may be selected;
    this is retrospective analysis. Set max_distance to reject distant samples.
    """
    mint_time = _utc(mint_time)
    baseline = number(mint_price, "mint_price")
    if baseline is None or baseline <= 0:
        raise ValueError("mint_price must be positive for percentage calculations")
    if max_distance is not None and max_distance < timedelta(0):
        raise ValueError("max_distance must be nonnegative")
    all_points = tuple(series)
    if len({point.timestamp for point in all_points}) != len(all_points):
        raise ValueError("duplicate sample timestamps are ambiguous")
    points = tuple(point for point in all_points if point.timestamp >= mint_time)
    rows: list[TrackingPoint] = []
    for label, elapsed in TRACKING_SCHEDULE:
        target = mint_time + elapsed
        sample = min(
            points, key=lambda point: (abs(point.timestamp - target), point.timestamp), default=None
        )
        if sample is None or (
            max_distance is not None and abs(sample.timestamp - target) > max_distance
        ):
            rows.append(TrackingPoint(label, target, None, None, None, None))
            continue
        rows.append(TrackingPoint(
            label,
            target,
            sample.timestamp,
            sample.price,
            (sample.price - baseline) / baseline * 100,
            Decimal(str((sample.timestamp - target).total_seconds())),
        ))
    return tuple(rows)


def render_tracking_table(rows: Iterable[TrackingPoint], *, currency: str = "DEMO") -> str:
    """Render target, actual sample, deviation, price, and change from mint."""
    currency = currency.replace("|", "&#124;").replace("\n", " ").replace("\r", " ")
    lines = [
        f"| Target | Target time (UTC) | Sample time (UTC) | Offset (s) | Price ({currency}) | Change vs mint |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        target = row.target_time.isoformat()
        if row.sample_time is None:
            lines.append(f"| {row.label} | {target} | unavailable | n/a | n/a | n/a |")
        else:
            lines.append(
                f"| {row.label} | {target} | {row.sample_time.isoformat()} | "
                f"{row.offset_seconds:+.0f} | {row.price:.4f} | {row.change_pct:+.2f}% |"
            )
    return "\n".join(lines)
