import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repository_checks", ROOT / "tools" / "check_repository.py")
CHECKS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKS
SPEC.loader.exec_module(CHECKS)


@pytest.mark.parametrize("content, rule", [
    ("pass" + "word=example", "prohibited credential term"),
    ("0" + "x" + "1" * 40, "EVM-style address"),
    ("2" * 44, "Base58-style address"),
    ("ghp_" + "X" * 36, "authentication material"),
    ("https" + "://private.example.invalid/data", "unapproved service URL"),
])
def test_repository_audit_detects_unpublishable_material(tmp_path, content, rule):
    (tmp_path / "example.txt").write_text(content, encoding="utf-8")
    count, findings = CHECKS.audit_repository_files(tmp_path)
    assert count == 1
    assert any(finding.rule == rule for finding in findings)


def test_repository_audit_checks_imports_and_syntax(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "unsupported.py").write_text("import external_sdk\n", encoding="utf-8")
    (source / "invalid.py").write_text("def broken(\n", encoding="utf-8")
    _, findings = CHECKS.audit_repository_files(tmp_path)
    assert {item.rule for item in findings} == {"non-stdlib application import", "Python 3.11 syntax"}


def test_only_named_public_repository_links_are_allowed():
    base = "https" + "://github.com/vap1024/"
    assert CHECKS.is_public_documentation_link(base + "codex-ops-system/blob/main/docs/PROTOCOL.md")
    assert CHECKS.is_public_documentation_link(base + "nft-collection-audit.git")
    assert not CHECKS.is_public_documentation_link(base + "unrelated-private-project")
    assert not CHECKS.is_public_documentation_link(base + "nft-collection-audit?access=example")
