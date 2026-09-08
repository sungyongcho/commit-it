# Release policy

`SKILL.md` metadata is the single source for the released semantic version. Do not
bump it for each conversation or policy edit. Track unpublished work with actual
Git state and content hashes, and accumulate release notes under `Unreleased`.

Before a release, inspect current source, relevant installed variants, assigned issues
and related PRs. Reconcile completed changes without taking over active work. Choose
the next version only after scope and verification are known: compatible fixes use
patch, additive behavior uses minor, and incompatible documented interfaces use major.
Follow [Semantic Versioning](https://semver.org/). When the user has authorized autonomous
version maintenance, make this decision and update metadata, release notes and verified
package metadata without asking again. A version-only bump without a meaningful change is
unnecessary. This authorization does not itself publish a tag or GitHub Release.

Commit subjects follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
and repository templates. Ordinary changes describe shipped behavior; a dedicated
preparation commit may use `chore(release): prepare vX.Y.Z`. Commits do not automatically
create releases. Preserve required issue references and actual evidence.

Run package and native-installation boundary tests, shell syntax checks and `scripts/check_release.py`.
For an explicitly authorized release, move the selected notes from Unreleased to a
dated version section and run `scripts/check_release.py --tag vX.Y.Z` with its actual
tag name. This validates agreement without creating a tag. Never rewrite published
tags or infer publication authority from passing checks.

Git source may contain unpublished work. Native product installations are maintained
separately and must not overwrite source changes. Verify current product installation
guidance before publishing material that promises an installation command is available.
