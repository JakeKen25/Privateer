# Submarine Manager

Published 0.9.9.1 provides a read-only inventory. Development 0.9.9.2 adds
construction from an existing same-nation submarine construction record.
The menu retains **(WIP)** pending in-game validation.

## Create a submarine (development 0.9.9.2)

Select a construction template, enter a unique name, and choose **Create**.
The new boat appears under construction and the window stays open. **Close**
retains created boats in memory; **Save** or **Save As** in the main window
writes the campaign. No live save is changed merely by opening this manager.

The template determines the type, saved Availability and Accuracy, and remaining
build time. This is a copy of remaining time, not a calculation of a fresh full
construction duration. Choose a newly ordered template when testing new orders.
If the nation has no suitable construction record, first order the desired type
in RTW3, save, and reload Privateer. Creation from an empty inventory, operational
boats, historical boats, and halted orders is not supported by this first pass.

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

Creation appends SubN fields, increments SubCount, preserves unknown template
fields, and initializes the observed construction state without a location.
Nation SubNumber is advanced once per boat: Game6 has SubNumber=126 after
S-125. Treat its precise naming behavior as an inference pending game testing.
No global ID is assigned: none was observed in these submarine records.
Funds, technology, designs, and explicit cost fields are not changed. The game
must be checked for normal construction charging and completion behavior.

Malformed counts, duplicate fields/sections, invalid counters, nonpositive build
time, and duplicate names block creation before mutation. Existing records,
other nations, and original construction orders remain unchanged.

## Remaining validation

Test a copied campaign: load each created type, advance a turn, check normal
construction charging and progress, complete a boat, and place another normal
in-game order to check the naming counter. Availability/Accuracy semantics,
technology-dependent initial values, full build durations, and any additional
bookkeeping remain unresolved. Do not treat successful save parsing as in-game
validation. Editing, transfer, deletion, and instant commissioning are unavailable.

## Earlier inventory research (historical)

Source: the loaded numbered campaign BCS, section `[NationNSubmarines]`.
`SubCount` declares the roster size; `SubX...` groups each record. Count/slot
disagreements are reported without hiding parsed entries. Duplicate sections or
keys reject the ambiguous inventory. Missing sections are distinguished from
an explicitly empty roster.

The 2026-09-29 read-only inspection found 2,506 records across nine current saves:
Game1 179, Game2 100, Game3 205, Game4 212, Game5 0, Game6 384, Game7 0,
Game8 57, Game9 1,369. Save slots are mutable snapshots; these counts supersede
earlier observations only for this inspection, not all campaigns using those slots.

Observed fields: Name, Availability, Accuracy, SubType, Fate, YearBuilt,
RemainingBuildTime, Halted, Sunk, Active, InPlay, LocationAreaName,
DestinationAreaName and OrderedAreaName. No permanent Id, Maintenance or
MonthlyCost was present in this submarine roster sample.

State interpretation checks Sunk and final Fate before InPlay. Sunk=1 is Sunk;
nonblank Fate other than XXX is Historical. With Sunk=0, InPlay=0 is construction
(Halted=1 distinguishes halted), while InPlay=1 is In service. Unsupported or
missing flags show Unknown. In service does not assert deployment or readiness.
Every observed Active value was zero; it is not used as an operational/deletion
flag. History may retain InPlay=1 and positive remaining construction time.

All five SubType labels are now identified above. Availability and Accuracy
remain raw saved values. The earlier inventory-only boundary is superseded by
the development construction workflow above.
