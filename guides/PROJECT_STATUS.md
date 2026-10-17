# Current project status and documentation policy

Reviewed 2026-10-17 for **Privateer 1.0.5 Beta**. The 1.0.6 local development
build adds an Air Wing Manager and same-campaign air-group migration for ship
transfers; it is not published yet. See [release notes](../packaging/RELEASE_NOTES.md)
and the [user wiki](https://github.com/JakeKen25/Privateer/wiki).

## Current boundaries

- Ship transfers preserve the original builder nation, including unfinished
  ships. Same-campaign carrier transfers migrate linked air wings by updating
  their nation while retaining aircraft references and base IDs. Cross-save
  carrier copies and transfers involving active player divisions remain blocked.
- Technology, caliber, economy/unrest, colonies, ordinary tensions, admiral,
  aircraft-model and infrastructure controls are implemented. Their user guides
  distinguish supported edits from unverified in-game consequences.
- The budget calculator displays numeric estimates and a ±10% monthly-balance
  planning allowance. Missing formulas use disclosed assumptions; the allowance
  is not a measured confidence interval. See [current rules](BUDGET_ESTIMATES.md)
  and [later possession research](POSSESSION_BUDGET_RESEARCH.md).
- Submarine Manager supports spawning, renaming, deletion and repair with staged
  Apply/Cancel changes; its generated behavior still needs in-game validation.
- Ship Spawner supports cross-save copying and SDF import. Built-in design
  spawning is not available. Custom nations and the AAR logger are not shipped.

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

Current tutorials should target the current published 1.0.5 Beta. Add actual
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

War, ceasefire and alliance actions are now implemented on develop; see [Relations](RELATIONS.md) for tested behavior and limits.
