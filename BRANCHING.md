# Branch strategy

Privateer uses two long-lived branches:

- `main` contains the latest supported release. Every commit on this branch
  must be tested and ready for end users.
- `develop` contains ongoing work for the next release. Features and fixes are
  integrated here and may be incomplete or unstable.

Create short-lived `feature/<name>` or `fix/<name>` branches from `develop` when
a change needs isolation. Merge completed work back into `develop`. To publish,
validate the complete candidate, update the version and release markers, then
merge `develop` into `main`. The Windows release workflow runs from `main` and
publishes the matching GitHub Release.

The former `Codex` branch is retired. New work should target `develop`, and
release promotion should target `main`.
