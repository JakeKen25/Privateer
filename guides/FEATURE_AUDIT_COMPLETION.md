# Final source-audit checkpoint

> Historical source-audit completion, not a current release checklist.
> Builder preservation is now settled product policy; no builder rewrite is
> planned. For shipped budget/submarine behavior and remaining documentation
> work, see [current status](PROJECT_STATUS.md).

**Checkpoint 8 — complete, 2026-09-26.**

The requested RTW3 install/save content audit and feature handoff are complete.
Every file in the two requested roots has been read, fingerprinted and assigned a
source-family disposition. Relevant manuals, named data and existing reference
material have been compared with the 15 open GitHub issues. Unanswered mechanics
are listed below rather than experimentally solved.

Completion means completion of this source audit. It does not mean the budget is
accurate yet, the roadmap is implemented, or every opaque field is understood.
No executable was decompiled, game state changed or new release produced.

## Deliverables

- [Feature readiness matrix](FEATURE_READINESS_MATRIX.md): all 15 issues,
  immediately supportable work and acceptance gaps.
- [Research checkpoints](FEATURE_RESEARCH_PROGRESS.md): source-specific findings,
  corrections and evidence through checkpoint 8.
- [Implementation guide](FEATURE_IMPLEMENTATION_GUIDE.md): architecture and
  milestone handoff from the initial audit; later checkpoints supersede its
  inventory-only descriptions and any conflicting source interpretations.
- [Field catalog](FEATURE_DATA_CATALOG.md): observed section/key families.

The full path/hash ledger, extraction files and census scripts are retained only
in the local outputs/feature-audit directory. They are not redistributed with the
public guide. Public documents contain summarized findings, not raw saves or
installed game assets.

## Coverage and disposition

| Source group | Files | Completed work | Deliberate boundary |
|---|---:|---|---|
| Installation, all files | 3,856 | Enumerated, read and SHA-256 fingerprinted | No installation modifications |
| Save root, all files | 164 | Enumerated, read and SHA-256 fingerprinted; zero final access errors | Snapshot evidence, not immutable future state |
| Installed readable text families | 3,152 | Strict text decode, structural scan; targeted field/content inspection | Named fields are not automatically decoded engine semantics |
| Save readable families | 164 | Structural scan; all nine numbered BCS rosters, 81 design libraries and ten SAC files included | Autosaves and historical records kept distinct |
| Installed PDFs | 6 / 248 pages | Local text extraction/indexing; feature-relevant prose review and selected visual checks | Not a cell-by-cell transcription of technology/artwork tables |
| Runtime/map binaries | 18 | Two EXEs, five DLLs and eleven LYR files classified/fingerprinted | Engine/binary decoding deferred; no decompilation |
| Media/other | 680 | Image/audio families and two empty placeholders classified/fingerprinted | No exhaustive visual/audio review or redistribution-rights assumption |

Installation bytes: 146,829,059. Save bytes: 259,702,708. Total: 4,020 files and
406,531,767 bytes. Final file counts/sizes agree with the initial inventory.
Fingerprinting binaries is coverage bookkeeping, not reverse engineering.

## Final directly usable data map

| Feature area | Best direct sources | Appropriate immediate use |
|---|---|---|
| Budget | BCS named Cost/MonthlyCost/Maintenance fields; user-controlled comparisons; manual/Tips modifiers | Preserve verified components and distinguish subtotal from missing charges |
| Submarines | NationNSubmarines, SubCount and 14 observed record fields | Read-only inventory with current/history/building distinctions |
| Aircraft and bases | AircraftTypes, AirUnits, HomeBase/Id links, CoastalArtillery, manual/FAQ | Relationship validation that preserves unassigned-model and special-role cases |
| Design preview/spawning | 1,466 individual designs, campaign libraries and existing transfer codec | Preview supported metadata now; gate conversion and fresh hull creation |
| Custom nations | BNat era templates, name/manufacturer pools, map data, WarInfo, supplied packages | Repair prototype input handling and produce dependency previews |
| Diplomacy | Existing controlled evidence plus dynamic nation records | Retain narrow verified operations; do not invent transition write sets |
| AAR | TLog/TTime, SKV, BBI, SAC and documented formatted log export | Source preview and raw local import design with explicit provenance |
| Graphics/tutorials | Manual dimensions/behavior, asset inventories and manager guides | Plan licensed assets and accurate instructions; capture UI only during later implementation |

