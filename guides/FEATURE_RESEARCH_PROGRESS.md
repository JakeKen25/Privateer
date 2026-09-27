# Feature research progress and resume point

Checkpoint 3: 2026-09-26. Read-only content research; no game edits or new
experiments. This document supplements FEATURE_IMPLEMENTATION_GUIDE.md and
records source-specific discoveries rather than silently overriding earlier evidence.

## Reading order and current position

1. Installed manuals, FAQ and release history: relevant prose sections reviewed;
   graphical tables and remaining pages still pending detailed review.
2. User reference guides: diplomacy final findings and verified add-enemy procedure
   reviewed, including base/wartime references. Evidence JSON and parts of ship guide remain.
3. Self-describing installed data: targeted nation, research, aircraft, map and event review complete.
4. Campaign and tactical records: AAR log samples reviewed; other targeted review remains.
5. Positional/opaque formats: last; no executable analysis initiated.

PDF text was extracted locally from all six installed PDFs (248 pages total).
Extraction is indexing, NOT evidence that every page was read. Raw extracted text
stays outside the repository in outputs/feature-audit/manuals. Page numbers below
are one-based PDF pages; for the main manual these match visible page numbers.

### Sources and reviewed ranges

- Manuals/Rule the Waves 3 Manual Patch 2026.pdf (149 pages): contents/key-topic
  search, full prose on pp.12-13,31,34-35,51-56,63,65-66,106-114,126,145.
- Manuals/Rule the Waves Expanded Battles Manual EBOOK.pdf (40 pages):
  pp.11,13-19,21-22,34-36 relevant text; no complete visual-table verification yet.
- Manuals/RTW3 FAQ v1.00.pdf (12 pages): topic index/search; technology tables
  pp.7-12 detected but NOT transcribed as validated tables.
- whatsnew.pdf (17 pages): topic search; pp.6-7 read for maintenance/submarine
  changes. Additional version sections remain to review.
- Manuals/Visual Parts Catalog 2.pdf (19 pages): extracted/indexed only; requires
  visual inspection and follows the higher-value prose references.
- End Users Agreement.pdf (11 pages): extracted/indexed only; no license or
  public-domain conclusion made.
- RTW3_Diplomacy_Codex_Reference_Package.zip: read export README,
  RTW3_Alliance_Final_Findings.md and RTW3_Verified_Add_Enemy_Procedure.md.
  This package is prior user evidence, not instructions authorizing a game edit.

## Direct findings by feature

### #22 Budget: documented modifiers and conflicts

Main manual pp.12-13 describes income as national resources times naval allocation,
plus possession income; colony income declines with game time. This confirms a
missing date-dependent possession component but supplies no exact coefficients.
Keep the income formula provisional; do not invent a constant colony multiplier.

Main manual p.51 states repairs cost approximately twice active maintenance;
mothballing halts repairs and avoids that surcharge. Working-up ships are not
battle-ready and cannot simply be restored to that state by the ordinary menu.
P.52 explicitly identifies the second maintenance figure as an all-active estimate
and warns of extra wartime expense. This agrees with the user's tooltip explanation.

Main manual p.53 gives gunnery 30%, night/torpedo/damage-control 20%, at most two
subjects, 12 months to proficiency, and immediate loss of benefits on stopping.
Japan has reduced training cost. These are game rules, not a decoded billing base
or saved pending-state formula. Do not multiply the entire budget maintenance by
40% just because two subjects are selected.

The same page describes exercise participants costing twice active maintenance.
P.56 explains academy benefits but gives no numeric cost formula.
P.145 lists a good-administrator officer characteristic that reduces ship maintenance.
Do not infer the corresponding Special/Special2 integer from list order.

whatsnew.pdf p.7, v01.00.46, documents a load-time maintenance display defect that
omitted officer attributes; it says actual calculations were unaffected. P.6,
v01.00.52, describes legacy ships sometimes receiving missile maintenance before
missiles existed. These are historical defects, NOT proof that either explains
Game3's 21 discrepancy in the currently installed build. They justify recording
exact game version and display-refresh context in future evidence.

**Conflict requiring research:** main manual p.31 says halted construction costs
half of mothballed maintenance, whereas our controlled Game3 example matches
floor(saved Maintenance/2). The manual also describes acceleration as 10% faster
with 5% increased cost; observed monthly charges fit x1.15. Monthly cash flow and
total project cost are different quantities. Preserve the measured implementation
and record the conflict; do not replace it with an unsupported interpretation.
The page also says delayed construction does not charge its monthly installment,
a further case not covered by our existing normal/halted/accelerated tests.

