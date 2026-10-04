# Ship transfers

Privateer transfers complete ship-instance records between the flattened
`[NationNShips]` rosters used by the supplied RTW3 saves. The selected ship keeps
its permanent hull ID, construction progress, location, logs, crew, equipment,
and every unknown field. Privateer regenerates only the nation-local `ShipN`
slots.

For each source design and receiving nation in a transfer batch, Privateer copies
the complete opaque design block into the receiver's `DesignFilesN.des`, assigns
the next valid internal design ID, appends the next record ordinal, and updates
the receiving hull's `DesignRefId`. The donor design remains in place.

`BuildingNationIdx` remains unchanged so the hull retains its original building
nation. When a player ship is transferred to an AI nation, its `CommanderId` is
cleared to `-1`; the officer record is retained. Ships received by the player
remain unassigned.

The transfer window displays the saved type, name, class, displacement, speed,
main caliber, search/fire-control radar classes, ASW value, build year, location,
status, crew quality, maintenance, and armament description. As of 0.9.8.1, the
status labels use the mapping supplied by the user on 2026-10-03:

| Saved Status | Game abbreviation | Privateer label |
| --- | --- | --- |
| 0 | AF | Active Fleet |
| 1 | RF | Reserve Fleet |
| 2 | MB | Mothballed |
| 3 | TP | Trade Protection |
| 4 | R | Raider |
| 6 | FS | Foreign Service |
| 9 | — | Museum Ship |

Reserve Fleet (1) and Raider (4) are distinct saved statuses. Transfers preserve
the saved status code; this mapping changes display labels, not budget formulas.
Unverified live codes retain their number and are labelled unknown rather than
being guessed. Crew quality remains a raw value.

Final disposition is read before interpreting ordinary fleet status. Scrapped,
broken-up-on-slipway, sunk, mined, scuttled, and other unavailable historical
hulls are omitted from the transfer window and cannot be transferred through the
save API. Museum ships are identified by the verified Status value 9 and are also
omitted and blocked, even if Fate is still XXX. A live record with Fate set to
XXX and InPlay set to 0 is shown as Under construction; it remains eligible under
the existing construction-transfer safeguards. This distinction prevents a
broken-up slipway record from being mistaken for a ship still being built.

Click any fleet-table column header to sort by that column. Click the same header
again to reverse the order. The arrow in the header shows the active direction;
saved numeric statistics sort by number and blank values remain at the bottom.

Privateer indexes each hull's fields once when the save loads. The transfer window
caches its display rows and sort values, and search input is debounced briefly.
Changing owners, filters, sorting, or staged destinations therefore does not scan
the complete raw nation roster once per ship.

The manager blocks carriers and other ships with aircraft capacity because their
air-group dependencies have not been decoded. It also blocks transfers involving
the player while active campaign divisions are present. These cases must be
handled in-game until their linked save structures are understood.

Changes are staged in memory. **Save As** is recommended for the first game-level
test. **Save** follows the configured backup policy before replacing the changed
campaign and destination design-library files.

## Cross-save experiment: HDP-64

On 2026-10-03 the user confirmed that combat and advancing turns worked after
18 HDP-64-class destroyers were copied from Game6 (USA, 1971) to Game7 (Italy,
1902). The experiment copied complete hull and design records, remapped their
identities and ownership, and preserved equipment and original builder history.

This is user-reported in-game validation for this class and campaign pair. It
supports further Ship Spawner work, but cross-save spawning is not yet a shipped
manager feature. Carrier dependencies, other ship types and fresh-hull creation
still need separate validation.
