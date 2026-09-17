# Aircraft models

Right-click a nation and choose **Aircraft Manager** to create a new aircraft
model. Choose the aircraft type from the dropdown, then edit its manufacturer,
name, and visible statistics. The design year comes from `[General]Year` in the
currently loaded campaign. **Privateer** is the default manufacturer; the
manufacturer dropdown also lists every manufacturer already used by the
selected nation's aircraft models. The change is staged in memory until Save
or Save As writes the campaign.

The form uses derived averages from all 1,121 Game 6 aircraft model records,
grouped by aircraft type and model year. Numeric game fields are rounded to
whole numbers. If the campaign year falls between two years with Game 6 models,
each field is linearly interpolated between those yearly averages and rounded to
the nearest whole number. After the final observed year, the latest averages
carry forward. The per-field lowest observed averages are used only when the
requested year is earlier than every observed model for that type. For example,
a helicopter created in 1914 uses those early-design defaults because Game 6
helicopters begin in 1954. All displayed defaults remain editable. The form
shows fields observed as relevant for that aircraft type; fields unused by the
type are hidden and set to inactive defaults. The aggregate table lives in
`privateer/aircraft_game6_averages.py` and contains no model names or raw save
records.

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
