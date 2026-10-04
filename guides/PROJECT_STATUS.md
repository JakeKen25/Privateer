# Current project status and documentation policy

Reviewed 2026-10-03 against development **Privateer 0.9.8.1**. The latest
published release remains **0.9.8**.
The [release notes](../packaging/RELEASE_NOTES.md) separate development changes
from shipped changes.
`develop` also contains subsequent research and documentation; `main` follows
the [release workflow](../BRANCHING.md).

Development 0.9.8.1 adds the supplied ship-status mapping, distinguishing RF from
R and identifying TP. The [ship guide](SHIPS.md) also records the user-confirmed
HDP-64 cross-save combat and turn-advancement experiment. No release was published
for this development update.

## Current boundaries

- Ship transfers preserve the original builder nation, including unfinished
  ships. Carrier/air-group and active player-division dependencies remain blocked.
- Technology, caliber, economy/unrest, colonies, ordinary tensions, admiral,
  aircraft-model and infrastructure controls are implemented. Their user guides
  distinguish supported edits from unverified in-game consequences.
- The budget calculator displays numeric estimates and a ±10% monthly-balance
  planning allowance. Missing formulas use disclosed assumptions; the allowance
  is not a measured confidence interval. See [current rules](BUDGET_ESTIMATES.md)
  and [later possession research](POSSESSION_BUDGET_RESEARCH.md).
- Submarine inventory is shipped, with search, filters, sorting and raw details.
  Creation, transfer, removal and editing remain unimplemented.
- Ship Spawner is a placeholder. War/alliance editing, custom nations and the
  AAR logger are not shipped features. The custom-nation prototype is separate.

## Which document to trust

Use [user guides](README.md) for current operations and source/tests for exact
implementation behavior. Use dated research for observations and unresolved
questions. A successful parser or automated test does not establish in-game
behavior. Historical test counts are results from that dated work, not the
current suite size. Historical milestone version numbers are planning labels,
not release promises or evidence that a milestone is complete.

The original CODEX_HANDOFF, ship-parser proposal and early format observations
are historical. Their prototype defects and builder-rewrite proposals do not
describe current behavior. Preserve them for provenance, not as implementation
instructions. Builder preservation is settled product policy; downstream game
effects of unfinished transfers remain a separate validation question.

## Remaining documentation work

Current tutorials should target 0.9.8, including submarine inventory. Add actual
UI screenshots, a first-edit walkthrough and verified backup-recovery steps.
Future tutorials should cover submarine mutations and other future controls only
when implemented. Existing external manual material has not been revalidated in
this repository cleanup.

## Maintenance rules

Update a feature's guide when its behavior changes, and link it from the guide
index. Keep evidence in its dated document instead of copying competing formula
tables into several guides. Mark superseded material explicitly; keep unresolved
questions visible. Do not rewrite historical measurements to match assumptions.

Generated package metadata, caches, temporary test folders and release binaries
are not source and must remain ignored. The intentionally supplied Game4/Game5
fixtures are used by tests and must remain immutable. Never add live campaigns
or installed game assets. This cleanup does not alter the published 0.9.8 binary.
