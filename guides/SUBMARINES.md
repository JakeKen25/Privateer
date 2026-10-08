# Submarine Manager: read-only inventory

Privateer 0.9.8 includes a Submarine Manager to each nation's right-click
menu. In 0.9.9, the menu label is **Submarine Manager (WIP)**;
the inventory remains read-only. Search saved values, filter by state, sort columns, and select a row to
inspect all saved fields. Reused names remain separate rows identified by local
roster slot. Missing locations stay blank. No save changes are made.

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

SubType values 0–4 occur. Only 3 is labeled Long range, based on the supplied
Game3 screenshot/save comparison. Other values keep their raw number and an
unverified label. Availability and Accuracy are shown raw without claiming they
represent reliability, readiness or percentages. RemainingBuildTime is raw too.

## Implementation boundary and next evidence

The parser and window are in `privateer/submarines.py` and
`privateer/submarines_gui.py`. They do not mutate records or invoke Save.
The submarine manager roadmap issue remains open: this is its inventory phase.

Creation, removal, transfer, rename and state editing remain unavailable until
identity/link behavior, SubCount versus nation/global counters, initialization
and state transitions are established. Needed comparisons include a copied-save
order, halt/resume, completion, rename and deployment change, one at a time.
Confirm all SubType labels and Availability/Accuracy semantics, then validate
any proposed edit through game load and turn progression. No cost formula or
in-game mutation was inferred from this inspection.
