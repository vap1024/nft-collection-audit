"""Version 1 scoring: four equally weighted, explainable components."""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from .features import CollectionFeatures, extract_features

CANDIDATE_THRESHOLD = Decimal("7.00")
_ZERO = Decimal(0)
_TEN = Decimal(10)


@dataclass(frozen=True)
class ComponentScore:
    name: str
    points: Decimal
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class AuditResult:
    features: CollectionFeatures
    components: tuple[ComponentScore, ...]
    score: Decimal

    @property
    def candidate(self) -> bool:
        return self.score >= CANDIDATE_THRESHOLD


def _component(name: str, points: Decimal, reasons: list[str]) -> ComponentScore:
    return ComponentScore(name, min(_TEN, max(_ZERO, points)), tuple(reasons))


def _liquidity(f: CollectionFeatures) -> ComponentScore:
    points = _ZERO
    reasons: list[str] = []
    floor_ok = f.floor_price is not None and f.floor_price > 0
    volume_ok = f.volume_24h is not None and f.volume_24h > 0
    points += Decimal(4) if floor_ok else _ZERO
    points += Decimal(4) if volume_ok else _ZERO
    points += Decimal(2) if floor_ok and volume_ok else _ZERO
    reasons.append("Positive primary floor: +4." if floor_ok else "Missing or zero primary floor: +0.")
    reasons.append("Positive primary 24h volume: +4." if volume_ok else "Missing or zero primary 24h volume: +0.")
    if floor_ok and volume_ok:
        reasons.append("Both market fields are present and positive: +2.")
    loud = f.high_liquidity_claim or (
        f.claimed_volume_24h is not None and f.claimed_volume_24h >= 1000
    )
    if loud and not (floor_ok and volume_ok):
        points -= 4
        reasons.append("Loud liquidity claim with incomplete primary market data: -4.")
    if (
        f.claimed_volume_24h is not None
        and f.volume_24h is not None
        and f.claimed_volume_24h > 2 * f.volume_24h
    ):
        points -= 2
        reasons.append("Claimed volume exceeds twice the primary volume: -2.")
    return _component("Liquidity and floor", points, reasons)


def _mint(f: CollectionFeatures) -> ComponentScore:
    points = _ZERO
    reasons: list[str] = []
    rules = (
        (f.mint_price is not None, 3, "Mint price disclosed (including a free mint)"),
        (f.stages is not None, 2, "Stage count disclosed"),
        (f.allowlist is not None, 1, "Allowlist policy explicitly disclosed"),
        (f.terms_disclosed is True, 2, "Terms transparent"),
        (f.terms_changed is False, 2, "Terms unchanged in the fixture review"),
    )
    for condition, award, label in rules:
        points += Decimal(award) if condition else _ZERO
        reasons.append(f"{label}: +{award if condition else 0}.")
    if f.terms_disclosed is False:
        points -= 5
        reasons.append("Hidden terms: -5.")
    if f.terms_changed is True:
        points -= 4
        reasons.append("Changing terms: -4.")
    return _component("Mint terms", points, reasons)


def _trading(f: CollectionFeatures) -> ComponentScore:
    if f.top_wallet_volume_share is None or f.circular_trade_share is None:
        return _component("Wash-trading risk", _ZERO, ["Incomplete primary trade summary: +0."])
    concentration_penalty = min(Decimal(8), max(_ZERO, (f.top_wallet_volume_share - Decimal("0.30")) * 20))
    circular_penalty = min(_TEN, f.circular_trade_share * 30)
    return _component(
        "Wash-trading risk",
        _TEN - concentration_penalty - circular_penalty,
        [
            "Complete primary trade summary: +10 before risk deductions.",
            f"Concentrated volume penalty: -{concentration_penalty:.2f}.",
            f"Circular-trade penalty: -{circular_penalty:.2f}.",
        ],
    )


def _contract(f: CollectionFeatures) -> ComponentScore:
    points = _ZERO
    reasons: list[str] = []
    if f.source_verified is True:
        points += 4
        reasons.append("Source verified in the primary fixture review: +4.")
    else:
        reasons.append("Source verification absent or negative: +0.")
    if f.source_verified is True and f.mint_method in {"standard", "seadrop"}:
        points += 6
        reasons.append("Verified source and standard mint method: +6.")
    elif f.mint_method in {"custom", "opaque"}:
        points -= 4
        reasons.append("Custom or opaque mint method: -4.")
    else:
        reasons.append("No verified standard mint evidence: +0.")
    return _component("Contract risk", points, reasons)


def score_collection(collection: Mapping[str, Any] | CollectionFeatures) -> AuditResult:
    """Clamp each component to 0..10, average, round half-up, then apply the gate."""
    features = collection if isinstance(collection, CollectionFeatures) else extract_features(collection)
    components = tuple(rule(features) for rule in (_liquidity, _mint, _trading, _contract))
    score = (sum((item.points for item in components), _ZERO) / 4).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return AuditResult(features, components, score)
