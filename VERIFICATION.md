# Local verification

Verified on 2026-10-24 on Windows with Python 3.13.15 and pytest 9.1.1.
The application targets Python 3.11+. Execution on Python 3.11 itself was not
available; all Python files were additionally parsed using the 3.11 grammar.

## README commands

All three commands completed successfully from the project root:

```text
python -m pip install -r requirements.txt
python examples/run_demo.py
python -m pytest
```

The test run collected **66 tests: 66 passed**, with no skipped tests.
There are 41 scoring/evidence/demo cases and 25 tracker cases. The final run
reported 0.30 seconds. Tests used a separate local environment under the
workspace's intermediate directory; no environment is bundled in this project.

The initial system Python and bundled runtime did not include pytest. The
dependency was installed into that isolated environment before the real pytest
run. Writable temporary storage was used for the Windows sandbox.

## Verified output

- Aurora Gardens: 9.85/10, CANDIDATE.
- Mist Arcade: 6.55/10, REJECTED.
- Paper Comets: 0.00/10, REJECTED.
- All 12 tracker targets appear in the required order, with positive changes
  from +1.00% to +90.00% on the increasing synthetic series.
- The optional export was exercised; `demo-output/report.md` contains the
  generated Markdown cards and tracker.
- An integration test runs the demo from a different working directory and
  checks that its saved report is identical to its standard output.

## Delivery checks

- All required modules, two JSON fixtures, two test files, README, MIT license,
  Python ignore rules, and test requirements are present.
- The README identifies Codex as an independent auditor and includes
  "built with Codex".
- The delivery-wide content scan found no prohibited credential-related terms,
  URL strings, EVM-style address patterns, or Base58 address-like strings.
- All source records and datasets explicitly declare that they are synthetic.
- Application code uses only Python standard-library imports. It performs
  local analysis and has no external service integration.
