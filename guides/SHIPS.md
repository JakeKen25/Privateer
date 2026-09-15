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
status, crew quality, maintenance, and armament description. Verified live-fleet
status values are shown as Active Fleet, Reserve, Mothballed, and Foreign Service.
Unverified live codes retain their number and are labelled unknown rather than
being guessed. Crew quality remains a raw value.

Final disposition is read from Fate before interpreting fleet status. Scrapped,
broken-up-on-slipway, sunk, mined, scuttled, and other unavailable historical
hulls remain visible in the roster but cannot be staged or transferred. A live
record with Fate set to XXX and InPlay set to 0 is shown as Under construction;
it remains eligible under the existing construction-transfer safeguards. This
distinction prevents a broken-up slipway record from being mistaken for a ship
still being built.

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
