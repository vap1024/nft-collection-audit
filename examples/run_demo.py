"""Print three audit cards and a price-tracking table; optionally save Markdown."""

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nft_audit.card import render_card  # noqa: E402
from nft_audit.scoring import score_collection  # noqa: E402
from nft_audit.tracker import load_price_series, render_tracking_table, track_prices  # noqa: E402


def build_report() -> str:
    collections = json.loads((PROJECT_ROOT / "data" / "collections.json").read_text(encoding="utf-8"))
    payload = json.loads((PROJECT_ROOT / "data" / "price_series.json").read_text(encoding="utf-8"))
    results = [score_collection(collection) for collection in collections]
    matching = next((item for item in results if item.features.collection_id == payload["collection_id"]), None)
    if matching is None:
        raise ValueError("tracked collection is absent from collection fixtures")
    mint_time, mint_price, prices = load_price_series(payload)
    if matching.features.mint_price != mint_price:
        raise ValueError("tracker baseline must match the primary mint terms")
    rows = track_prices(mint_time, mint_price, prices)
    parts = ["# Synthetic NFT collection audit", "All prices use fictional DEMO units."]
    parts.extend(render_card(result) for result in results)
    parts.extend([
        "## Post-mint price tracker",
        f"Collection: `{payload['collection_id']}`. Mint price: {mint_price:.4f} DEMO.",
        "Nearest post-mint samples; positive offsets mean observations after the target time.",
        render_tracking_table(rows, currency=payload["currency"]),
    ])
    return "\n\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="also save the full Markdown report to this local path")
    args = parser.parse_args()
    report = build_report()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
