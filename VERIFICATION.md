# Local verification and remaining acceptance

Prepared and checked on 2026-10-24, Europe/Kiev. Scope: this repository only.
The replacement brief superseded the earlier local-only brief on this date.

## Completed local checks

- **78 passed**, zero skipped, using `python -m pytest` with Windows,
  Python 3.13.15, pytest 9.1.1. There are 46 scoring/evidence/demo cases,
  25 tracker cases, and 7 repository-file cases.
- Requirements pin pytest to the exact tested version. The runtime application
  uses only standard-library imports; Python 3.11 grammar checks pass.
- A fresh local Git clone was used to verify installation, the demo, pytest,
  and repository-file checks. This does not verify the future public clone URL.
- `python examples/run_demo.py` regenerates
  `examples/output/scorecards.md`. It contains all three cards and 12 tracker
  targets, with the exact synthetic marker inside the outputs and the research
  disclaimer beside every gate score. Export explicitly writes LF; regeneration
  leaves both the sample content and the clean clone's Git status unchanged.
- Fixture scores are 9.78, 6.95, and 0.22. The increasing tracker series spans
  +1.07% through +93.88%; dates, prices, and source records are all fictional.
- The actual disclosure regression/fix has recorded before/after results in
  `docs/audit/2026-10-24-results.md`: 3 failed before, 3 passed after.
- `python tools/check_repository.py` reports zero findings. It checks delivered
  text, address-like values, credential-related terms, application imports, and
  unsupported endpoints. Only explicit public toolchain/CI/license documentation
  links are allowed; Git internals and local environments are outside the scan.
- The README follows the required section order and has exactly two badges.
- A single-job Ubuntu/Python 3.11 workflow is present. Its definition was checked
  locally; it has not executed on GitHub.
- Local commits record actual work on 24 October with Git-generated timestamps;
  no commit dates were overridden. The initial commit honestly imports an
  existing verified implementation. Later commits record new tests, the fix,
  CI/checks, refreshed fixtures/sample, and publication documentation. A seventh
  real fix addresses the Windows newline issue found during the clean-clone check.

## Pending external or future checks

| Requirement | Actual status on 2026-10-24 | Next step |
| --- | --- | --- |
| Public repository and clone quickstart | Not published or verified | Publish and run on/after 27 October |
| Hosted CI on Ubuntu / Python 3.11 | Definition ready; no run | Wait for actual GitHub result after push |
| About, topics, v0.1.0 release | Payload and release notes prepared | Apply and verify on/after 27 October |
| Public cross-links | Intended destinations present; availability unverified | Check both repositories and flagship protocol after publication |
| Profile UI and pins | User actions not performed | User handles on 28 October |
| Final anonymous reviewer pass | Not performed | Complete on 29 October |

GitHub CLI is not installed here. No authenticated account was used during this
preparation, no repository was created remotely, and no automated future task was
configured. Publication instructions and the exact metadata are in `publication/`.

Python 3.11 and Ubuntu execution are not available locally. They remain part of
the honest hosted-CI acceptance, not a completed local claim.
