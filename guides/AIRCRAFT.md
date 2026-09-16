# Aircraft models

Right-click a nation and choose **Aircraft Manager** to create a new aircraft
model. Choose a saved model as a template, edit its name and statistics, and
apply. The change is staged in memory until Save or Save As writes the campaign.

Privateer reads models from `[AircraftTypes]` in `RTWGameX.bcs`. Each `ATn` model
contains a manufacturer, model name, year, role (`Purpose`), nation index,
performance values, weapons, available-aircraft stock, and a unique `Id`.
Creation copies the template's full record so unknown fields survive, assigns
the next contiguous `ATn` slot and an unused global ID, changes `Nation` to the
selected nation, and increments `ACTypesNo`. The new model starts non-obsolete
and with no development delay. Editable values are checked before staging.

The aircraft export files supplied for Game6 match model records for fighters,
dive and torpedo bombers, floatplanes, patrol aircraft, medium bombers, jets,
and helicopters. The export is a view of model statistics; it is not a separate
save file and does not directly create aircraft.

`[AirUnits]` stores squadrons separately. An `AU` unit points to a model by
`AircraftTypeId` and has its own nation, number of aircraft, base, experience,
and other state. Creating a model and available stock does not create a
squadron, assign a carrier air group, or change existing units. Those linked
operations need separate management and validation.
