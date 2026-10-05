# Privateer 0.9.8.1 — development, unpublished

- Colony Manager now permits ordinary possessions inside home areas to transfer,
  while protecting individual home provinces with saved Value >= 200.
- Transfer Ships now labels status 1 as Reserve Fleet, 3 as Trade Protection,
  and 4 as Raider. Active Fleet, Mothballed, Foreign Service and Museum Ship
  retain their existing mappings and lifecycle safeguards.
- Updated the ship-transfer guide with all seven supplied codes and recorded
  user-confirmed combat and turn advancement for the HDP-64 cross-save test.
- Version metadata advances to 0.9.8.1. No dedicated release or tag is published.

# Privateer 0.9.8

This release includes all updates since 0.9.4: a read-only Submarine Manager, expanded budget estimates, a monthly-balance planning range, and the completed game-data research handoff.

## Budget calculator: estimates and a ±10% range

**The final monthly balance now includes a ±10% planning range alongside the central estimate, rather than presenting that estimate as an exact result. The underlying budget calculations are still under review.** This is a chosen planning allowance, not a measured confidence interval or a guarantee that actual costs fall inside it.

For example, an estimated balance of -3,795 displays a range of -4,174.5 to -3,415.5. Negative balances keep correctly ordered bounds; zero displays 0.0 to 0.0. The range does not change the underlying income or expense calculations.

Every calculator row now displays a numeric estimate, including total expenses and monthly balance. Changes since 0.9.4 include:

- Provisional income now accounts for saved budget modifier and fleet size instead of the original fixed resource multiplier. Research uses the resulting monthly-income estimate.
- Historical and museum ships are excluded from surface maintenance and construction.
- Reserve and mothball maintenance reductions use nearest-even rounding; observed class-2 search-radar charges are included for destroyers, light cruisers and carriers.
- Surface construction handles normal, accelerated and halted charges, with halted construction taking precedence.
- Normal unfinished fortification construction uses saved monthly cost; completed installations are kept out of construction.
- Player intelligence uses the confirmed rate of 80 per level per target, summed across targets.
- Installation maintenance and missing submarine, aircraft, academy, training and dock costs now have explicitly documented reference estimates.
- An **Estimate assumptions…** dialog lets you adjust the fallback rates and income factor for the current calculator window.
- A scrollable explanation identifies the inputs, assumptions and unresolved components. A separate all-active maintenance estimate is informational and is not added again to expenses.
- Calculator changes and assumptions do not write projected costs to game saves. Existing Funds, Base Resources and Unrest editing remains separate.

**Accuracy limitations:** several fallback rates are calibrated to the Game3 example and are not verified across nations, eras or submarine/aircraft types. Annual income, aircraft/pilot costs, submarine pricing, academy/training timing, missile-storage accounting and other maintenance modifiers remain unresolved. Some missing inputs use disclosed zero fallbacks. The Game3 ship-maintenance aggregate still differs from the displayed ship rows by 21; no arbitrary correction was added.

## Submarine Manager

Right-click a nation and choose **Submarine Manager**.

- Search the submarine roster and sort its columns.
- Filter in-service boats, boats under construction, halted construction, sunk/history records and unknown states.
- Inspect every saved field for the selected record.
- Keep repeated names as separate roster entries and retain missing locations explicitly.
- Check sunk/final-fate state before ordinary service/construction flags.
- Show unverified type codes and statistics as raw values rather than guessing labels.
- Report missing rosters, inconsistent counts and ambiguous duplicate fields.

This is the **read-only inventory phase**. Submarine creation, editing, transfer and removal are not implemented. Save-slot numbers are not permanent submarine IDs. No in-game turn-progression validation of submarine edits is claimed.

## Research and documentation

- Added the nine-save budget comparison and controlled Game3 experiment findings.
- Documented maintenance-tooltip, construction, training and aircraft reconciliations.
- Added the feature implementation guide, field catalog, research checkpoints, readiness matrix and final source-audit handoff.
- Documented the current calculator assumptions and submarine-manager implementation boundaries.
- Updated roadmap/milestone planning, including the future AAR Logger; these plans are not shipped features.

## Validation

132 automated tests passed before release preparation. Read-only checks covered 2,506 submarine records across nine save slots. GUI checks covered submarine search, duplicate names, filtering, details and sorting, plus calculator assumptions and positive/negative/zero balance ranges. The local Windows build was opened successfully. No live save files were modified by these checks.

## Installation

Download **Privateer-0.9.8-Windows-x64.zip**, extract the entire archive and run **Privateer.exe**. Keep the accompanying runtime folder beside the executable. Python is not required.

Close RTW3 before saving edits. Use **Save As** for the first edited copy and retain a known-good backup.
