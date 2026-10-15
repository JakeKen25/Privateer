# Ship Spawner: cross-save copy

Development build 1.0.1 Beta adds Import from SDF file alongside
Copy from another save and Use built-in designs (still disabled).
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


## Standalone SDF import (1.0.1 Beta development build)

The importer reads supported SDFs independently of all source campaigns.
No Game6, template hull, or installed design is needed at runtime. The schema
module contains field names only, not bundled game designs. Alongside current
exports, the importer supports the common older layout used by installed RTW3
ship designs. That layout omits deck-color and high-spotting fields; the importer
supplies empty and zero defaults. Unknown layouts are rejected explicitly.
Schema detection, not the filename extension alone, decides support.

Choose Import from SDF file, Browse SDF, and a count from 1 to 100. Preview shows
the ship names and shared class. Apply accepts the whole batch in memory; Cancel,
Escape and window-close leave the campaign unchanged. Save/Save As is separate.

The importer pre-fills each ship name as Privateer TYPE N, continuing above the
highest existing number in the receiving nation's roster, including historical
hulls. Each copy has its own editable name field. The suggested class is TYPE NAME
N (for example, Destroyer 2 or Battleship 7); edit the shared Class name field to
use a different name for the entire batch. Class numbering considers roster class
names and destination design names. A subsequent import suggests another class.
The original SDF name is not used. Blank, duplicate, or already-used ship names
are rejected before the batch is staged.

Serialization follows the v10139 structure observed in the Vicksburg experiment:
explicit named-field order, duplicate exported Helipad collapsed, mount/equipment
counts inserted, and deck color moved to the tail. Campaign-only metadata uses
neutral defaults except the observed fixed value 8. These metadata meanings are
not fully verified. Full field sets and contiguous component numbering are
required so unrecognized schemas cannot silently shift the positional record.

Completed hulls receive new IDs, the destination nation as builder, the current
campaign year, full cost as build progress, zero monthly construction cost, AF
status, default crew, no commander, and no service history. SDF specifications,
cost, maintenance and capacity are preserved; technology is not scaled to the
receiving campaign. No aviation record or aircraft assignment is created, as
explicitly requested for this experiment. No radar fit is inferred from the SDF
RadarLimit field; fresh hull radar classes start at zero. HSSM is derived from
MT=4 launchers; other missile-fit defaults need broader in-game verification.
Funds are not charged. No source design file is modified.

The user verified the one-off Vicksburg import in Game7. That experiment reused
some Game6 campaign metadata and hull defaults. The generalized converter uses
fresh defaults instead and still needs in-game acceptance/turn/combat testing;
passing Privateer's structural validation does not prove RTW3 acceptance for
all ship types, carrier behavior, or the meaning of every positional field.
Automated coverage includes batch naming/class numbering, shared design IDs,
round-trip persistence, existing-hull preservation, source changes, invalid
counts, malformed components, encoding failures, and duplicate field handling.


### SDF source folders (1.0.4 Beta local build)

Import from SDF file now offers Custom designs and Installed designs. Custom
uses the configured save_game_directory's parent / Custom Files (a sibling of
Save). If no save directory is configured, use the loaded Game folder's
parent's parent / Custom Files. Installed uses rtw3_install_directory / Designs.
A missing installation setting or missing folder gives an informational message
instead of silently browsing an unrelated folder. Read settings at each browse,
so changes apply without restarting Privateer. Both choices use the same importer.
It supports the common older installed-ship layout as well as current exports;
unknown layouts and non-ship designs remain unsupported.
