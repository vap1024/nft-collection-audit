"""Validate JSON fields and resolve primary fixture records independently of claims."""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


def number(value: Any, field: str, *, maximum: Decimal | None = None) -> Decimal | None:
    """Read a finite, nonnegative JSON number; null means missing evidence."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError(f"{field} must be a number or null")
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{field} must be finite") from error
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field} must be finite and nonnegative")
    if maximum is not None and result > maximum:
        raise ValueError(f"{field} must be at most {maximum}")
    return result


def _flag(value: Any, field: str) -> bool | None:
    if value is not None and not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean or null")
    return value


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


@dataclass(frozen=True)
class CollectionFeatures:
    collection_id: str
    name: str
    floor_price: Decimal | None
    volume_24h: Decimal | None
    claimed_volume_24h: Decimal | None
    high_liquidity_claim: bool
    mint_price: Decimal | None
    stages: int | None
    allowlist: bool | None
    terms_disclosed: bool | None
    terms_changed: bool | None
    top_wallet_volume_share: Decimal | None
    circular_trade_share: Decimal | None
    source_verified: bool | None
    mint_method: str | None
    source_ids: tuple[tuple[str, str], ...]
    warnings: tuple[str, ...]


def extract_features(collection: Mapping[str, Any]) -> CollectionFeatures:
    """Resolve typed records; a missing or mismatched reference earns no evidence."""
    collection = _mapping(collection, "collection")
    if collection.get("synthetic") is not True:
        raise ValueError("collection must explicitly declare synthetic=true")
    for field in ("id", "name"):
        if not isinstance(collection.get(field), str) or not collection[field].strip():
            raise ValueError(f"{field} must be a nonempty string")
    claims = _mapping(collection.get("claims", {}), "claims")
    sources = _mapping(collection.get("sources", {}), "sources")
    refs = _mapping(collection.get("evidence_refs", {}), "evidence_refs")
    warnings: list[str] = []
    used: list[tuple[str, str]] = []

    def resolve(section: str, kind: str) -> Mapping[str, Any]:
        ref = refs.get(section)
        if ref is None:
            warnings.append(f"Missing {section} primary fixture record.")
            return {}
        if not isinstance(ref, str):
            raise ValueError(f"evidence_refs.{section} must be a string")
        record = sources.get(ref)
        if not isinstance(record, Mapping) or record.get("kind") != kind:
            warnings.append(f"Unresolved or wrong-kind {section} reference: {ref}.")
            return {}
        if record.get("synthetic") is not True:
            raise ValueError(f"Source {ref} must explicitly declare synthetic=true")
        used.append((section, ref))
        return record

    market = resolve("market", "market_snapshot")
    mint = resolve("mint", "mint_terms")
    trading = resolve("trading", "trade_summary")
    contract = resolve("contract", "contract_review")
    stages = mint.get("stages")
    if stages is not None and (
        isinstance(stages, bool) or not isinstance(stages, int) or not 1 <= stages <= 20
    ):
        raise ValueError("mint.stages must be an integer from 1 to 20 or null")
    method = contract.get("mint_method")
    if method is not None and method not in {"standard", "seadrop", "custom", "opaque"}:
        raise ValueError("contract.mint_method is not a supported category")
    return CollectionFeatures(
        collection_id=collection["id"],
        name=collection["name"],
        floor_price=number(market.get("floor_price"), "market.floor_price"),
        volume_24h=number(market.get("volume_24h"), "market.volume_24h"),
        claimed_volume_24h=number(claims.get("volume_24h"), "claims.volume_24h"),
        high_liquidity_claim=_flag(claims.get("high_liquidity"), "claims.high_liquidity") is True,
        mint_price=number(mint.get("price"), "mint.price"),
        stages=stages,
        allowlist=_flag(mint.get("allowlist"), "mint.allowlist"),
        terms_disclosed=_flag(mint.get("terms_disclosed"), "mint.terms_disclosed"),
        terms_changed=_flag(mint.get("terms_changed"), "mint.terms_changed"),
        top_wallet_volume_share=number(
            trading.get("top_wallet_volume_share"), "trading.top_wallet_volume_share", maximum=Decimal(1)
        ),
        circular_trade_share=number(
            trading.get("circular_trade_share"), "trading.circular_trade_share", maximum=Decimal(1)
        ),
        source_verified=_flag(contract.get("source_verified"), "contract.source_verified"),
        mint_method=method,
        source_ids=tuple(used),
        warnings=tuple(warnings),
    )
