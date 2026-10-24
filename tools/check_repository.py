"""Audit distributable files for accidental live data and unsupported imports."""

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


IGNORED_DIRECTORIES = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "demo-output"}
WORD_PATTERN = re.compile("pass" + "word|sec" + "ret|api" + "_key", re.I)
EVM_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
BASE58_PATTERN = re.compile(r"(?<![A-Za-z0-9])[1-9A-HJ-NP-Za-km-z]{32,44}(?![A-Za-z0-9])")
AUTH_PATTERN = re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")
URL_PATTERN = re.compile(r"(?:https?|wss?|ftp)://[^\s<>\"'`)]+", re.I)
PUBLIC_REPOSITORIES = {"nft-collection-audit", "l2-project-audit", "codex-ops-system"}


@dataclass(frozen=True)
class RepositoryFinding:
    path: str
    line: int
    rule: str


def is_public_documentation_link(url: str) -> bool:
    """Allow only the explicit publication/toolchain links required by the brief."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or "@" in parsed.netloc or parsed.query or parsed.fragment:
        return False
    if parsed.netloc == "img.shields.io":
        return parsed.path == "/badge/license-MIT-blue.svg"
    if parsed.netloc != "github.com":
        return False
    parts = parsed.path.strip("/").split("/")
    return (
        len(parts) >= 2 and parts[0] == "vap1024"
        and parts[1].removesuffix(".git") in PUBLIC_REPOSITORIES
    )


def audit_repository_files(root: Path) -> tuple[int, tuple[RepositoryFinding, ...]]:
    """Scan every delivered text file, omitting Git internals and local caches.

    Findings include positions and rule names only, so a bad value is never
    copied to command output. Explicit public documentation links are allowed;
    application service endpoints are not.
    """
    findings: list[RepositoryFinding] = []
    count = 0
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in IGNORED_DIRECTORIES for part in relative.parts[:-1]):
            continue
        count += 1
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            findings.append(RepositoryFinding(relative.as_posix(), 1, "unreadable text file"))
            continue
        for label, pattern in (
            ("prohibited credential term", WORD_PATTERN),
            ("EVM-style address", EVM_PATTERN),
            ("Base58-style address", BASE58_PATTERN),
            ("authentication material", AUTH_PATTERN),
        ):
            for match in pattern.finditer(text):
                findings.append(RepositoryFinding(relative.as_posix(), text.count("\n", 0, match.start()) + 1, label))
        for match in URL_PATTERN.finditer(text):
            if not is_public_documentation_link(match.group()):
                findings.append(RepositoryFinding(relative.as_posix(), text.count("\n", 0, match.start()) + 1, "unapproved service URL"))
        if path.suffix == ".py":
            try:
                tree = ast.parse(text, filename=str(relative), feature_version=(3, 11))
            except SyntaxError:
                findings.append(RepositoryFinding(relative.as_posix(), 1, "Python 3.11 syntax"))
                continue
            if relative.parts[0] == "src":
                for node in ast.walk(tree):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.level == 0:
                        names = [node.module]
                    if any(name.split(".")[0] not in sys.stdlib_module_names for name in names):
                        findings.append(RepositoryFinding(relative.as_posix(), node.lineno, "non-stdlib application import"))
    return count, tuple(findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    count, findings = audit_repository_files(args.root.resolve())
    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.rule}")
    print(f"Audited {count} files; {len(findings)} findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
