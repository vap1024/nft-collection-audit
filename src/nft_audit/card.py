"""Markdown collection cards, including evidence provenance and score reasons."""

from .scoring import AuditResult, CANDIDATE_THRESHOLD


def _text(value: str) -> str:
    return value.replace("|", "&#124;").replace("\n", " ").replace("\r", " ")


def render_card(result: AuditResult) -> str:
    status = "CANDIDATE" if result.candidate else "REJECTED"
    f = result.features
    lines = [
        f"## {_text(f.name)}",
        "",
        f"Synthetic collection: `{_text(f.collection_id)}`",
        "Demo data: synthetic fixtures",
        "",
        f"**Score: {result.score:.2f}/10 - {status}** (candidate gate: >= {CANDIDATE_THRESHOLD:.2f}).",
        "Research scoring model. Not investment advice.",
        "",
        "| Component | Points / 10 | Weight |",
        "| --- | ---: | ---: |",
    ]
    for component in result.components:
        lines.append(f"| {component.name} | {component.points:.2f} | 25% |")
    lines.extend(["", "### Score explanation", ""])
    for component in result.components:
        lines.append(f"- **{component.name}:** " + " ".join(component.reasons))
    lines.extend(["", "### Primary fixture references", ""])
    if f.source_ids:
        lines.extend(f"- {_text(section)}: `{_text(source_id)}`" for section, source_id in f.source_ids)
    else:
        lines.append("- No resolved primary fixture records.")
    if f.warnings:
        lines.extend(["", "### Evidence warnings", ""])
        lines.extend(f"- {_text(warning)}" for warning in f.warnings)
    lines.extend(["", "Offline model output; candidate status requests human review."])
    return "\n".join(lines)
