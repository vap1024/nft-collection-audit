from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path

import pytest

from nft_audit.tracker import (
    PricePoint,
    TRACKING_SCHEDULE,
    load_price_series,
    parse_timestamp,
    render_tracking_table,
    track_prices,
)

MINT = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[1]


def point(seconds, price):
    return PricePoint(MINT + timedelta(seconds=seconds), Decimal(str(price)))


def test_monotonic_series_has_positive_changes_at_exact_schedule():
    expected_minutes = [1, 30, 60, 180, 240, 360, 1440, 2880, 4320, 10080, 20160, 43200]
    series = [point(minutes * 60, 101 + index) for index, minutes in enumerate(expected_minutes)]
    rows = track_prices(MINT, 100, reversed(series))
    assert len(rows) == 12
    assert [row.label for row in rows] == ["1m", "30m", "60m", "180m", "240m", "360m", "1d", "2d", "3d", "7d", "14d", "30d"]
    assert [row.target_time for row in rows] == [MINT + timedelta(minutes=value) for value in expected_minutes]
    assert all(row.sample_time == row.target_time for row in rows)
    assert all(row.change_pct > 0 for row in rows)
    assert all(row.offset_seconds == 0 for row in rows)


def test_actual_fixture_matches_all_targets_with_small_offsets():
    payload = json.loads((ROOT / "data" / "price_series.json").read_text(encoding="utf-8"))
    mint, baseline, series = load_price_series(payload)
    rows = track_prices(mint, baseline, series, max_distance=timedelta(minutes=1))
    assert len(TRACKING_SCHEDULE) == 12
    assert [row.sample_time for row in rows] == [sample.timestamp for sample in series]
    assert [row.offset_seconds for row in rows] == [5, -10, 20, 10, -20, 30, 10, -10, 20, 10, -10, 30]
    assert all(row.change_pct > 0 for row in rows)
    assert rows[-1].change_pct == Decimal(90)
    table = render_tracking_table(rows)
    assert "+90.00%" in table
    assert "Offset (s)" in table
    assert len(table.splitlines()) == 14


def test_nearest_sample_is_selected_including_sample_after_target():
    rows = track_prices(MINT, 100, [point(50, 105), point(64, 110), point(100, 120)])
    assert rows[0].sample_time == MINT + timedelta(seconds=64)
    assert rows[0].offset_seconds == 4
    assert rows[0].change_pct == 10


def test_equal_distance_tie_uses_earlier_observation():
    rows = track_prices(MINT, 100, [point(70, 120), point(50, 110)])
    assert rows[0].sample_time == MINT + timedelta(seconds=50)
    assert rows[0].price == 110


def test_pre_mint_data_cannot_be_used():
    rows = track_prices(MINT, 100, [point(-1, 1000)])
    assert all(row.sample_time is None for row in rows)


def test_empty_series_preserves_all_schedule_rows():
    rows = track_prices(MINT, 100, [])
    assert len(rows) == 12
    assert all(row.sample_time is None and row.change_pct is None for row in rows)
    assert render_tracking_table(rows).count("unavailable") == 12


def test_max_distance_rejects_distant_samples_and_includes_boundary():
    rows = track_prices(MINT, 100, [point(90, 110)], max_distance=timedelta(seconds=30))
    assert rows[0].sample_time == MINT + timedelta(seconds=90)
    assert all(row.sample_time is None for row in rows[1:])


def test_sparse_series_reuses_sample_but_reports_deviation():
    rows = track_prices(MINT, 100, [point(60, 105)])
    assert len({row.sample_time for row in rows}) == 1
    assert rows[-1].offset_seconds == Decimal(60 - 30 * 86400)


def test_falling_and_zero_prices_have_correct_changes():
    rows = track_prices(MINT, 100, [point(60, 90), point(1800, 0)])
    assert rows[0].change_pct == -10
    assert rows[1].change_pct == -100


@pytest.mark.parametrize("baseline", [0, -1, None, True, float("nan"), float("inf")])
def test_invalid_mint_baseline_is_rejected(baseline):
    with pytest.raises(ValueError, match="mint_price"):
        track_prices(MINT, baseline, [])


@pytest.mark.parametrize("price", [-1, None, True, float("nan"), float("inf")])
def test_invalid_observed_price_is_rejected(price):
    with pytest.raises(ValueError, match="price"):
        PricePoint(MINT, price)


def test_duplicate_timestamps_are_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        track_prices(MINT, 100, [point(60, 110), point(60, 120)])


def test_naive_timestamps_are_rejected():
    with pytest.raises(ValueError, match="timezone"):
        PricePoint(datetime(2026, 1, 1), Decimal(1))
    with pytest.raises(ValueError, match="timezone"):
        track_prices(datetime(2026, 1, 1), 100, [])
    with pytest.raises(ValueError, match="timezone"):
        parse_timestamp("2026-01-01T12:00:00")


def test_timezone_offsets_are_normalized_to_utc():
    other_zone = timezone(timedelta(hours=2))
    local_mint = MINT.astimezone(other_zone)
    observation = PricePoint((MINT + timedelta(seconds=60)).astimezone(other_zone), 110)
    row = track_prices(local_mint, 100, [observation])[0]
    assert row.target_time.tzinfo == timezone.utc
    assert row.sample_time.tzinfo == timezone.utc
    assert row.offset_seconds == 0
    assert parse_timestamp("2026-01-01T14:00:00+02:00") == MINT


def test_negative_max_distance_is_rejected():
    with pytest.raises(ValueError, match="max_distance"):
        track_prices(MINT, 100, [], max_distance=timedelta(seconds=-1))


def test_price_fixture_must_be_synthetic():
    with pytest.raises(ValueError, match="synthetic=true"):
        load_price_series({"synthetic": False})
