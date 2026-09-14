# Privateer — Codex Project Handoff

## Purpose of this document

This is the continuity document for the next Codex task. It records the product
goal, user discoveries, current implementation, known defects, missing inputs,
and the order in which the project should be corrected. Read this document,
`README.md`, `INSTALL.md`, and the source before making changes.

The repository currently contains an architectural prototype, **not a usable
RTW3 save editor**. Do not describe it as version 1.0 and do not trust its output
with a real save until the real-format acceptance gates below pass.

## Core product purpose

Privateer is intended to be a Python 3.11+ desktop application for safely editing
existing **Rule the Waves 3 (RTW3)** save games. A user selects a complete save
slot folder, Privateer loads the related files as one structured save, permits
controlled changes in memory, validates all cross-file relationships, backs up
the slot, and only then writes a result that RTW3 can load.

Privateer is not a generic INI editor or a search-and-replace utility. Ship
ownership, nation rosters, ship counts, design-library ownership, external design
record numbers, internal design IDs, builder information, and construction state
are interconnected. A transfer is a database migration across those structures.

The governing safety rule is:

> Never create a save that the validator already knows is inconsistent.

Unknown fields and files must survive unchanged. A failed batch operation must
roll back in full. Correctness and preservation take priority over convenience.

## Intended user experience

1. Start Privateer and choose **Select Rule the Waves 3 Save Folder**.
2. Select one complete slot such as:

   ```text
   C:\Users\<user>\Documents\My Games\Rule the Waves 3\Save\Game5
   ```

   The parent `Save` directory contains `Game1`, `Game2`, and similar slot
   directories. The slot—not the parent and not one file—is the editing unit.
3. Privateer discovers the main save and its `.des`, `.off`, `.sta`, and other
   associated files. Unknown files are preserved without interpretation.
4. Privateer detects the player nation, using an explicit indicator where one is
   available and a visibly warned `Nation0` fallback otherwise.
5. The GUI provides Nations, Fleets, Technology, Economy, and Validation views.
6. Edits remain in memory and the title/status shows an unsaved-change marker.
7. **Validate** reports original-save issues separately from edit-introduced
   issues.
8. **Save As** creates an experimental slot. **Save** first creates a complete,
   timestamped backup. **Restore Backup** restores a selected valid backup.
9. Saving uses temporary output, reloads it, validates it, and publishes it only
   after all critical checks pass.

## Required feature set

### Nations and economy

- List all nations and identify the player.
- Set exact `Funds` or multiply current funds.
- Edit `BaseResources` separately from current funds.
- Expose `BudgetModifier` when present.
- Calculate an approximate base-resource target from an observed and desired
  annual budget:

  ```python
  new_base_resources = round(
      current_base_resources * desired_budget / observed_budget
  )
  ```

- Clearly state that RTW3 remains authoritative for the displayed annual budget.
- Validate integers and warn about game-unsafe extremes.

### Technology

- Represent technology generically and per nation.
- Copy a known-valid complete technology state between nations.
- Support simple presets only after the real format and valid ranges are mapped.
- A maximum preset must update every required level/unlock field; it must not be
  an invented blanket value.
- Advanced categories must come from observed RTW3 fields, not guessed names.

### Fleet browser and transfers

- Display every ship with owner, name, class, type, displacement, status,
  construction status, design reference, and builder where available.
- Filter and select single ships, multiple ships, a type, or an owner's fleet.
- Plan and perform batch transfers atomically.
- Remove complete ship records from source rosters and insert them into the
  destination roster using the real record grammar.
- Recalculate `ShipCount`; never ask the user to edit it.
- Resolve the source design for every ship.
- Reuse a proven-equivalent destination design or clone the source design.
- Allocate collision-free destination IDs.
- Remap both the design's external record identifier and internal design ID.
- Point the ship to the resulting destination design.
- Preserve the donor's original design library.
- Handle shared designs, colliding source IDs, and under-construction ships.
- Support explicit builder policies, with the default chosen from real-game
  testing rather than assumption.

### Bulk/scenario support

The core should expose reusable APIs for ship queries, batch transfer, economy
changes, technology copying, and seeded random distribution. Seeds must be logged
for reproducibility. Scenario recipes belong above the parser and should not be
hard-coded into it.

## Save-integrity requirements

Before normal saving, validation must cover at least:

- All expected nations remain present and indexes are unique.
- Player detection is explicit or reports its `Nation0` fallback.
- Every physical ship record is parsed and belongs to exactly one roster.
- Ship IDs are unique in the scope required by RTW3.
- Every stored `ShipCount` equals the actual roster-record count.
- Owner fields agree with roster placement.
- Every ship design reference resolves in the correct nation's library.
- External design record IDs equal internal design IDs.
- Design IDs are unique in their required scope.
- Ship and design types agree when comparable.
- Required design libraries remain present.
- Under-construction ownership/building relationships are valid.
- Economy values are valid integers in confirmed game-safe ranges.
- Technology values/types satisfy a detected format profile.
- Reloaded temporary output has the same logical model as the in-memory save.
- Unknown files are byte-identical and untouched records remain unchanged.

The report should include concrete totals: ships, resolved references, missing
references, duplicate IDs, count mismatches, type mismatches, and critical issue
count. Critical issues must disable normal saving.

## What has been implemented

The current branch contains:

- `privateer/document.py`: a line-oriented section document that retains
  preamble, raw lines, separators, ordering, and detected newline style, and
  rewrites only a targeted field line.
- `privateer/model.py`: preliminary `Nation`, `Ship`, `ShipDesign`, and
  `TechnologyState` dataclasses.
- `privateer/save.py`: preliminary folder loading, nation/ship/design modeling,
  player fallback, fleet queries, snapshot transactions, transfers, seeded
  distribution, technology operations, validation, backup, Save As, and audit
  logging.
- `privateer/validation.py`: structured issues and a printable validation report.
- `privateer/main.py` and `privateer/__main__.py`: GUI/CLI entry points.
- `privateer/gui.py`: a minimal Tkinter shell with folder browsing, nation table,
  player display, Validate, Save, and Save As.
- `tests/test_privateer.py`: six synthetic tests for the prototype assumptions.
- Packaging and user documentation in `pyproject.toml`, `README.md`, and
  `INSTALL.md`.

The existing tests passed under their synthetic format. That does not establish
compatibility with genuine RTW3 saves.

## User-observed failure in the prototype

The user selected a real slot at approximately:

```text
C:/Users/Yunda/Documents/My Games/Rule the Waves 3/Save/Game5
```

The GUI correctly displayed ten nations, their funds, base resources, and the
`Nation0` player fallback (Austria-Hungary). It displayed **zero ships for every
nation**. Validation then reported nine `ship_count` errors, for example stored
counts of 36 for Austria-Hungary, 51 for Great Britain, and 46 for France versus
an actual parsed count of zero.

Interpretation: nation parsing worked, but real ship records were silently
ignored. The original save was not thereby proven corrupt. The application must
never present an unsupported/unparsed fleet as a valid empty fleet.

## Root causes and unsafe assumptions in the current code

### Ship section assumption

The parser only recognizes individual sections matching `NationNShipM` or
`ShipM`. The user's original material described sections such as
`[Nation0Ships]`, and real ship records evidently do not match the prototype.
The record grammar inside the real roster section must be documented before it is
implemented. Do not merely add one more regular expression.

### Ship movement is not physical record movement

The prototype moves a `Ship` between Python lists and changes owner fields, but
does not relocate its underlying lines between real nation roster containers.
Real transfer support needs source spans and a roster record codec that can remove
and insert an entire record without reformatting unrelated data.

### Guessed design ownership and grammar

The loader guesses design-library ownership from filenames containing
`DesignFilesN` or `NationN`, or from an owner field. Actual `.des` naming,
record boundaries, ownership, ID scope, free-slot behavior, and internal-ID field
must be learned from the supplied examples.

### Simplified design allocation

The prototype chooses `max(existing external ID) + 1`. This may violate real ID
bounds, reserved values, contiguity, index tables, or free-slot conventions. The
allocator must be format-specific and batch-aware.

### Guessed design equivalence

The current signature ignores a small guessed set of fields. Two designs must not
be declared equivalent until fields that affect RTW3 identity and behavior are
known. It is safer to clone an extra valid design than to merge different ones.

### Invented maximum technology

The prototype recognizes name prefixes and sets integer technology fields to
`100`. This is not a validated RTW3 preset. Disable or remove maximum technology
until known-good saves establish every field, type, range, and dependency.

### Encoding is not preserved

Loading tries UTF-8 and CP1252, but writing always emits UTF-8. The document must
retain encoding, BOM state, newline convention, and final-newline state per file.

### Main-save discovery is weak

The first alphabetically sorted `.bcs` file is selected. Correct discovery must
use real naming and structural probes, detect ambiguity, and fail safely.

### Transaction reference problem