Main manual p.126 documents three peacetime missile-stock levels and shortage risk
in the first 18 wartime months at lower levels. It does not resolve how the tooltip's
1967 is accounted for. No new missile formula established.

### #19 Submarines: useful documented meanings

Main manual pp.34-35 names coastal, medium, long-range, minelaying and missile
types and explains technology availability. Coastal boats cannot make strategic
moves during war; long-range boats operate better away from sufficient friendly
bases. These restrictions should inform a future manager but do not establish
numeric SubType mappings beyond existing evidence.

Expanded Battles manual pp.34-35 explains tactical Availability as technical state
(roughly 60 for WWI, 90 for WWII) and Accuracy as torpedo proficiency (normally 0,
with +1/-1 for better/worse). Downtime is minutes temporarily unavailable after diving.
This improves labels for SCENARIO/tactical records. Campaign fields with matching
names are strong candidates, but cross-format equivalence is not established by
name alone. Keep numeric ranges and write permissions conservative.

### #27 Aircraft/base validation and #30/#31 spawning

Main manual pp.106-112 documents carrier compatibility: light jets consume 1.5
capacity; heavy jets/jet attack require jet capability and use 1.5 capacity below
40000 tons. Technology and carrier size affect eligibility. The main manual also
requires an angled deck for heavy jets. Existing plain aircraft-count checks must
not be advertised as complete carrier compatibility validation.

P.113 documents airbase growth in steps of 20 subject to technology, and automatic
squadron creation for ship floatplanes/airship bases. P.114 explains automatic model
replacement subject to availability. This reinforces that a new model is not the
same operation as spawning an air unit, and that the game may create dependencies
after loading/turn progression. Existing carrier-transfer blocks remain justified.

Expanded Battles pp.13-16 says standalone designs are saved as .sdf and can ignore
campaign design checks, including overweight cases. The design year controls
armor/machinery technology and must represent the original design when modelling
a rebuild. Therefore an importable scenario design is not necessarily campaign-legal.

Expanded Battles pp.18-19 documents the scenario bundle: .nsc scenario, .ndt
nations, .act aircraft and .txt briefing, all with the same basename.
Design lookup order: scenario directory -> user Custom files -> user Ship Designs
-> installed Designs -> installed Data/Ides. Duplicate class names can intentionally
shadow stock designs. A future catalog must retain source path and resolution
priority rather than deduplicate by filename. This is documented scenario behavior,
not proof of the campaign's design-library conversion procedure.

### #28/#21 Diplomacy: prior evidence stronger than the initial audit summary

The final alliance reference supersedes early countdown claims. Player alliance
Allied=1 and reciprocal AIAlliance values=2 persisted through two months of a
wartime campaign with displayed alliances intact. Creation at 16 had also been
user-confirmed. Do not label values as months, strength, or normalize them to 1.
Zero correlates with no alliance, but explicit breakup effects were not tested.
Peacetime progression and assistance effects remain open.

The verified add-enemy reference reports one successful displayed change in an
existing player war: selected AI scalar Tension 6 -> 50 while General/War remained
1 and another enemy's Tension stayed 50. Dynamic nation-slot targeting is required.
This does not establish starting war from peace, forced peace, AI-only war,
arbitrary positive War values, or downstream battles/settlements. It is sufficient
to specify a narrow experimental command's evidence boundary, not a universal toggle.

Main manual pp.65-66 explains that alliances affect technology/aircraft licensing,
battle assistance and tensions; wartime allies may make separate peace instead
of normal alliance revocation. That is consistent with unresolved conditional
alliance timing, not proof of a particular stored-number interpretation.

## Unchanged research boundaries

No formulas were fitted, no game turns advanced, no save edited, no executable
inspected, and no public-domain artwork sourced. The 21 maintenance residual,
academy formula, aircraft/submarine cost functions, war transition initialization
and individual-design conversion remain unresolved. Documentation facts are
implementation constraints, not automatically verified save-field recipes.

## Checkpoint 1 resume point (superseded below)

Read the remaining high-value user references (base/wartime tension documents,
JSON evidence and ship storage/transfer guide), then inspect self-describing
nation, research, map and design template contents. Finish the manual sections
covering AAR/battle results and graphical technology tables as needed. Keep a
source/page or filename/field citation per finding, preserve conflicts, and add
another checkpoint before moving into positional formats. Do not re-extract all
PDFs or repeat the completed inventory.

