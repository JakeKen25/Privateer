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

The normal transfer policy changes `BuildingNationIdx` to the receiver. When a
player ship is transferred to an AI nation, its `CommanderId` is cleared to `-1`;
the officer record is retained. Ships received by the player remain unassigned.

The manager blocks carriers and other ships with aircraft capacity because their
air-group dependencies have not been decoded. It also blocks transfers involving
the player while active campaign divisions are present. These cases must be
handled in-game until their linked save structures are understood.

Changes are staged in memory. **Save As** is recommended for the first game-level
test. **Save** creates a complete timestamped sibling backup before replacing the
changed campaign and destination design-library files.