Rollback replaces internal structures with deep copies. Callers may still hold
references to objects from the discarded model. Prefer a planned operation
applied to a private working clone, then swap in the validated model on success.

### Incomplete validation

Current validation covers some count, duplicate-ID, design-reference, type, and
integer-range checks, but not the full invariant list above. It also cannot be
trusted while the parser silently omits real records.

### GUI is only a shell

There is no fleet browser/transfer editor, economy editor, technology editor,
modified marker, baseline-versus-working validation, or backup restore UI.
Do not prioritize these until real-format parsing and transfer tests pass.

## Newly referenced artifacts that are not in this checkout

The user reports recreating part of the real game directory structure in the
GitHub repository and placing an explanatory Markdown file inside the example
saves folder. That Markdown is development documentation and **does not normally
exist in an RTW3 installation**. It must never become a required game file or be
treated as save metadata.

At the time this handoff was written:

- The local checkout had no configured Git remote.
- No example save folder was present locally.
- No diagnostic Markdown was present beyond normal project documentation.
- A GitHub web search attempt was unavailable due to HTTP 401.

The next task must provide or discover the repository URL/branch, fetch those
artifacts, and read the diagnostic Markdown before implementation.

## Required next-task workflow

### Phase 0 — Read instructions and establish repository state

1. Locate every applicable `AGENTS.md` before editing.
2. Inspect status, branches, remotes, and recent history.
3. Fetch/checkout the branch containing the example structure without deleting
   user work.
4. Read this handoff and the example-folder diagnostic Markdown.
5. Inventory every example file and identify which files normally belong to RTW3.

### Phase 1 — Freeze and characterize fixtures

1. Hash all example files and never mutate the originals in tests.
2. Copy/anonymize suitable files into a clearly marked test-fixture tree if their
   licensing and privacy permit it.
3. Record filename, encoding, BOM, line endings, size, and whether each file is
   textual or binary.
4. Produce `guides/rtw3-format-observations.md` with confirmed real excerpts.
5. Separate facts from hypotheses and note the exact RTW3 version if available.

### Phase 2 — Reverse-engineer read-only grammar

1. Identify the main save by name and contents.
2. Map nation record boundaries and fields.
3. Map the exact `[NationNShips]` roster grammar and individual ship boundaries.
4. Map ship ID, design reference, owner, builder, status, type, class, and
   construction fields.
5. Map `.des` files to nations.
6. Map external and internal design IDs and all design record boundaries.
7. Map actual player indicators and technology storage.
8. Record any indexes/counts/checksums that must be maintained.

**Gate A:** An unchanged real fixture parses every nation and every ship, and all
parsed per-nation counts equal stored counts. Unrecognized records are errors,
never silently discarded.

### Phase 3 — Implement format profiles and record codecs

1. Add a version/profile abstraction for file discovery and field names.
2. Add nation, roster, ship, and design codecs based on confirmed grammar.
3. Retain exact source spans and raw unknown fields for every record.
4. Preserve file encoding and line-ending metadata.
5. Produce descriptive unsupported-format diagnostics with file and line context.

**Gate B:** Every ship in an unchanged fixture resolves a correct design in its
owner's actual library. External/internal ID mismatches remain unresolved and are
reported.

### Phase 4 — Baseline validation and no-op round trip

1. Implement the complete invariant list in this document.
2. Save original validation separately from working-copy validation.
3. Serialize an unchanged save to a new folder.
4. Compare hashes/bytes and explain any intentionally generated file.
5. Reload the output and compare the logical models.

**Gate C:** No-op Save As is functionally identical, unknown files are
byte-identical, and recognized untouched content is byte-identical wherever no
format-required change occurred.

### Phase 5 — Planned atomic transfer migration

1. Build an immutable transfer plan before mutation.
2. Resolve every source design.
3. Group ships sharing designs.
4. Conservatively match equivalent destination designs.
5. Allocate all destination IDs in one collision-free batch.
6. Clone records and remap external/internal IDs.
7. Physically relocate complete ship records between roster containers.
8. Apply the tested builder policy, with special under-construction checks.
9. Recalculate all derived counts and indexes.
10. Serialize to temporary output, reload, validate, and only then commit.

**Gate D:** A single real ship transfer loads in RTW3, resolves its design, and
leaves the donor design available.

**Gate E:** A batch covering shared designs, colliding IDs, multiple donors, and
under-construction ships loads in RTW3 with zero missing-design warnings.

### Phase 6 — Economy and technology

1. Add safe setters and multiplication with audit entries.
2. Add the approximate annual-budget calculator with divide-by-zero and range
   checks.