## Checkpoint 2: readable guides and installed data

### #17 Custom nations: encoding and identifiers

The custom-nation prototype at a2aa879 uses cp1252 in `_read_game_text` and
recognizes nation sections with a full-line `[NationN]` match. Installed
Data/BNat1890.dat and BNat1920.dat have a UTF-8 BOM. Decoding these with cp1252
leaves three characters before the first section: only nine of ten sections match.
UTF-8-with-BOM decoding recognizes all ten. Implementation requirement: detect
BOMs before the legacy encoding fallback, retain the chosen encoding for safe
writes, and test that Nation0 survives parsing. This is a directly reproduced
parser problem; no prototype code has been changed during this audit.

Keep identifiers separate. BNat research advantages use keys such as
Research1Advantage and Research19Advantage. ResearchAreas3.dat has area sections
0 through 21; the prototype accepts advantage identifiers 1 through 22. Their
mapping is not established here. Do not silently shift identifiers based on the
apparent indexing difference.

StockMapData contains named areas, possession owner codes, Value, BaseValue,
Oil, and parallel site/coordinate/adjacency lists. These are candidate inputs for
nation setup and a map preview. They do not establish the campaign income formula.
Validate parallel-array lengths and preserve owner codes; do not substitute
campaign nation slots for installation nation identities.

### Technology and aircraft reference tables

Data/ResearchAreas3.dat has 22 areas and 572 semicolon records. Of these, 569 have
seven fields and three have eight. The extra-field rows include proximity-fuze
technologies (lines 400, 401 and 403). The existing technology parser retains
raw_fields, which must remain intact. Description is field seven in these records;
the optional eighth field's meaning remains unresolved. Never discard it while
editing a known field or infer a technology ID from row position alone.

AircraftBasicData.dat has seven role blocks and 147 rows with 22 fields.
AircraftBasicData3.dat has eleven role blocks: 255 rows have 22 fields, four have
23, and 32 have 26. The later roles include light/heavy jet fighters, jet attack
and helicopters. Rows contain decimal commas, missing-value dashes, empty fields
and trailing flags. These are useful role/year reference inputs, but lack column
labels establishing aircraft maintenance or purchase costs. A fixed-width parser
for every role would lose information. Preserve raw fields and flag unsupported
layouts rather than assign guessed cost meanings.

Gundata.dat is tab-delimited with headers c, sw, ROF, mr; TorpedoData.dat is
also tab-delimited, headed TYPE, CAL, WH, RH, SH, RL, SL, N. Neither is a labeled
budget price table. Delimiter handling must be per source.

### #14/#30/#31 Ship catalogs and transfers

The user ship-storage guide separates ShipDesignN record ordinals from internal
design IDs and treats DesignIDCount as a high-water mark, not the record count.
Its documented transfer procedure clones the complete opaque design block,
allocates above both counter and observed IDs, and reuses a clone by source nation,
source design ID and destination nation. Preserve building nation separately from
current ownership. Cached Description is not an authoritative design definition.
Carrier links remain outside that guide's supported transfer procedure.

Installed Data/IDes contains 56 .sdf and 1,237 .tdf files; Designs contains 173
.sdf files. ShipParts contains 293 BMP assets and two extensionless files, not a
ship-statistics table. A sampled battery .tdf has named design fields (including
Ready, Displacement, ShipType, Nation and BuildingNation), but those are not the
campaign BCS hull schema. Do not import a design template as a completed hull.
DataGraphics .eqs/.tus/.hus examples describe geometry rather than budget costs.

Expanded Battles manual pp.21-22 distinguishes national technology and doctrine,
design-year armor/engine technology, and individual hull radar/build year. Setting
a scenario tech year resets manual technology adjustments. These distinctions
belong in catalog provenance and validation; tactical setup is not evidence of a
campaign conversion recipe.

### #28/#21 Diplomacy and event grammar

The base/wartime reference documents distinguish dynamic campaign slots from
NationNumber. A known wartime sample still has Wars and WillGoToWar equal to zero;
those names do not justify automatically setting them to one. An observed
General/War change from -61 to 1 spans multiple months and is not an isolated
transition test. Self-cells and extra indexed records must not be interpreted as
ordinary foreign relations solely because they exist.

