# Submarine Manager

Published 0.9.9.1 remains read-only. Development 0.9.9.6 spawns completed
submarines using built-in references from the completed Game6 boats below.
It supersedes the destination-template restriction in 0.9.9.4.

## Spawn

Choose **Submarine Type**, review the editable **Privateer X** default name,
choose a spawn location, and select **Spawn**. The window stays open and proposes
the next unused positive number after each spawn. Historical names reserve
numbers too. Close retains spawned boats in memory; Save or Save As writes them.

No existing submarine or local Game6 installation is required. Empty rosters
are supported; an absent submarine section is created after validation.
Locations include the destination nation's saved BuildAreaName and its existing
in-service submarine locations. Missing location/counter/year or inconsistent
roster data blocks the operation.

## Built-in reference records

Completed Game6/RTWGame6.bcs Nation0Submarines, inspected October 8, 2026:

| Reference | Type | SubType | Availability | Accuracy |
| --- | --- | --- | --- | --- |
| S-120 / Sub92 | SSC Coastal | 2 | 135 | 0 |
| S-121 / Sub93 | SS Submarine | 0 | 135 | 0 |
| S-122 / Sub94 | SSM Minelaying | 1 | 135 | 1 |
| S-123 / Sub95 | SSM Minelaying | 1 | 135 | 0 |
| S-124 / Sub96 | SSL Long range | 3 | 135 | 0 |
| S-125 / Sub97 | SSG Missile | 4 | 135 | 1 |

Only the S-123 minelayer reference (Accuracy=0) is offered, by user choice.
S-122 remains in the evidence table above but is not a selectable type.
Accuracy semantics remain unresolved.
The reference type, Availability and Accuracy values are bundled in source code.
Privateer does not read Game6 at runtime or copy US ownership/location/name.

New records use the chosen name/location, destination campaign year, InPlay=1,
RemainingBuildTime=0, Halted=0, Sunk=0, Active=0, blank Fate, and XXX destination
and ordered areas. SubCount and the nation's SubNumber each advance once.
No global ID, technology unlock, or direct construction charge is added.
Stats are fixed Game6 values, not adapted to destination technology or year.

## Validation and remaining work

26 targeted tests cover all five selectable references in empty and absent rosters,
round-trip parsing, naming and rejected inputs without mutation. Validate game
loading, readiness/deployment, maintenance, turn progression and naming continuity
with an ordinary in-game submarine order. In-game behavior across eras remains
unverified; Availability/Accuracy and naming-counter semantics are unresolved.
The menu retains (WIP). Editing, transfer and deletion are not implemented.
