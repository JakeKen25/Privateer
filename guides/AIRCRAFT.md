# Aircraft models

Right-click a nation and choose **Aircraft Manager** to create a new aircraft
model. Choose the aircraft type from the dropdown, then edit its manufacturer,
name, and visible statistics. The design year comes from `[General]Year` in the
currently loaded campaign. **Privateer** is the default manufacturer; the
manufacturer dropdown also lists every manufacturer already used by the
selected nation's aircraft models. The change is staged in memory until Save
or Save As writes the campaign.

The form reads a static table row for the selected aircraft type and exact
campaign year. `privateer/aircraft_year_defaults.py` contains all years from
1800 through 2200. No interpolation or year-based stat calculations run when
opening the form or adding an aircraft.

The table was prepared from the 1,121 Game 6 models summarized in
`privateer/aircraft_game6_averages.py`. Missing intermediate years were filled
once using linear interpolation with whole-number half-up rounding. Years
before the first observed model use per-field minimum averages; years after
the last observed model repeat its averages. These values are stored explicitly
in the table. Both files contain aggregate statistics, not raw save records.
All displayed defaults remain editable. Fields unused by the selected type
are hidden and set to inactive defaults.

Privateer reads models from `[AircraftTypes]` in `RTWGameX.bcs`. Each `ATn` model
contains a manufacturer, model name, year, role (`Purpose`), nation index,
performance values, weapons, available-aircraft stock, and a unique `Id`.
Creation copies a compatible saved source model's full record so unknown fields
survive, assigns the next contiguous `ATn` slot and an unused global ID, changes
`Nation` and `Purpose` to the selected nation and type, advances `[General]IDNo`,
and increments `ACTypesNo`. The new model starts non-obsolete and with no
development delay. Editable values are checked before staging.

The aircraft export files supplied for Game6 match model records for fighters,
dive and torpedo bombers, floatplanes, patrol aircraft, medium bombers, jets,
and helicopters. The export is a view of model statistics; it is not a separate
save file and does not directly create aircraft.

`[AirUnits]` stores squadrons separately. An `AU` unit points to a model by
`AircraftTypeId` and has its own nation, number of aircraft, base, experience,
and other state. Creating a model and available stock does not create a
squadron, assign a carrier air group, or change existing units. Those linked
operations need separate management and validation.
