import copy
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys

import pytest

from nft_audit.card import render_card
from nft_audit.features import extract_features
from nft_audit.scoring import CANDIDATE_THRESHOLD, score_collection

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def collections():
    return json.loads((ROOT / "data" / "collections.json").read_text(encoding="utf-8"))


def source(collection, section):
    return collection["sources"][collection["evidence_refs"][section]]


@pytest.mark.parametrize("index, expected, candidate", [(0, "9.85", True), (1, "6.55", False), (2, "0.00", False)])
def test_demo_collection_gates(collections, index, expected, candidate):
    result = score_collection(collections[index])
    assert result.score == Decimal(expected)
    assert result.candidate is candidate
    assert len(result.components) == 4
    assert all(0 <= component.points <= 10 for component in result.components)


def test_empty_floor_with_loud_volume_reduces_score(collections):
    baseline = score_collection(collections[0])
    source(collections[0], "market")["floor_price"] = None
    result = score_collection(collections[0])
    assert result.score < baseline.score
    assert result.components[0].points == 0
    assert "Loud liquidity claim" in render_card(result)


def test_loud_claim_itself_penalizes_incomplete_market_data(collections):
    collection = collections[0]
    source(collection, "market")["floor_price"] = None
    loud = score_collection(collection)
    collection["claims"] = {"volume_24h": 10, "high_liquidity": False}
    quiet = score_collection(collection)
    assert quiet.score - loud.score == Decimal("1.00")


def test_promotion_cannot_fill_empty_primary_market_fields(collections):
    collection = collections[0]
    source(collection, "market").update(floor_price=None, volume_24h=None)
    collection["claims"].update(floor_price=100, volume_24h=100000)
    result = score_collection(collection)
    assert result.features.floor_price is None
    assert result.features.volume_24h is None
    assert result.components[0].points == 0


def test_exaggerated_volume_costs_points(collections):
    baseline = score_collection(collections[0])
    collections[0]["claims"]["volume_24h"] = 100000
    assert score_collection(collections[0]).score == baseline.score - Decimal("0.50")


@pytest.mark.parametrize("field, value", [("terms_disclosed", False), ("terms_changed", True), ("price", None)])
def test_problematic_mint_terms_reduce_score(collections, field, value):
    baseline = score_collection(collections[0])
    source(collections[0], "mint")[field] = value
    assert score_collection(collections[0]).score < baseline.score


def test_free_mint_and_public_allowlist_policy_are_disclosed(collections):
    baseline = score_collection(collections[0])
    source(collections[0], "mint").update(price=0, allowlist=False)
    assert score_collection(collections[0]).score == baseline.score


@pytest.mark.parametrize("field, value", [("top_wallet_volume_share", 0.95), ("circular_trade_share", 0.8)])
def test_wash_trading_risk_materially_reduces_score(collections, field, value):
    baseline = score_collection(collections[0])
    source(collections[0], "trading")[field] = value
    assert baseline.score - score_collection(collections[0]).score >= Decimal("1.85")


@pytest.mark.parametrize("method, verified", [("opaque", False), ("custom", True), ("standard", False)])
def test_untrusted_contract_is_penalized(collections, method, verified):
    source(collections[0], "contract").update(mint_method=method, source_verified=verified)
    assert score_collection(collections[0]).components[3].points == 0


@pytest.mark.parametrize("section", ["market", "mint", "trading", "contract"])
def test_unresolved_evidence_cannot_earn_component_points(collections, section):
    collections[0]["evidence_refs"][section] = "missing-fixture"
    result = score_collection(collections[0])
    index = ("market", "mint", "trading", "contract").index(section)
    assert result.components[index].points == 0
    assert result.features.warnings
    assert "missing-fixture" in render_card(result)


def test_wrong_kind_source_is_not_accepted(collections):
    source(collections[0], "market")["kind"] = "promotional_card"
    result = score_collection(collections[0])
    assert result.components[0].points == 0
    assert "wrong-kind" in result.features.warnings[0]


def test_missing_all_evidence_is_zero(collections):
    collections[0].pop("evidence_refs")
    result = score_collection(collections[0])
    assert result.score == 0
    assert not result.candidate
    assert len(result.features.warnings) == 4
    assert "No resolved primary fixture records" in render_card(result)


@pytest.mark.parametrize("score, candidate", [("6.99", False), ("7.00", True), ("7.01", True)])
def test_gate_is_inclusive_at_seven(collections, score, candidate):
    result = replace(score_collection(collections[0]), score=Decimal(score))
    assert CANDIDATE_THRESHOLD == Decimal("7.00")
    assert result.candidate is candidate


def test_scores_are_bounded_and_decimal_rounding_is_explicit(collections):
    source(collections[0], "trading").update(top_wallet_volume_share=0, circular_trade_share=0.001)
    assert score_collection(collections[0]).score == Decimal("9.99")
    source(collections[0], "trading")["circular_trade_share"] = 0
    assert score_collection(collections[0]).score == Decimal("10.00")


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True, "1.2"])
def test_invalid_market_numbers_are_rejected(collections, value):
    source(collections[0], "market")["floor_price"] = value
    with pytest.raises(ValueError, match="market.floor_price"):
        extract_features(collections[0])


@pytest.mark.parametrize("field, value", [("top_wallet_volume_share", 1.01), ("circular_trade_share", -0.1)])
def test_invalid_trade_shares_are_rejected(collections, field, value):
    source(collections[0], "trading")[field] = value
    with pytest.raises(ValueError, match=field):
        extract_features(collections[0])


@pytest.mark.parametrize("field, value", [("allowlist", "yes"), ("terms_changed", 0), ("stages", 0), ("stages", True)])
def test_invalid_mint_types_are_rejected(collections, field, value):
    source(collections[0], "mint")[field] = value
    with pytest.raises(ValueError, match=field):
        extract_features(collections[0])


@pytest.mark.parametrize("section", [None, "market"])
def test_synthetic_declaration_is_required(collections, section):
    target = collections[0] if section is None else source(collections[0], section)
    target["synthetic"] = False
    with pytest.raises(ValueError, match="synthetic=true"):
        score_collection(collections[0])


def test_scoring_does_not_mutate_input_and_card_shows_provenance(collections):
    before = copy.deepcopy(collections[0])
    result = score_collection(collections[0])
    assert collections[0] == before
    card = render_card(result)
    assert "9.85/10 - CANDIDATE" in card
    assert "aurora-market-v1" in card
    assert "Circular-trade penalty" in card
    assert card.count("25%") == 4


def test_demo_runs_outside_project_and_saves_identical_report(tmp_path):
    destination = tmp_path / "nested" / "report.md"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "run_demo.py"), "--output", str(destination)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert destination.read_text(encoding="utf-8") == completed.stdout
    assert completed.stdout.count("/10 - CANDIDATE") == 1
    assert completed.stdout.count("/10 - REJECTED") == 2
    assert "| 30d |" in completed.stdout
    assert "+90.00%" in completed.stdout


@pytest.mark.parametrize("index", [0, 1, 2])
def test_each_scorecard_discloses_synthetic_data_and_research_model(collections, index):
    card = render_card(score_collection(collections[index]))
    assert "Demo data: synthetic fixtures" in card
    score_line = next(i for i, line in enumerate(card.splitlines()) if line.startswith("**Score:"))
    assert card.splitlines()[score_line + 1] == "Research scoring model. Not investment advice."
