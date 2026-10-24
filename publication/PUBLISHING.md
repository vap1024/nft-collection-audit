# Publication checklist for this repository

Prepared on 2026-10-24, Europe/Kiev. This is a handoff, not an automatic schedule.
No future execution is configured or promised. Public creation, push, About,
topics, release, and hosted CI have not occurred.

## 24–26 October: local preparation

- Keep the real local commit history; do not rewrite dates or create a tag early.
- Run tests, regenerate `examples/output/scorecards.md`, and run the file audit.
- Use `repository.json` for the exact owner, description, and topics.
- Preserve the actual local review/fix trace; a separate reviewer is not claimed.

## 27 October: publish and verify

GitHub CLI was unavailable in the preparation environment. On the publication
date, use a connected GitHub tool or install the CLI, check the authenticated
account is exactly `vap1024`, and inspect whether the target repository exists.
Do not display authentication material. If it exists, inspect it before changing
anything; do not overwrite unrelated work.

For a new repository with no existing origin remote, the prepared creation
command is:

```text
gh repo create vap1024/nft-collection-audit --public --source . --remote origin --push
```

Apply the description and six topics from `repository.json`. Wait for the
actual workflow result; inspect and correct failures. Recheck the public clone
quickstart and the three cross-links, including the flagship protocol. The
documentation links were prepared but their public availability was not verified
on 24 October.

After the actual checks, update the dated preparation statuses in README,
VERIFICATION, CHANGELOG, release notes, and repository metadata. Commit these
real changes, then create the release from the checked commit:

```text
gh release create v0.1.0 --repo vap1024/nft-collection-audit --target main --title v0.1.0 --notes-file publication/release-v0.1.0.md
```

Do not state that CI passed until it has. The badge remains a live status link.

## 28 October: user's profile actions

The user manages the profile UI and pins. For this repository the prepared row
is `nft-collection-audit | NFT collection scoring with a 7.0 gate and a 30-day
price tracker`. The intended pin order places this repository third, after the
flagship and L2 application. This project does not modify the other projects or
the profile itself.

## 29 October: public acceptance

- Open the public repository without signing in.
- Follow the clone/install/demo quickstart and run pytest.
- Inspect the sample disclosures, real audit trace, current workflow status,
  release, About/topics, and cross-links.
- Record the actual review date, outcome, and any resulting fixes.
