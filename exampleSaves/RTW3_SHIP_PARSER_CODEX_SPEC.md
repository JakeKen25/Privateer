# RTW3 Ship Parser and Transfer Implementation Notes for Codex

## Purpose

This document explains how Rule the Waves 3 stores ship records and ship designs, and how the save editor should parse, validate, and transfer ships safely.

The current editor is successfully reading each nation's stored `ShipCount`, but it is not parsing the actual `[NationNShips]` sections. Validation therefore reports values such as:

```text
Austria-Hungary: stored 36, actual 0
Great Britain: stored 51, actual 0
France: stored 46, actual 0
```

This is a parser bug, not evidence that the save itself is corrupt.

Do not implement mass fleet transfers until an untouched save can be loaded and validated with matching stored and parsed ship counts.

---

## 1. Immediate Bug

The save contains nation metadata in a section such as:

```text
[Nation0]
ShipCount=36
```

but actual ships are stored separately in:

```text
[Nation0Ships]
```

Ships are **not** stored in sections such as:

```text
[Ship0]
[Ship1]
```

Instead they are flattened key/value records inside the nation's ship section.

Example:

```text
[Nation0Ships]
Ship0Id=129
Ship0DesignRefId=2
Ship0Name=Cygnet
Ship0Classname=Cygnet
Ship0EnemyClassName=Cygnet
Ship0ShipType=DD
Ship0Displacement=300
Ship0CrewQuality=0
Ship0TimeToRefit=0
Ship0InPlay=1
...
Ship0BuildingNationIdx=0
...
Ship0NumberOfLogEntries=2
Ship0LogEntry0=January 1899 Laid down in Great Britain as DD Cygnet.
Ship0LogEntry1=

Ship1Id=130
Ship1DesignRefId=2
Ship1Name=Mallard
Ship1Classname=Cygnet
Ship1ShipType=DD
...
```

There are no blank lines or subsections separating ships.

The number after `Ship` is a local record slot within that nation's ship section.

For example:

```text
Ship0Id=129
```

means:

- local ship record slot = `0`
- permanent ship ID = `129`

Those values are unrelated and must not be conflated.

---

## 2. Verified Nation Section Layout

A real RTW3 save follows this pattern:

```text
[Nation0]
[Nation0Ships]
[Nation0CoastalArtillery]
[Nation0Submarines]
[Nation0Losses]

[Nation1]
[Nation1Ships]
[Nation1CoastalArtillery]
[Nation1Submarines]
[Nation1Losses]

...
```

In a verified Game7 save, stored ship counts were:

```text
Nation0 ShipCount=105
Nation1 ShipCount=93
Nation2 ShipCount=110
Nation3 ShipCount=99
Nation4 ShipCount=106
Nation5 ShipCount=67
Nation6 ShipCount=76
Nation7 ShipCount=62
Nation8 ShipCount=74
Nation9 ShipCount=0
```

Counting `ShipNId=` records in each `[NationNShips]` section matched those values exactly.

Therefore:

```python
actual_ship_count = number_of_distinct_ship_records_with_an_Id_field
```

must equal the nation's stored:

```text
ShipCount
```

for a valid normal save.

---

## 3. Do Not Filter Ships by Active or InPlay

Do not do this:

```python
if ship.active:
    nation.ships.append(ship)
```

or:

```python
if ship.in_play:
    nation.ships.append(ship)
```

Those fields do not indicate whether a strategic ship record exists.

Many valid ships have:

```text
Active=0
```

Ships under construction often have:

```text
InPlay=0
```

and must still be parsed and counted.

Verified example:

```text
Ship91Id=898
Ship91DesignRefId=26
Ship91Name=Hannibal
Ship91ShipType=B
Ship91InPlay=0
Ship91BuildProgress=25079
Ship91MonthlyCost=2006
Ship91YearBuilt=1901
Ship91BuildingNationIdx=0
```

Hannibal is under construction but is still a real ship and must count toward `ShipCount`.

The parser must parse all `ShipN` records first. Operational state should be represented as properties after parsing.

---

## 4. Correct `[NationNShips]` Parsing

Do not enumerate only known field names.

RTW3 ship field names can contain spaces. Example:

```text
Ship0Mine capacity=0
```

This regex is unsafe:

```python
r"Ship(\d+)(\w+)=(.*)"
```

because `\w+` will not correctly represent every valid field name.

Instead:

1. Split every line on the first `=`.
2. Parse the key.
3. If the key starts with `Ship` followed by digits, extract the numeric record slot.
4. Treat everything after those digits as the field name.
5. Group fields by local record slot.
6. A grouped record with an `Id` field is a real ship record.

Recommended parser:

```python
import re

SHIP_KEY_RE = re.compile(r"^Ship(?P<slot>\d+)(?P<field>.+)$")


def parse_ship_section(lines):
    records = {}

    for line in lines:
        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        match = SHIP_KEY_RE.match(key)
        if not match:
            continue

        slot = int(match.group("slot"))
        field = match.group("field")

        record = records.setdefault(slot, {})
        record[field] = value

    ships = []

    for slot in sorted(records):
        fields = records[slot]

        if "Id" not in fields:
            continue

        ships.append(
            Ship(
                slot=slot,
                ship_id=int(fields["Id"]),
                fields=fields,
            )
        )

    return ships
```

Do not discard fields the editor does not yet understand.

Recommended object model:

```python
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class Ship:
    slot: int
    ship_id: int
    fields: OrderedDict[str, str]

    @property
    def name(self):
        return self.fields.get("Name", "")

    @property
    def ship_type(self):
        return self.fields.get("ShipType", "")

    @property
    def design_ref_id(self):
        return int(self.fields["DesignRefId"])

    @design_ref_id.setter
    def design_ref_id(self, value):
        self.fields["DesignRefId"] = str(value)
```

The raw field dictionary must survive load/save intact.

---

## 5. Three Different Ship Identifiers

RTW3 uses at least three different identifiers related to a ship.

### 5.1 Local record slot

Example:

```text
Ship57Name=Hogue
```

`57` is only the record's position inside `[NationNShips]`.

It is not a permanent ship identity.

### 5.2 Permanent ship ID

Example:

```text
Ship57Id=186
```

`186` is the saved ship identity.

When transferring a ship between nations:

```text
Id=186
```

must stay unchanged.

### 5.3 Design reference ID

Example:

```text
Ship57DesignRefId=17
```

This refers to the ship's design in the current owner's design library.

Never treat the local slot, ship ID, and design reference ID as interchangeable.

---

## 6. Current Ownership Is Determined by Section Membership

A ship is owned by Nation 0 because its record is located in:

```text
[Nation0Ships]
```

A ship is owned by Nation 5 because its record is located in:

```text
[Nation5Ships]
```

Do not determine ownership from:

```text
BuildingNationIdx
```

`BuildingNationIdx` is builder/construction metadata, not authoritative current ownership.

Incorrect:

```python
ship.owner = ship.fields["BuildingNationIdx"]
```

Correct:

```python
ship.owner_nation_index = nation_index_of_containing_section
```

---

## 7. Transferring a Ship Means Moving the Entire Record

If Germany owns a ship like:

```text
[Nation5Ships]

Ship14Id=521
Ship14DesignRefId=12
Ship14Name=Bayern
Ship14Classname=Bayern
Ship14ShipType=B
...
Ship14NumberOfLogEntries=6
Ship14LogEntry0=...
Ship14LogEntry1=...
...
```

a transfer to Britain must move the entire field collection for `Ship14`.

Do not copy only selected properties.

Fields to preserve include, but are not limited to:

```text
Id
DesignRefId
Name
Classname
EnemyClassName
ShipType
Displacement
CrewQuality
BuildProgress
Maintenance
Status
YearBuilt
BuildingNationIdx
LocationAreaName
NumberOfLogEntries
LogEntry0
LogEntry1
...
```

Unknown fields must be preserved.

---

## 8. Local `ShipN` Slots Must Be Regenerated

Suppose Britain has:

```text
Ship0
...
Ship50
```

and Germany has:

```text
Ship0
...
Ship45
```

If German `Ship14` is transferred to Britain, do not paste `Ship14...` directly into Britain's section because Britain already has a local `Ship14`.

Treat prefixes as array indexes only.

After modifications, serialize Britain's ships as:

```text
Ship0...
Ship1...
...
Ship51...
```

and Germany's remaining ships as:

```text
Ship0...
Ship1...
...
Ship44...
```

The permanent `Id` field inside each record stays unchanged.

Recommended serializer logic:

```python
for new_slot, ship in enumerate(nation.ships):
    for field, value in ship.fields.items():
        output.write(f"Ship{new_slot}{field}={value}\n")
```

This automatically renumbers every attached field, including log entries such as:

```text
Ship51LogEntry0
Ship51LogEntry1
Ship51NumberOfLogEntries
```

Do not rename only a hardcoded subset of keys.

---

## 9. ShipCount Is Derived After Editing

After a transfer:

```python
nation.ship_count = len(nation.ships)
```

Write this into:

```text
[NationN]
ShipCount=X
```

Then validate:

```python
stored_ship_count == len(parsed_ship_records)
```

The current application's error:

```text
stored 36, actual 0
```

must disappear once the flattened ship sections are parsed correctly.

---

## 10. Ship Designs Are Separate and Required

Each ship contains:

```text
DesignRefId
```

RTW3 expects that design ID to exist in the **current owner's design library**.

Mapping:

```text
Nation0 -> DesignFiles0.des
Nation1 -> DesignFiles1.des
Nation2 -> DesignFiles2.des
...
```

The design filename corresponds to the save's `NationN` slot index, not the nation's historical `NationNumber`.

Example:

```text
[Nation0]
Name=Great Britain
NationNumber=2
```

Britain still uses:

```text
DesignFiles0.des
```

because Britain is currently occupying save slot `Nation0`.

If Austria-Hungary is `Nation0`, then Austria-Hungary uses:

```text
DesignFiles0.des
```

Do not derive the design filename from `NationNumber`.

---

## 11. `.des` Design Numbering Has Two Different IDs

A real design file begins roughly like:

```text
v10139
29
ShipDesign0
Cygnet
0
DD
2
0
300
...
```

Interpretation:

```text
v10139       format/version marker
29           number of design records
ShipDesign0  design record ordinal
Cygnet       design/class name
0            another positional field
DD           ship type
2            INTERNAL DESIGN ID
0            another positional field
300          displacement
```

The corresponding ship might contain:

```text
Ship0DesignRefId=2
Ship0Name=Cygnet
Ship0ShipType=DD
Ship0Displacement=300
```

Therefore:

```text
Ship0DesignRefId=2
```

resolves to the design whose **internal design ID is 2**.

It does **not** mean:

```text
ShipDesign2
```

This distinction is essential.

---

## 12. `ShipDesignN` Is a Record Ordinal, Not the Referenced Design ID

Verified example:

```text
ShipDesign0 -> internal design ID 2
ShipDesign1 -> internal design ID 3
ShipDesign2 -> internal design ID 4
...
ShipDesign28 -> internal design ID 30
```

So `ShipDesign0` and internal design ID `2` are intentionally different values.

Do not force:

```text
ShipDesign36
```

to mean:

```text
DesignRefId=36
```

Recommended design model:

```python
from dataclasses import dataclass


@dataclass
class ShipDesign:
    record_ordinal: int
    internal_id: int
    ship_type: str
    name: str
    raw_record: list[str]
```

---

## 13. `DesignIDCount` Is Not the Number of Design Records

Example nation block:

```text
DesignIDCount=30
```

while its `.des` file contains:

```text
29 design records
```

with internal IDs:

```text
2 through 30
```

Thus:

```text
Design file record count = 29
DesignIDCount = 30
```

They are different values.

`DesignIDCount` tracks the nation's highest/current internal design ID allocation, not the number of records.

Do not automatically set both to the same value.

---

## 14. Correct Design Allocation During Transfer

Suppose Britain has:

```text
DesignIDCount=30
```

and:

```text
DesignFiles0.des
record count = 29
ShipDesign0 ... ShipDesign28
internal IDs = 2 ... 30
```

Britain receives a foreign ship whose design is not already copied.

Allocate:

```python
new_internal_id = (
    max(
        destination.design_id_count,
        destination.design_library.max_internal_id()
    )
    + 1
)
```

Result:

```text
new_internal_id = 31
```

Append the copied foreign design as the next `.des` record:

```text
ShipDesign29
```

but set that copied design's internal design ID to:

```text
31
```

Then update the ship to:

```text
ShipXDesignRefId=31
```

Also update:

```text
[Nation0]
DesignIDCount=31
```

and the `.des` record-count header:

```text
29 -> 30
```

Resulting valid relationship:

```text
ShipDesign29     <- record ordinal
...
31               <- internal design ID
```

and:

```text
ShipXDesignRefId=31
```

The ordinal and internal design ID are not expected to be equal.

---

## 15. Never Delete the Donor Nation's Design

A transfer must copy the design to the destination.

It must not remove the original design from the donor nation.

If Germany gives Bayern to Britain:

```text
Germany keeps the Bayern design
Britain gets a copied Bayern design
```

This is necessary so Germany can immediately build more ships of that class.

Ordinary ship transfer must leave the source `.des` library unchanged.

---

## 16. Safe V1 Strategy for Design Copying

For V1, correctness is more important than aggressive deduplication.

Recommended workflow:

```text
Transfer ship
    ->
Resolve source design using internal DesignRefId
    ->
Clone complete design record
    ->
Allocate new destination internal design ID
    ->
Append cloned design to destination .des
    ->
Change cloned internal ID
    ->
Change transferred ship DesignRefId
```

When transferring several ships that share one source design, use a transaction-local mapping:

```python
copied_designs = {}
```

Suggested key:

```python
(source_nation_index, source_design_id)
```

Example:

```python
key = (5, 12)

if key in copied_designs:
    ship.design_ref_id = copied_designs[key]
else:
    new_id = copy_design(...)
    copied_designs[key] = new_id
    ship.design_ref_id = new_id
```

This ensures one copied class produces one destination design, even if multiple hulls share it.

---

## 17. `BuildingNationIdx` and Transfers

`BuildingNationIdx` is not current ownership.

However, it matters for transferred ships, especially ships under construction.

The safest V1 behavior is:

```python
ship.fields["BuildingNationIdx"] = str(destination.index)
```

for every transferred ship.

This prevents inherited unfinished ships from later resolving against an inappropriate foreign construction/design context.

A future advanced mode may preserve historical builder metadata for completed ships, but V1 should prioritize reliable loading.

---

## 18. Under-Construction Ships Must Be Included

A record with:

```text
InPlay=0
BuildProgress>0
```

is a ship under construction, not an absent ship.

Example:

```text
Ship91Name=Hannibal
Ship91ShipType=B
Ship91InPlay=0
Ship91BuildProgress=25079
Ship91DesignRefId=26
```

If transferred, preserve:

```text
BuildProgress
MonthlyCost
YearBuilt
all other construction fields
```

and perform normal design copying/remapping.

The receiving nation inherits the unfinished hull.

---

## 19. Recommended Atomic Transfer Algorithm

Implement ship transfer as one atomic transaction.

```python
def transfer_ship(save, ship, source, destination, design_map):
    # 1. Verify current ownership.
    assert ship in source.ships

    # 2. Resolve source design using INTERNAL design ID.
    source_design_id = ship.design_ref_id
    source_design = source.design_library.by_internal_id(
        source_design_id
    )

    if source_design is None:
        raise ValidationError(
            f"{source.name} ship {ship.name} references "
            f"missing design ID {source_design_id}"
        )

    # 3. Reuse a design already copied during this transaction.
    map_key = (source.index, source_design_id)

    if map_key in design_map:
        destination_design_id = design_map[map_key]

    else:
        # 4. Allocate destination internal design ID.
        destination_design_id = (
            max(
                destination.design_id_count,
                destination.design_library.max_internal_id()
            )
            + 1
        )

        # 5. Clone the complete raw design record.
        copied_design = source_design.clone()

        # ShipDesignN is only the destination RECORD ordinal.
        copied_design.record_ordinal = (
            destination.design_library.next_record_ordinal()
        )

        # This is the ID that ShipDesignRefId will reference.
        copied_design.internal_id = destination_design_id

        destination.design_library.append(copied_design)

        destination.design_id_count = destination_design_id

        design_map[map_key] = destination_design_id

    # 6. Update transferred ship design reference.
    ship.design_ref_id = destination_design_id

    # 7. Use destination as construction/builder nation for safe V1 transfer.
    ship.fields["BuildingNationIdx"] = str(destination.index)

    # 8. Move the entire in-memory ship object.
    source.ships.remove(ship)
    destination.ships.append(ship)

    # 9. Never change the permanent ship Id.
```

