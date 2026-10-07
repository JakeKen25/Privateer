# Aircraft models

Right-click a nation and choose **Aircraft Manager** to create a new aircraft
model. Choose the aircraft type from the dropdown, then edit its manufacturer,
name, and visible statistics. The design year comes from `[General]Year` in the
currently loaded campaign. **Privateer** is the default manufacturer; the
manufacturer dropdown also lists every manufacturer already used by the
selected nation's aircraft models. The change is staged in memory until Save
or Save As writes the campaign.

The Equivalent year (stats) slider selects the stored defaults for that year.
Its bounds match the first and last recorded Game 6 model years for the chosen
aircraft type. The initial selection is the campaign year, or the nearest
endpoint when the campaign is outside that range. Changing aircraft type resets
this selection. Moving the slider replaces the editable stats; the design year
and base model year remain the current campaign year.

`privateer/aircraft_year_defaults.py` contains one stored row for every year
within each type's recorded range, including precomputed intermediate years.
There are no rows before or after that range and no runtime interpolation.
The source aggregates remain in `privateer/aircraft_game6_averages.py`.

Privateer reads models from `[AircraftTypes]` in `RTWGameX.bcs`. Each `ATn` model
contains a manufacturer, model name, year, role (`Purpose`), nation index,
performance values, weapons, available-aircraft stock, and a unique `Id`.
When existing models are present, creation copies a compatible saved source model's full record so unknown fields
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

## Creating the first aircraft model

Development 0.9.8.1 opens the manager even when `ACTypesNo=0`. The empty list
shows "No aircraft are detected in this save" without an error dialog. Choose
a type, adjust the statistics, and Apply as usual; no source model is required.

The first model uses bundled role/year statistics, with the equivalent year
clamped to the available table and the design/base year kept at the campaign
year. The observed record schema supplies Version=0, ReliabilityKnown=1,
ValuesKnown=0, Obsolete=0 and DevelopmentTime=0. These are initialization choices,
not newly verified interpretations of the engine's knowledge flags. Initial
stock is zero unless changed in the form. Fields not applicable to the selected
role are zeroed (Radar uses -1). Creation assigns AT0, the target nation, and a
fresh ID from General/IDNo, then increments ACTypesNo and IDNo. Subsequent models
can use that saved model as their source. Squadrons and nation technology are
not changed. Missing/ambiguous sections and invalid counters still report errors.

Automated checks cover all ten roles, save/reload, sequential IDs, and rejected
invalid edits. First-model creation still needs in-game load and turn validation,
including campaigns predating aviation; creating a model does not unlock aviation.
