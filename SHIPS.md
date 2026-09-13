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
status, crew quality, maintenance, and armament description. Status and crew
quality remain labeled as raw values because their integer-to-text enumerations
have not been validated.

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
test. **Save** creates a complete timestamped sibling backup before replacing the
changed campaign and destination design-library files.
