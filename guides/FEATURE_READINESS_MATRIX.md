# Feature readiness after the content audit

Implementation update, 2026-09-29: released 0.9.8 implements the read-only submarine
inventory described below. Search, filters, sorting and raw details are available;
creation and edits remain gated. See [Submarine Manager](SUBMARINES.md).

Updated 2026-09-26, through final research checkpoint 8. This is an implementation
handoff, not a statement that the features have passed in-game validation.
See [implementation guide](FEATURE_IMPLEMENTATION_GUIDE.md) for architecture,
[data catalog](FEATURE_DATA_CATALOG.md) for field families and
[research progress](FEATURE_RESEARCH_PROGRESS.md) for source-specific evidence.
Later checkpoint corrections take precedence over initial inventory-only notes.

## Open issue coverage

| Issue | Directly useful inputs / work now supportable | Remaining research or acceptance boundary |
|---|---|---|
| #22 Budget | Saved construction/maintenance fields, controlled budget screenshots, explicit intelligence rate, installation/submarine breakdowns; Tips.txt adds age and repair/rebuild cases. | Missing aircraft/submarine/academy formulas, maintenance residual, missile accounting, income adjustments and modifier order. Do not double-apply age costs or call subtotal complete. |
| #27 Aircraft/fortification validation | AircraftTypes/AirUnits, all 4,055 observed HomeBase links, model sentinel cases, installed templates and FAQ base behavior. | In-game multi-turn evidence for generated roles, capacities, player/AI bases, automatic airships, financial effects and restore. Presence of a record is not functionality. |
| #28 War/alliance research | Existing controlled add-enemy and alliance evidence, scalar/pairwise relations, manual rules, event grammar. | First war from peace, ending wars, AI-only wars, conditional alliance timing and downstream effects. Event codes are not save-write recipes. |
| #16 Current tutorials | Existing manager guides, manual/FAQ behavior and concrete caveats identified by the audit. | Current UI screenshots and verified recovery steps; distinguish public release from local test build. |
| #29 Public-domain sourcing | Asset-family inventory and exact dependency names. | Rights evidence and actual asset selection remain unresearched. Installed/modded artwork is not automatically redistributable. |
| #19 Submarine manager | All nine campaign rosters; 14 observed fields; status/history examples and optional building locations. A read-only sortable roster is shipped in 0.9.8. | Numeric labels/ranges beyond verified cases, creation/removal counters, persistent identity, pricing and multi-turn edits. Active=0 is not a deletion condition. |
| #21 War/alliance editor | Reuse existing diplomacy staging after #28; preserve raw directional values and dynamic slots. | Safe transition transactions remain gated on #28. No broad war/peace toggle is established. |
| #30 Built-in spawning | Metadata preview over 1,466 individual designs is supportable. Existing transfer code supplies whole-block copying and ID remapping for already saved designs. | Headerless Game7 libraries, individual-design conversion, fresh hull initialization, histories/counters, construction and carrier/division dependencies; game checks across nations. |
| #31 Custom-design spawning | Reuse phase-1 preview/provenance and supported-format rejection; user templates and scenario lookup documentation exist. | Depends on #30; campaign legality, custom-nation compatibility and multi-turn imports. Scenario acceptance does not prove campaign legality. |
| #14 Spawner parent | Shared catalog, staging and dependencies are documented under #30/#31. | Keep open until both child phases meet their acceptance criteria. |
| #17 Custom nations | Existing isolated prototype, BNat era records, names, map possessions, WarInfo and user packages. | Fix BOM handling; explicitly pair Russia/Soviet-era templates; handle conflicting duplicate keys and missing flags; verify install/new campaigns. Do not merge prototype as already validated. |
| #23 Graphics/pictures | Catalog of runtime references and graphics/geometry families. | Select licensed/public-domain assets under #29; UI integration and accessibility remain implementation work. |
| #25 Logo | Product requirement and asset policy. | User-approved/public-domain artwork and actual design work remain; no image was generated during the audit. |
| #32 Future tutorials | Feature-specific failure cases and acceptance checklist below. | Current submarine inventory belongs in #16; cover future submarine edits, diplomacy, spawning and nations after implementation and testing. |
| #33 AAR logger | Paired text/time logs, combat tables, battle metadata and tactical ship/hit records. A raw local viewer/import preview is supportable. | Requirements TBD; stale-file association, finality, date linkage, sentinel IDs and malformed headers. Cloud/Pro integration remains exploratory. |

## Concrete first implementation slices

These are proposed next development steps, not changes performed by the audit.

1. **Read-only submarine roster (shipped in 0.9.8):** group by nation/local slot, retain historical
   records, expose raw unknown values, make missing locations explicit, and keep
   creation/removal disabled until initialization and dependency rules are known.
2. **Read-only design catalog:** index relative source, filename, class name,
   type, displacement and optional year/cost. Preserve duplicates and source
   priority. Label cost as template cost; omit any unsupported spawn action.
3. **Nation prototype repair:** BOM-aware read, per-era template identity,
   duplicate/conflict reporting and dependency preview. Work on its existing
   branch. Confirm chosen text encodings and output names against actual packages.
4. **AAR source preview:** show each file's own date and source identity; preserve
   raw records and reject unsupported row shapes without data loss. Do not join
   stale SAC/log/BCS data into a supposedly final report.
5. **Budget evidence reconciliation:** add verified cases to tests and labels;
   keep unresolved components explicitly partial. The new tip about older ships
   identifies a missing case, not a verified computation to insert immediately.

## Acceptance cases that must survive implementation

- Submarines: sunk history with InPlay=1; repeated names; building hull without
  LocationAreaName; every Active value zero; no permanent surface-style Id.
- Aircraft/bases: empty model assignment with desired aircraft; populated Role=14
  unit with AircraftTypeId=-1; ship and installation HomeBase targets; conversion
  or deletion of an occupied base; new airship base actually populated by game.
- Designs: absent optional Cost/BuildYear/Weights; duplicate names in different
  sources; ordinal different from internal design ID; full opaque payload preserved;
  carrier/division dependencies; interrupted multi-file commit recovery.
- Nations: UTF-8 BOM; accented text; same and conflicting duplicate keys; changing
  era display names; filename stem different from nation name; missing stock flag;
  supporting name/manufacturer pools and opponent mission data retained.
- AAR: dated tactical file years older than campaign; numbered versus autosave
  disagreement; repeated tactical Id=0; unequal paired logs; empty/header-only logs;
  seven-field bombing header with ten-field data; GameEnded not yet interpreted.
- Diplomacy: already-in-war add-enemy evidence must not be generalized to first
  war or peace; alliance values must not be normalized into an invented timer.

These are proposed tests. The audit did not run game acceptance, mutate saves,
create a release, or claim a new cost formula.

## Final source-audit disposition

The scoped source audit is complete. See [final coverage and research gaps](FEATURE_AUDIT_COMPLETION.md).
Every source family has a disposition; unresolved mechanics and lower-priority
opaque formats remain documented future research, not unfinished checkpoints.
Neither audit completion nor parser support establishes in-game compatibility.
