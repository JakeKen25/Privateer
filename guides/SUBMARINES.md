# Submarine Manager

Published 0.9.9.1 provides a read-only inventory. Development 0.9.9.3 adds
**Spawn** for completed submarines, superseding the construction-only 0.9.9.2
implementation. The menu retains **(WIP)** pending in-game validation.

## Spawn a submarine (development 0.9.9.3)

Select a same-nation in-service template, enter a unique name,
choose a spawn location, and select **Spawn**. The boat appears in service and
the window stays open. **Close** retains spawned boats in memory; **Save** or
**Save As** in the main window writes the campaign.

Type, Availability, Accuracy and unknown template fields are copied. The new
boat has InPlay=1, RemainingBuildTime=0, YearBuilt equal to General/Year,
Halted=0, Sunk=0, Active=0, blank Fate, and DestinationAreaName/OrderedAreaName=XXX.
LocationAreaName is the selected location. These service-state fields match
Game6 Sub90/S-118 and Sub91/S-119, both built in 1968 with zero build time,
InPlay=1 and North American East Coast as their location.

Locations are limited to existing in-service submarine locations for that
nation. At least one in-service boat and a suitable template are required.
Spawning does not wait for construction or directly deduct construction costs.
No technology unlock, cost formula, or runtime game behavior is inferred.

## Validation

24 targeted tests passed, covering all types, service initialization, counters,
repeated spawning, save/reload, invalid names/locations and malformed inputs.
In-game loading, readiness, deployment, maintenance and turn progression still
need testing, along with an ordinary in-game order to check naming continuity.
Availability/Accuracy semantics and naming-counter behavior remain unresolved.
Editing, transfer and deletion are unavailable.

## Type identification: Game6 and user screenshot, October 8, 2026

| Saved SubType | Game type | Screenshot boat | RemainingBuildTime | Accuracy |
| --- | --- | --- | --- | --- |
| 0 | SS / Submarine | S-121 | 10 | 0 |
| 1 | SSM / Minelaying submarine | S-122, S-123 | 10 | 1, 0 |
| 2 | SSC / Coastal submarine | S-120 | 8 | 0 |
| 3 | SSL / Long range submarine | S-124 | 10 | 0 |
| 4 | SSG / Missile submarine | S-125 | 12 | 1 |

Source: Game6/RTWGame6.bcs, [Nation0Submarines], Sub92 through Sub97,
matched by name to the supplied in-game construction screenshot. All six have
Availability=135, YearBuilt=0, Halted=0, Sunk=0, Active=0, InPlay=0,
blank Fate, and DestinationAreaName/OrderedAreaName=XXX. These construction
records omit LocationAreaName. The screenshot's displacement is not stored in
these records and is not written by Privateer. Accuracy is not a type selector:
both observed Accuracy values appear on minelayers.

Spawning appends SubN fields and increments SubCount and the nation's
SubNumber once per boat. Game6 has SubNumber=126 after S-125; its precise naming
behavior remains an inference. No global ID was observed in submarine records.
Existing boats, other nations, funds and technology remain unchanged. Unknown
fields are preserved from the template. Missing/ambiguous layouts are rejected.
