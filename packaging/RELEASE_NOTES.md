# Privateer 0.93 Beta

Privateer 0.93 Beta introduces aircraft-model creation and improves how aircraft
design values are selected for the current campaign. This is a beta release so
the new aircraft workflow can receive broader in-game testing before it becomes
part of the next stable release.

## Aircraft Manager

- Create a new aircraft model for any nation from the nation context menu.
- Choose among all supported aircraft roles, including fighters, bombers,
  floatplanes, patrol aircraft, jets, and helicopters.
- Start with **Privateer** as the manufacturer or choose a manufacturer already
  used by the selected nation.
- Set the model's design year automatically from the current campaign year.
- Show only the statistics that apply to the selected aircraft role.
- Prefill editable statistics using year-by-year averages derived from all 1,121
  aircraft models observed in Game 6.
- When a role has no model in the campaign year, use that role's lowest observed
  yearly average for each field as a conservative starting point.
- Preserve the source model's unknown internal fields and leave existing air
  units and squadrons unchanged.

## Safety and validation

- New aircraft models receive a contiguous aircraft slot and an ID allocated
  through the campaign's global ID counter.
- Aircraft-only saves compare all other loaded campaign files and sections with
  their original data before writing.
- Existing unrelated ship-design validation findings no longer prevent a valid
  aircraft-only edit from being saved.
- The complete automated suite passes 91 tests, including aircraft creation in a
  fixture that already contains an unrelated missing ship-design reference.

## Known limitations

- Aircraft Manager creates aircraft model definitions; it does not create or
  modify air units or squadrons.
- The Game 6 averages are practical starting values and may not match every
  campaign's technology state or the game's internal aircraft generator.
- Economy projections are estimates and still require refinement.
- Relationship editing remains under development. Fortification editing and Ship
  Spawner remain placeholders.

Keep automatic backups enabled and test important edits in a copied save slot.
