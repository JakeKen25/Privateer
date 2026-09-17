# Privateer 0.931 Beta

Privateer 0.931 Beta fixes an aircraft-default progression issue identified
after 0.93 Beta was published.

## Corrected aircraft progression

- If the selected aircraft type has no data for the current campaign year,
  Privateer now interpolates every field between the nearest earlier and later
  yearly averages, rounding the result to the nearest whole number.
- For example, a year halfway between two observed years receives the midpoint
  of each field's actual averages from those surrounding years.
- After the final observed year for a type, its latest averages carry forward.
- The per-field minimum fallback is now reserved for designs earlier than every
  observed model of that type. This supports deliberately early aircraft, such
  as attempting to design a helicopter before helicopters normally appear.
- All generated values remain editable before the aircraft model is applied.

## Aircraft Manager introduced in 0.93 Beta

- Create aircraft models for any nation with a role-specific editor.
- Use **Privateer** as the default manufacturer or select a manufacturer already
  used by the nation.
- Read the design year from the current campaign.
- Show only fields relevant to the selected aircraft role.
- Draw plausible defaults from year-by-year averages of the 1,121 aircraft
  models observed in Game 6.

## Known limitations

- Aircraft Manager creates aircraft model definitions; it does not create or
  modify air units or squadrons.
- The averages are starting values and may not match every campaign's technology
  state or the game's internal aircraft generator.
- Economy projections are estimates. Relationship editing remains under
  development, and fortification editing and Ship Spawner remain placeholders.

Keep automatic backups enabled and test important edits in a copied save slot.