## Newly confirmed implementation hazards

1. Custom-nation prototype cp1252 decoding skips the first BOM-prefixed nation.
2. Russia and Soviet Union need explicit era-template identity handling.
3. Some stock nation keys conflict; a dictionary silently discards source meaning.
4. Some stock asset references are absent; existence must be checked.
5. Aircraft role and model-purpose enums must not be assumed identical.
6. Populated air units can use AircraftTypeId=-1; strict nonnegative-only links fail.
7. Submarine histories retain InPlay/build-time fields and reused names.
8. Game7 has nine design libraries without the supported v10139 header.
9. Design blocks have variable lengths; copied libraries cannot use fixed strides.
10. Tactical files can be years older than the campaign and repeat Id=0.
11. Bombing-log headers have fewer fields than their data rows.
12. Component/template cost fields do not establish current monthly charges.

Each is backed by a named source or corpus observation in the checkpoint guide.
No listed hazard was silently fixed while doing this research.

## Research still required — not attempted here

### Budget

- Exact aircraft and submarine expense functions, academy cost and income
  adjustments; unresolved maintenance residual and missile-storage accounting.
- Whether age/officer/repair/war/status modifiers are already reflected in saved
  Maintenance, their ordering and rounding, and how rebuilt ships determine age.
- Design-study expenses, halted/delayed/accelerated cases and manual/measurement
  disagreements; template Cost versus campaign cost applicability.
- Meaning of FinalMaintenance and MissileMaintenancePoints outside their directly
  observed fields. Do not fit constants or substitute similarly named values.

### Save editing and compatibility

- Headerless design-library adapter and individual design-to-library conversion.
- New hull/submarine initialization, counters, history behavior and dependencies.
- Builder-preservation versus the older transfer guide's builder-rewrite policy,
  especially unfinished transfers and subsequent rebuilds.
- Carrier air-group migration, special Role=14 semantics and division reconciliation.
- Automatic airship creation following direct base-record creation, capacity
  limits and actual multi-turn behavior of generated aircraft/installations.

### Nations and diplomacy

- Game duplicate-key precedence, era overlay/load order, package identity and
  install compatibility. Missing-asset fallback and rights remain separate work.
- First-war, peace, AI-only-war and alliance transition semantics, conditional
  duration, downstream battles and settlements. Event codes are not direct flags.

### AAR and presentation

- User workflow/export requirements, log rotation, association, complete dates,
  battle completion, victory scoring and row/prefix semantics.
- Public-domain/user-provided asset selection and rights evidence; final screenshots,
  logo work and feature-specific tutorials. No asset sourcing was performed.

### Lower-priority sources

Unlabeled positional statistics, opaque map formats and engine binaries remain
uninterpreted. Detailed artwork/technology cells and unrelated tactical gameplay
manual sections were indexed or sampled rather than exhaustively transcribed.
Their disposition is complete for this audit: no current planned feature requires
claiming those sources are decoded. A future task can reopen a specific source
when an implementation need is established.

## Verification performed

- Read/fingerprint pass completed with no unresolved file-access errors.
- Cross-save counts and air-unit relationship totals checked against saved census.
- Both observed design-header styles and marker counts inspected; unknown style
  left unsupported. No inferred payload conversion was performed.
- All nine installed scenario bundles have matching four-file basenames.
- Documentation links, issue coverage and public-path hygiene checked before push.
- GitHub updates are documentation-only on develop; main, releases and issue state
  remain unchanged. No in-game acceptance test is claimed.

The next task is implementation or explicitly authorized targeted research from
this handoff. There is no remaining checkpoint in this source-audit sequence.