Data/BuldCampEventConditions.txt documents semicolon response records with caption,
budget/prestige/tension effects, affected-nation selector and condition. Its
selectors include context-dependent and all/random/most-tense targets; they are
not ordinary nation IDs. A separate chengenationcodeforevents.txt notes a code
change from 7 to 15, so these comments may reflect different format generations.
Treat the event description as a grammar lead, not a verified current schema.
Peace-related response codes do not establish a direct save-edit peace operation.
Preserve blank fields when inspecting Events.dat.

### #33 AAR and tutorial implications

Expanded Battles manual p.11 states that Exit battle opens results, while closing
the battle window ends a standalone scenario without that results screen. An AAR
collector therefore cannot equate window closure with completed result capture.
Page 36 describes Check scenario warnings as reminders, not universally fatal
errors. Tutorials should preserve those distinctions.

### Remaining work / next resume point

Read the remaining ship-guide sections and structured evidence JSON, then inspect
Events.dat, named campaign/tactical records and AAR log samples. Record field
presence separately from verified semantics. Positional design data remains last;
use existing supported codecs as evidence and mark unknown fields without reverse
engineering them. The aircraft/submarine price functions, academy formula,
maintenance residual and missile accounting remain unresolved. No new game tests,
executable analysis, feature implementation or release occurred in this checkpoint.

## Checkpoint 3: event records and AAR candidates

### Events.dat structure

All 324 nonblank lines fit 81 consecutive groups of one nine-field prompt and
three six-field responses. This matches the broad grammar in the event-condition
reference, while exposing additional prompt fields absent from the response
schema. Preserve empty semicolon fields and distinguish prompt/response records.
This validates the observed grouping only, not every numeric selector or condition.
Do not implement diplomacy transitions by copying event effect codes into saves.

### #33 AAR: directly available log inputs

Five available TLog.log/TTime.log pairs have matching line counts: 1,890, 998,
43, 699 and 4. One pair belongs to the standalone Scenarios directory. TLog holds
narrative events; TTime holds corresponding-looking day/time strings. Line-index
pairing is a supported candidate, not yet a verified lifecycle contract. Preserve
blank lines and original order; reject or explicitly flag unequal counts instead
of silently truncating with zip. Dates lack a full year/month in sampled lines.
Some narrative lines start with numeric prefixes; retain them until their meaning
is established rather than stripping them as noise.

BattleInfo.bbi has a named BATTLE INFO section with BattlePossession, BattleArea,
BattleIndex, BattleSize and BattleOpponentIndex. These are useful metadata
candidates. Their relation to the current campaign save, log freshness and battle
completion is unresolved. A collector must not attach old tactical files to the
current campaign date merely because they share a save directory.

Air Combat Log.skv has a 13-field semicolon header and 18 populated rows in the
available nonempty sample, all also 13 fields. It labels time, attacker/defender
counts, roles, aircraft types, home bases, attack/resistance values, destroyed and
damaged. Duplicate column names occur for each side: use positional, side-qualified
labels instead of a dictionary keyed only by header text.

Bombing Log.skv is less reliable: its header splits into seven fields, but all
11 populated rows across two samples split into ten. Header text visibly joins
some labels. Preserve all ten raw values; do not use the header directly to map
columns or discard extras. Full column semantics require additional research.
All four AA Log.skv files in the current corpus are empty. Header-only aircraft
logs also exist; empty/header-only does not demonstrate that no combat happened.

The .sta sample is positional numeric data without a descriptive header. Its
meaning remains unassigned; no reverse engineering was attempted. These files
must not become an invented casualty or campaign-statistics schema.

### Implementation requirements and remaining scope

For an eventual local AAR prototype, record source identity, content hash, capture
time, encoding and raw rows; detect absent/empty/malformed files; keep narrative,
combat and battle metadata separate until their association is verified. These
are recommendations from observed format hazards, not a new product commitment.
Campaign association, rotation/overwrite behavior, complete timestamps, result
finality and the meaning of numeric prefixes remain research tasks. No watcher,
cloud integration or automated collection has been implemented.

Next resume point: finish the remaining user ship-reference sections and evidence
JSON, then review named campaign/tactical records against the existing codecs.
Remaining manual pages and positional formats are still not fully reviewed.
The file inventory is complete; the content/semantic audit is deliberately not
marked complete. Checkpoints 1-3 retain the verified findings and open questions.

