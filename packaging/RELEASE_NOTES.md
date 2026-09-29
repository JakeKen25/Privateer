# Privateer 0.9.6 — local testing build

Every budget field now shows a numeric estimate, including total expenses,
monthly balance and a separate all-active maintenance estimate. Saved charges
take precedence where available; missing costs use documented reference rates.
An Estimate assumptions dialog adjusts aircraft, submarine, infrastructure,
training, academy, dock and income assumptions without changing game saves.

The budget remains approximate. Game3-derived rates are not universal formulas;
missing inputs can produce explicitly disclosed zero fallbacks. See
[calculation rules](../guides/BUDGET_ESTIMATES.md). Public release remains 0.9.4.

# Privateer 0.9.4 (historical public release)

This release adds fortification management and more precise technology editing.

## Fortifications Manager

- View and sort each nation’s fortification roster alongside its dockyard size.
- Add coastal and turreted batteries, missile batteries, MTB squadrons, airship bases, and airbases in owned possessions.
- Edit built installations and resize airbases while preserving installation IDs and aircraft assignments.
- New installations are built immediately without deducting funds. Construction and retired entries remain read-only.
- Airbase sizes respect the campaign limit; bases cannot shrink below their assigned aircraft capacity.

## Technology Manager

- Keep the cumulative research-area sliders, with individual checkboxes to enable or skip specific technologies.
- View each technology’s description and typical unlock year.
- Moving a slider replaces that area’s individual exceptions with a fresh cumulative selection.

## Aircraft Manager testing status

The Aircraft Manager appears to be working, but has not been extensively tested. Keep backups and verify generated aircraft in-game before relying on them in an ongoing campaign.

## Validation and installation

103 automated tests passed, along with Tk interaction checks and a temporary Game 6 save/reload check. The live Game 6 save was not modified. Newly created fortifications have not yet been verified through an RTW3 turn advance.

Download the Windows ZIP, extract the entire folder, and run Privateer.exe. Keep the _internal folder beside the executable. INSTALL.txt is packaged with the application; no separate Python installation is required.

The application now displays the corrected version number, 0.9.4.