After all transfers:

```python
source.ship_count = len(source.ships)
destination.ship_count = len(destination.ships)
```

Then serialize both ship sections with newly generated local `ShipN` prefixes.

If any step fails, roll back the entire transfer transaction.

---

## 20. `.des` Files Are Positional, Not INI Files

The `.bcs` save is section/key-value based.

The `.des` format is different.

Typical structure:

```text
v10139
29
ShipDesign0
... positional lines ...
ShipDesign1
... positional lines ...
ShipDesign2
...
```

Parse design records by marker:

```python
import re

DESIGN_MARKER = re.compile(r"^ShipDesign(\d+)$")
```

Everything from one marker until the next marker belongs to that design record.

Preserve every line in the record.

For V1, do not attempt to fully reverse engineer the hundreds of design fields.

Only parse the positional values needed for safe references:

```text
record ordinal
design name
ship type
internal design ID
```

and preserve all other lines verbatim.

Validate the `.des` format/version marker, for example:

```text
v10139
```

before trusting positional offsets.

---

## 21. Avoid Blind Use of Python ConfigParser

A custom line-preserving parser is preferable for `.bcs`.

Important formatting/data to preserve:

```text
capitalization
unknown keys
field ordering
keys containing spaces
raw values
section ordering
```

Treat the `.bcs` as a game serialization format, not a generic settings file.

Recommended structure:

```python
class Section:
    name: str
    lines: list[RawLine | KeyValueLine]
```

Then layer specialized parsers on top for:

```text
NationN
NationNShips
```

This allows unchanged content to be emitted with minimal modification.

---

## 22. Recommended Ship Object

```python
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class Ship:
    original_slot: int
    fields: OrderedDict[str, str]

    @property
    def id(self) -> int:
        return int(self.fields["Id"])

    @property
    def design_ref_id(self) -> int:
        return int(self.fields["DesignRefId"])

    @design_ref_id.setter
    def design_ref_id(self, value: int):
        self.fields["DesignRefId"] = str(value)

    @property
    def name(self) -> str:
        return self.fields.get("Name", "")

    @property
    def class_name(self) -> str:
        return self.fields.get("Classname", "")

    @property
    def ship_type(self) -> str:
        return self.fields.get("ShipType", "")

    @property
    def displacement(self) -> int:
        return int(self.fields.get("Displacement", 0))

    @property
    def building_nation_idx(self) -> int:
        return int(self.fields.get("BuildingNationIdx", -1))

    @property
    def under_construction(self) -> bool:
        return (
            self.fields.get("InPlay") == "0"
            and int(self.fields.get("BuildProgress", "0")) > 0
        )
```

Expose typed properties for convenience, but preserve the full raw field dictionary.

---

## 23. Recommended Design Object

```python
from dataclasses import dataclass


@dataclass
class ShipDesign:
    record_ordinal: int
    lines: list[str]

    @property
    def name(self):
        return self.lines[1]

    @property
    def ship_type(self):
        return self.lines[3]

    @property
    def internal_id(self):
        return int(self.lines[4])

    @internal_id.setter
    def internal_id(self, value):
        self.lines[4] = str(value)
```

For the verified format:

```text
lines[0] = ShipDesignN
lines[1] = design name
lines[2] = another field
lines[3] = ship type
lines[4] = internal design ID
```

Validate the file version before assuming these offsets.

---

## 24. Validate Designs by Internal ID

Correct validation:

```python
design_ids = {
    design.internal_id
    for design in nation.design_library.designs
}

for ship in nation.ships:
    if ship.design_ref_id not in design_ids:
        error(...)
```

Incorrect validation:

```python
ShipDesign36 exists
```

A ship with:

```text
DesignRefId=36
```

requires a design record whose **internal design ID** equals 36.

The `.des` record may be named:

```text
ShipDesign29
```

or any other ordinal.

This is the exact type of mismatch that caused earlier RTW3 errors such as:

```text
Could not find design ID: 36
```

---

## 25. Required V1 Validation Report

An untouched valid save should be able to produce:

