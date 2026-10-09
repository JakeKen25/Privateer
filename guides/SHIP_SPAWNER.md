# Ship Spawner: cross-save copy

Development build 0.9.10.2 implements the first of two entry choices:
Copy from another save and Use built-in designs (disabled until implemented).
The currently loaded save and right-clicked nation are the destination.

Browse selects a separate campaign folder, loads it read-only, and lists current
hulls by source nation. Search covers saved ship statistics; headings sort the
table. Stage selected adds one copy per hull to the pending batch across source
nations. Unstage selected/Reset changes remove pending choices. Apply atomically
accepts the batch and closes the manager; Cancel/Escape/window-close discard it.
Main-window Save/Save As remains necessary to write the destination.

## Data contract

- Flattened NationNShips and positional v10139 designs only, as in transfers.
- Copies preserve saved equipment, crew, build year, logs, status, damage,
  construction progress and unknown fields. This is not fresh-design construction.
- New global Id values are allocated at or above General/IDNo and above observed
  ID-bearing fields in destination documents and the matching officer file.
  IDNo is advanced to the next unused value. Integer overflow aborts the batch.
- Destination-local Ship slots append contiguously; ShipCount increases.
- One opaque design copy per source nation/design pair per batch is appended to
  the receiving DesignFilesN.des. Its ordinal and internal ID are remapped;
  DesignIDCount and each hull's DesignRefId are updated. Existing designs remain.
- BuildingNationIdx is set to the receiving nation. The source builder does not
  need to exist in the destination campaign. Existing log text remains unchanged.
  This copy rule does not change ordinary transfers, which preserve the builder.
- CommanderId becomes -1. No source officers or division assignments are copied.
  Fresh hull IDs are not added to destination divisions; existing divisions remain.
- LocationAreaName becomes the destination BuildAreaName; DestinationAreaName and
  OrderedAreaName become XXX. Names are retained unless already used in the
  receiving roster, then receive `(copy 2)`, `(copy 3)`, etc.
- Funds, research, dates and other campaign state are not changed. Equipment is
  not scaled to destination technology or year. Existing construction costs may
  apply to copied unfinished hulls when RTW3 advances.
- Carriers/aircraft-capable hulls, historical losses, scrapped and museum hulls
  remain unsupported under the transfer dependency rules.

Source and destination on-disk snapshots are checked before Apply. No source
files are written. Destination edits use a deep copy, validate, check hull
preservation and encoding, then commit in memory. Save retains the existing
source-change/backup checks. Only the main save and destination design library
should change on disk.

## Verification

Automated tests cover round-trip saving, different nation ordering, original hull
and source preservation, commander reset, construction preservation, shared design
reuse, repeated copies, name/ID collisions, and atomic rejection of invalid batches.
The prior HDP-64 Game6-to-Game7 experiment passed user-reported combat and turn
advancement. The generalized manager still needs user testing across more classes
and campaigns. Built-in designs are not implemented in this build.
