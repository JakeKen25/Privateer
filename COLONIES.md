# Colony ownership manager

Right-click a nation and choose Manage Colonies. The window initially lists that
nation's possessions. Choose All owners to include other nations and Neutral
possessions. Search by name, owner, or map-area index. Select one or more rows,
choose a new owner, and click Stage transfer. The New owner column shows pending
changes. Apply stages the batch in memory; Reset or Cancel discards dialog edits.
Save or Save As writes the changes through the backup and validation workflow.

Click any possession-table column header to sort by that column. A second click
reverses the order, and the header arrow shows the current direction. Map area,
value, oil, and base fields sort numerically; blank values remain at the bottom.

Game1 was inspected read-only: MapData1.dat has one [MapAreas] section, 16 map areas,
and 123 possessions. Each MapAreaAPossessionBOwner value is a saved nation name or
Neutral. Names and the Value, Oil, BaseValue, Rebellion, Invaded, InvasionSupport,
BuildingBase, and TakenFrom fields are separate. Only Owner values are changed.
The file contains both overseas possessions and home territories; the manager
includes both and does not guess an unsupported colony/home classification.
Area indices are displayed because the file has no verified region-name mapping.

Campaign loading prefers RTWGameX.bcs over Autosave.bcs and associates only
MapDataX.dat with that numbered campaign, even after the folder is renamed.
Missing maps disable colony management. Missing/duplicate fields and inconsistent
possession counts are rejected. Unknown original owner names remain visible;
new owners must be a nation in the loaded save or Neutral. No ownership ID is
inferred from NationNumber. Invasion, settlement, fleet, economy and diplomatic
side effects are not synthesized. In-game transfer behavior remains to be checked.

Save creates a complete folder backup. Save As leaves the source unchanged. Both
use temporary writes and reload validation; colony edits also check for source
files changed on disk since loading. Close the game before saving to avoid a
concurrent game write after the final check.

Validation: five colony unit tests passed, plus the existing 15 targeted tests.
A Game1 GUI/save-as test loaded all 123 possessions, staged one transfer, and
confirmed that only one Owner line in MapData1.dat changed. All other source files
remained byte-identical; the live Game1 folder was never modified. UI checks cover
owner filtering, search, Reset, Cancel and Apply. Full pytest suite not run.