```text
Fleet Validation

Nation0: Great Britain
Stored ShipCount: 105
Parsed Records:   105
Design Refs:      105 / 105 resolved

Nation1: ...
...

Total ship records: 792
Missing design references: 0
ShipCount mismatches: 0
Duplicate permanent ship IDs: 0
Malformed ship records: 0
```

Do not consider transfer support ready until an untouched real save reaches zero critical fleet validation errors.

---

## 26. Regression Tests to Add Immediately

### Parse real ship records

```python
def test_parse_nation0_ships():
    save = load_fixture("Game7")

    assert save.nations[0].stored_ship_count == 105
    assert len(save.nations[0].ships) == 105

    ship = save.nations[0].ships[0]

    assert ship.id == 129
    assert ship.name == "Cygnet"
    assert ship.class_name == "Cygnet"
    assert ship.ship_type == "DD"
    assert ship.design_ref_id == 2
```

### Do not filter unfinished ships

```python
def test_under_construction_ship_is_not_filtered():
    save = load_fixture("Game7")

    hannibal = find_ship("Hannibal")

    assert hannibal.id == 898
    assert hannibal.fields["InPlay"] == "0"
    assert int(hannibal.fields["BuildProgress"]) == 25079

    assert hannibal in save.nations[0].ships
```

### Resolve by internal design ID, not record ordinal

```python
def test_design_ref_uses_internal_id_not_record_ordinal():
    save = load_fixture("Game7")

    design = save.nations[0].design_library.designs[0]

    assert design.record_ordinal == 0
    assert design.name == "Cygnet"
    assert design.ship_type == "DD"

    assert design.internal_id == 2

    cygnet = save.nations[0].ships[0]

    assert cygnet.design_ref_id == 2
```

This test is mandatory because it prevents conflating:

```text
ShipDesign0
```

with:

```text
Design ID 2
```

### Add additional regression tests

```text
- untouched save round-trip preserves ship counts
- all original ship design refs resolve
- transfer one completed ship
- transfer one unfinished ship
- transfer multiple ships sharing one design
- transfer ships from multiple nations with colliding design IDs
- permanent ship IDs remain unchanged
- destination local ShipN prefixes are regenerated
- source local ShipN prefixes are regenerated
- source design library remains unchanged
- destination DesignIDCount updates correctly
- .des record-count header updates correctly
- missing internal design ID is detected
- duplicate permanent ship IDs are detected
```

---

## 27. Recommended Development Order

Do not add more GUI features until the parser is correct.

Implement in this order:

1. Fix `[NationNShips]` parsing.
2. Load an untouched save.
3. Make every stored `ShipCount` equal the number of parsed records.
4. Build the `.des` parser.
5. Resolve every ship's `DesignRefId` against the current owner's design library by internal design ID.
6. Reach zero validation errors on an untouched save.
7. Implement a single-ship transfer.
8. Save the result.
9. Reload the written save.
10. Validate it again.
11. Only after that, implement batch and scenario transfers.

The current screenshot's `actual 0` errors indicate step 1 is the immediate blocker.

---

## 28. Core Rules Summary

Codex should treat these as invariants:

```text
1. Ship ownership is determined by the containing [NationNShips] section.

2. ShipN prefixes are local record slots and may be regenerated.

3. Ship Id is the permanent ship identity and must not change during transfer.

4. DesignRefId references the INTERNAL design ID in the current owner's DesignFilesN.des.

5. ShipDesignN in a .des file is a record ordinal, not the design ID referenced by ships.

6. DesignIDCount is not the number of .des records.

7. Transferring a ship requires copying its design into the destination library and remapping the ship's DesignRefId.

8. The source nation keeps its original design.

9. Unknown ship fields and unknown design lines must be preserved.

10. Ships with InPlay=0 or Active=0 must not be discarded.

11. Ships under construction are full ship records and must be transferrable.

12. ShipCount must always be recalculated from the actual roster before save.

13. All fleet edits should be atomic and validated before writing.

14. Never write a save with unresolved destination design references.
```

---

## 29. Immediate Acceptance Criterion

The next milestone is complete when the current save shown in the UI no longer produces:

```text
stored X, actual 0
```

and instead produces matching counts for every nation, followed by successful design-reference resolution.

Do not begin debugging mass-transfer logic until that baseline validation succeeds.
