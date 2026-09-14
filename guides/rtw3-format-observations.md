# RTW3 format observations

This is the evidence log for the read-only reverse-engineering phase. The files
under `developmentResources/exampleSaves/Game4` and
`developmentResources/exampleSaves/Game5` are treated as immutable
reference material. Tests open them only for reading.

## Provenance and inventory

Both supplied slots identify themselves as **Rule the Waves III 1.01.44** in the
`[VERSION]` section of their `.bcs` file. Each slot contains the files below:

- `RTWGameN.bcs`: sectioned main save and nation rosters.
- `DesignFiles0.des` through `DesignFiles8.des`: positional design libraries for
  nation slots 0 through 8. There is no `DesignFiles9.des`; Nation 9 has no ships.
- `MapDataN.dat`, `RTWGameN.off`, and `RTWGameN.sta`: associated slot files not
  yet interpreted by Privateer.

`developmentResources/exampleSaves/RTW3_SHIP_PARSER_CODEX_SPEC.md` is repository
documentation, not
an RTW3 save file. It must never be required by loading or copied as generated
save metadata.

All 26 game files are UTF-8 with a UTF-8 BOM, use CRLF exclusively, have a final
newline, and contain no NUL bytes. The `.dat`, `.off`, and `.sta` extensions do
not imply binary content in these two examples, but they remain opaque until a
codec is supported. File sizes and complete SHA-256 hashes can be reproduced
with:

```bash
Get-FileHash developmentResources\exampleSaves\Game4\*, developmentResources\exampleSaves\Game5\*
```

The source fixtures must not be used as destinations in save or transfer tests.

## Confirmed main-save grammar

The only `.bcs` in each supplied slot follows the slot number naming convention:
`Game4/RTWGame4.bcs` and `Game5/RTWGame5.bcs`. This supports that discovery rule
for these fixtures only; behavior with multiple `.bcs` files remains unknown.

Nation containers repeat in this order:

```text
[NationN]
[NationNShips]
[NationNCoastalArtillery]
[NationNSubmarines]
[NationNLosses]
```

Ships are flattened within `[NationNShips]`. A key is composed of `Ship`, a
decimal local slot, and the complete field name. Splitting at the first `=` and
then matching `^Ship(?P<slot>\d+)(?P<field>.+)$` preserves names containing
spaces, including `Mine capacity`. Distinct grouped records containing an `Id`
field are physical ships. `Id` is the permanent identity; the prefix number is
only the roster-local slot. Ownership is the containing nation section.

All records must be included regardless of `Active` or `InPlay`. In particular,
`InPlay=0` records can represent ships under construction.

### Stored and observed ship totals

| Slot | Game4 stored/parsed | Game5 stored/parsed |
|---:|---:|---:|
| Nation0 | 52 / 52 | 36 / 36 |
| Nation1 | 91 / 91 | 51 / 51 |
| Nation2 | 74 / 74 | 46 / 46 |
| Nation3 | 147 / 147 | 37 / 37 |
| Nation4 | 100 / 100 | 50 / 50 |
| Nation5 | 111 / 111 | 40 / 40 |
| Nation6 | 136 / 136 | 49 / 49 |
| Nation7 | 34 / 34 | 22 / 22 |
| Nation8 | 33 / 33 | 26 / 26 |
| Nation9 | 0 / 0 | 0 / 0 |
| **Total** | **778 / 778** | **357 / 357** |

The parser now clears this read-only portion of Gate A.

## Confirmed design-container facts

The `.des` files are positional rather than INI/section documents. Every observed
file starts with `v10139`, then a decimal record count, followed by records headed
`ShipDesignN`. The declared count equals the number of those headings in all 18
libraries. A record contains positional lines rather than `key=value` fields.
Consequently, these records use a dedicated read-only positional parser rather
than the prototype `TextDocument`/`[ShipDesignN]` model. Design cloning remains
disabled.

The supplied diagnostic identifies one positional value as the internal design
ID. Its exact schema needs a dedicated codec and regression checks before it is
used for mutation.

## Safety decisions in the first implementation change

- Real flattened rosters are parsed read-only, including unknown fields.
- Every ship reference in both examples resolves by internal design ID in the
  positional library belonging to its nation slot.
- No-op output retains each recognized file's encoding, UTF-8 BOM, line endings,
  final newline, and bytes.
- Transfers of those records fail explicitly. Moving a Python object without
  removing, inserting, and renumbering its complete source lines would corrupt
  the save.
- The guessed blanket maximum-technology operation is disabled. No observed
  profile yet proves its fields, ranges, or dependencies.
- Existing synthetic section-based fixtures remain supported only to avoid
  mixing this parser correction with a removal migration.

## Hypotheses and open questions

The following are not yet established by the two fixtures:

1. Whether permanent ship IDs are globally unique by game rule or happen to be
   unique in these examples.
2. The full positional `.des` schema, design ID limits, reserved/free slots, and
   all fields involved in design equivalence.
3. Whether roster and design ordering is semantically required.
4. How transferred under-construction ships should retain or change builder data.
5. Whether RTW3 requires BOM/CRLF or merely produces them.
6. Whether `.off`, `.sta`, or map data contain cross-file references affected by
   transfers.
7. Whether a player marker more authoritative than the Nation0 convention exists.
8. Whether checksums or indexes outside the observed counts need maintenance.

## Next implementation slice

Fully map the remaining positional design fields and gate the codec with more
malformed-record fixtures. Then build an immutable transfer plan and implement
physical roster serialization plus positional design cloning without changing
untouched source records.
