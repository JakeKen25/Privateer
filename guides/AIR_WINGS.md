# Air Wing Manager

The Air Wing Manager is opened from a nation's right-click menu. It lists that
nation's saved air-unit records, including model name when the `AircraftTypeId`
resolves, raw role, current and desired aircraft counts, carrier-capable flag,
and current base. Unresolved model IDs remain visible as `Unknown model (ID)`;
the manager does not guess a replacement.

The first implementation supports reassigning an existing wing to an
aircraft-capable ship owned by the selected nation. Use **Assign** to stage the
selected wing's base change, then **Apply** to accept it into the current save
session. **Cancel** discards the window's pending changes. The app's Save or Save
As action writes accepted edits to disk.

The manager changes only `AU#HomeBase`. It does not alter aircraft models,
quantities, roles, or create/delete air wings. It does not yet validate aggregate
deck capacity or determine the operational consequences of a base assignment;
those behaviors need in-game testing.

When a ship with aircraft capacity transfers to another nation, air units whose
`HomeBase` is that ship's permanent `Id` follow the ship. Privateer changes their
`Nation` only, preserving the base ID and all aircraft/model references. A
missing or mismatched `Nation` field blocks the transfer to avoid separating a
carrier from its air group.

The manager edits an isolated draft and merges only `[AirUnits]` when applied.
It rejects an Apply if another manager changed that section while this window
was open. The transfer logic validates the air-unit roster and checks that all
linked groups belong to the ship's source nation before accepting a batch.
