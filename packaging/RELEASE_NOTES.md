# Privateer 0.92

Privateer 0.92 expands the stable Rule the Waves 3 save editor with safer colony
transfers, clearer ship-state handling, unrest editing, save reloading, and a
guided first-launch setup.

## Major improvements

- The Colony Manager now shows named map regions instead of raw area numbers.
- National home regions are identified and locked so they cannot be transferred
  through the Colony Manager.
- The Transfer Ships screen now displays saved ship statuses, including Active
  Fleet, Reserve, Mothballed, Foreign Service, and Under Construction.
- Destroyed, sunk, mined, scrapped, retired, and museum ships are omitted from
  the transfer list and rejected by the transfer API.
- The Economy and Unrest Manager can edit each nation's `UnrestLevel` alongside
  funds and base resources. These changes are staged and validated together.
- A Reload button refreshes the currently selected save without opening the
  folder picker again. The selected nation is retained, and Privateer warns
  before discarding unsaved changes.
- First Run Configuration now collects the Rule the Waves 3 installation folder,
  save-game folder, and backup preferences. Every option remains available later
  through Settings.

## Additional refinements

- Colony, ship-transfer, economy, and main tables retain sortable column headers.
- Loading, reloading, validating, and saving continue to use responsive progress
  windows for larger campaigns.
- Economy and Infrastructure menu names now reflect unrest and planned
  fortification management.

## Known limitations

- Economy projections are estimates and still require refinement against the
  game's internal calculations.
- Relationship editing remains under development. Fortification editing and Ship
  Spawner remain placeholders.
- Transfers involving aircraft carriers or certain active campaign-division
  relationships remain blocked until their linked records can be handled safely.

Keep a known-good backup and test important edits in a copied save slot.