3. Map technology from known-good real saves.
4. Implement technology copy first.
5. Implement presets only from validated profiles; never restore the blanket-100
   behavior without proof.

### Phase 7 — Complete save safety

1. Implement full backup creation and collision-safe timestamp naming.
2. Implement atomic Save and Save As destination checks.
3. Reload and validate all candidate output.
4. Add Restore Backup with confirmation and validation.
5. Expand the audit log with old/new values, transfer/design totals, seed, source
   path, output path, profile, and validation summary.

### Phase 8 — Build the complete GUI

Only after Gates A–E:

1. Add Nations, Fleets, Technology, Economy, and Validation tabs.
2. Add fleet filtering, multiselect, destination, and plan preview.
3. Add economy controls and proportional budget calculation.
4. Add technology copy and validated presets.
5. Add unsaved-change status and safe close confirmation.
6. Disable Save on critical validation errors.
7. Clearly show unsupported/partially parsed saves as read-only instead of empty.

### Phase 9 — Release acceptance

1. Run unit tests and anonymized real-fixture regression tests.
2. Run no-op byte comparisons.
3. Run single and large transfer scenarios.
4. Load outputs in the matching RTW3 version.
5. Confirm transferred ships, designs, builders, construction, donor designs,
   counts, funds, resources, and technology in game.
6. Save and reload once from RTW3 itself.
7. Do not call the application usable until the large-transfer design audit and
   in-game load pass.

## Minimum regression matrix

- Invalid folder and ambiguous main save.
- Nation0 fallback and explicit/ambiguous player indicators.
- Every real fixture's per-nation and total ship count.
- No-op load/save preservation, including CP1252 and CRLF.
- Unknown text fields, comments, binary files, and documentation-only Markdown.
- Exact funds/base-resource edits and funds multiplication.
- Budget approximation and invalid input.
- Single and batch ship transfer.
- Donor design preservation.
- External/internal design remapping.
- Multiple ships sharing a design.
- Equivalent destination design reuse.
- Multiple sources with colliding IDs.
- Under-construction ships under each builder policy.
- Missing design, mismatched internal ID, duplicate ship/design ID, type mismatch,
  malformed record, and count mismatch detection.
- Atomic rollback at every failure stage.
- Deterministic random distribution and seed audit.
- Technology copy and profile-backed maximum technology.
- Backup, Save As, restore, temporary-write failure, and reload failure.

## Questions that must be answered from evidence

1. What exact RTW3 version produced each example?
2. Which `.bcs` is the authoritative main save when several exist?
3. What delimits one ship in `[NationNShips]`?
4. Are ship IDs globally unique or only unique per nation/roster?
5. How does a design file map to a nation?
6. What are the actual external and internal design-ID fields?
7. Are design IDs bounded, contiguous, reserved, or indexed elsewhere?
8. Which fields determine safe design equivalence?
9. Must roster order or design order be preserved?
10. Which builder behavior does RTW3 accept for transferred ships under
    construction?
11. Is player identity stored anywhere more authoritative than `Nation0`?
12. Which technology fields and ranges constitute a known-valid maximum state?
13. Does RTW3 require the original encoding or tolerate UTF-8?
14. Are there counts, indexes, checksums, or cross-file references not yet known?

## Suggested first prompt for the next Codex task

> Read `developmentResources/CODEX_HANDOFF.md` and all applicable `AGENTS.md` files. Fetch the
> updated branch containing the recreated RTW3 save-folder structure and the
> diagnostic Markdown. Do not implement mutations yet. Inventory the files,
> inspect the Markdown, document the real `.bcs` ship roster and `.des` design
> record grammar with anonymized excerpts, identify every unsupported assumption
> in the current parser, and propose a file-by-file implementation plan. Preserve
> the example files and do not write into them.

## Repository hygiene for future work

- Follow all `AGENTS.md` instructions in scope.
- Never test writes against the original example folder.
- Do not commit personal save data, usernames, or absolute local paths.
- Keep fixture provenance and anonymization documented.
- Do not put import statements inside `try`/`except` blocks.
- Run tests, compilation, formatting/diff checks, and clean-status checks.
- Commit changes on the current branch and create the required pull request after
  implementation changes.
- Cite changed files and exact test commands in the final response.

## Current stopping point

The project is intentionally paused before real-format correction. The next
useful work is to retrieve and study the newly supplied example artifacts. No
further parser, transfer, validator, or GUI assumptions should be added before
that read-only audit is complete.
