# Infrastructure and fortifications

Load a save, right-click a nation, and open **Infrastructure and Fortifications
Manager**. Dockyard size remains editable at the top. The table lists that
nation's installations, their type, possession, aircraft capacity, state and
recorded maintenance. Click any column heading to sort it.

Select a built installation and choose **Edit selected** (or double-click its
row). Batteries can change caliber/type, name and owned possession. MTB
squadrons can change name and owned possession. Airbases can change size;
their name, site and permanent ID stay unchanged so assigned aircraft retain
their base links. A base cannot shrink below the sum of its air units' greater
current/desired aircraft counts. Converting between airbases, airship bases,
batteries and MTB squadrons is not supported.

**Add installation** creates a built installation in an owned possession.
Choose a type, possession and name. For airbases or airship bases, choose a
named site instead of entering a name. Site lists come from
`Data/MapData.dat` under the game installation configured in Settings. A second
base of the same family at an occupied site is rejected, including sites named
"Naval air station ..." in the save. The campaign's `GameMaxAirbaseSize` limits
the available airbase sizes. No funds are deducted and no aircraft units are
created automatically.

**Stage** updates this window's pending list. **Apply** stages the whole batch
in the loaded editor; use **Save** or **Save As** to write it with the normal
backup settings. **Reset changes** restores this window's original values;
**Cancel** discards this window's edits. Invalid batches do not partially apply
dockyard edits or other installations. Construction, retired and unrecognized
types are visible but read-only. This version does not remove installations.

## Format observations and verification

Game6 was inspected across all nine nations: USA 70, Germany 48, Great Britain
72, France 57, Russia 46, Japan 50, Italy 53, Spain 30, Austria-Hungary 19.
These are `[NationNCoastalArtillery]` sections in the numbered campaign BCS,
with `CACount` and zero-based `ShipN...` fields. They are not normal fleet ships
and do not need copied entries in `DesignFilesN.des`.

- Observed classes include 4–12-inch coastal batteries, 12–14-inch turreted
  batteries, Missile Battery, MTB squadron, Airship base (8 airships), and
  Airbase20/40/60/80. Installed `Data/IDes` also supplies Airbase100 and Airbase120
  templates; the campaign size limit still applies.
- `Classname`, `ShipType`, `AircraftCapacity` and `Description` must agree.
  Type changes update those fields together with type costs/maintenance.
- `InPlay=1` identifies built examples. Britain's last battery has `InPlay=0`
  and incomplete `BuildProgress`. Completed installations can retain positive
  progress and monthly-cost values, so positive progress alone does not mean
  construction. Airbase `Status=1` also appears on existing foreign bases and
  is preserved rather than being mistaken for construction.
- `AU...HomeBase` references an installation's permanent `Id`. Existing IDs,
  unknown fields, log entries and air-unit records are preserved. Additions
  allocate above the global `IDNo` counter and all BCS identity fields, update
  `CACount`, and advance `IDNo`.
- New built records use the observed scenario-start representation:
  `InPlay=1`, `BuildProgress=0`, `MonthlyCost=0`, `DesignRefId=-1`.
- Default type costs and maintenance are based on Game6's USA records; foreign
  construction costs can differ. Airbase maintenance defaults follow the
  observed 20/40/60/80 progression (capacity + 26); 100/120 maintenance is an
  extrapolation, not a measured Game6 value. Existing values remain untouched
  unless the type changes. The game may recalculate expenses.

Synthetic tests cover atomic validation, ID allocation, occupied-base protection,
campaign limits, stale-save rejection and save/reload. A temporary Game6 copy
was edited and reloaded successfully with unrelated sections unchanged and
the original folder's hashes unchanged. The new records have not yet been
verified through an RTW3 turn advance.
