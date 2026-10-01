# Privateer feature implementation guide

> Current implementation overlay, 2026-09-30: released Privateer is 0.9.8.
> Numeric budget estimates and read-only submarine inventory are shipped.
> The source audit and milestone baselines below retain their historical dates.
> See [current status](PROJECT_STATUS.md); later research checkpoints supersede
> initial inventory-only coverage statements.

Audit date: 2026-09-26. Scope: installed RTW3 data, all nine local save slots,
current public releases, open GitHub issues and their milestone descriptions,
and the isolated custom-nation prototype. This is an implementation handoff,
not a claim that all formats or planned operations are decoded.

## Reading this guide

- **Observed** means a field/file was read in this audit or a supplied screenshot.
- **Supported** means an existing Privateer implementation handles that operation;
  it does not imply multi-turn validation in the game.
- **Research required** identifies an unanswered question. No new game experiments,
  executable analysis, internet investigation, or attempts to solve those questions
  were performed for this audit.
- Counts and example values describe this installation and save snapshot, not all
  RTW3 versions. Preserve unknown fields, encoding, newline style and record order.

## Scope, release state and source coverage

Installation root: `C:/Program Files (x86)/Steam/steamapps/common/Rule the Waves 3`.
Save root: `C:/Users/Yunda/Documents/My Games/Rule the Waves 3/Save`.
Relative paths below are resolved against one of those roots or this repository.

The inventory covers 3,856 installed files (146,829,059 bytes) and 164 save files
(259,702,708 bytes). Final enumeration/content-scan errors: zero. All files were
inventoried; supported text-like files were scanned for section/key schemas.
Binary images/audio, executable libraries, map layers and PDFs were inventoried,
not decoded, executed, decompiled, visually reviewed or exhaustively interpreted.
Positional text was recognized but not assigned invented field meanings.
A schema scan is not a complete semantic specification of every file.

At the 2026-09-26 audit start, the public release was **0.9.4** (`v0.9.4`)
and the local testing build was **0.9.5**. These are historical baselines,
not current release numbers. At that time:

- `main`: `a9937c364a3cda9439171e30d7662c61eaaa4064`.
- `develop`: `639e51bfee6488b415fd812bfca6d8302e578d6f`.
- `feature/custom-nation-maker`: `a2aa87991072aac9d8644e8ba65026129d13ab13`.

Open issues and comments were queried: 15 issues, no comments on those issues.
Milestone descriptions were read from the milestone objects embedded in issue
responses; the connector rejected the standalone milestones endpoint.
All target versions below are proposals, not release declarations.
The older format-observations guide describes an earlier parser stage; its
statement that design copying is disabled is superseded by current SHIPS.md
and ship_transfers.py. Old release notes likewise describe historical states.

## Campaign comparison set

| Slot | Player | Date | Best existing evidence/use |
|---|---|---|---|
| Game1 | Germany | January 1920 | Early technology, funds, AF/RF/MB/FS comparisons |
| Game2 | China | June 1907 | Accelerated surface construction, early fleet |
| Game3 | China | December 1945 | Budget tooltip, maintenance, aircraft, training, construction |
| Game4 | Soviet Union | January 1935 | Existing parser fixture, mixed designs |
| Game5 | Austria-Hungary | January 1900 | Early parser fixture and small budget |
| Game6 | USA | October 1971 | Late aircraft roles, all-nation fortification coverage |
| Game7 | USA | December 1970 | Late aircraft and accelerated construction |
| Game8 | Spain | January 1935 | Small fleet; unresolved historical intelligence discrepancy |
| Game9 | China | December 1926 | Historical fates, museum status, unfinished ships |

Treat live saves as evidence, never regression-test destinations. Save copies can
change between audits. Preserve a hashed snapshot before any future controlled
comparison. Autosave is an independent state, not interchangeable with RTWGameX.

## File families and how features connect

| Source | Available data | Consumers / limitations |
|---|---|---|
| `Save/GameX/RTWGameX.bcs` | General, nation, hull, fortification, submarine, loss, aircraft, air-unit records | Primary manager state; local record slots are not permanent IDs |
| `Save/GameX/DesignFilesN.des` | Positional design libraries, version headers, design IDs | Transfers/spawning; use existing codec, preserve opaque record content |
| `Save/GameX/MapDataX.dat` | Regions, possessions, owner/base/building data | Colonies, installations, nation geography; not the stock map template |
| `Save/GameX/RTWGameX.off` | Officers and campaign divisions | Commander/division links; historical officers are retained |
| `Save/GameX/RTWGameX.sac` | Tactical environment, forces, ships, reports and damage state | AAR candidate; latest tactical state is not proven to be final battle result |
| `Save/GameX/BattleInfo.bbi` | Battle possession, area, index, size, opponent index | AAR metadata; battle association needs validation |
| `Save/GameX/TLog.log`, `TTime.log` | Event text and separate timestamp-like lines | AAR candidates; one-to-one alignment is NOT established |
| `Save/GameX/*Log.skv` | Semicolon-separated combat/bombing/AA logs when present | AAR candidates; some files are empty |
| `Save/GameX/RTWGameX.sta` | Positional statistics-like text | Undecoded; do not assign meanings to positions |
| `Data/BNat*.dat` | Era-specific nation definitions | Custom nation templates; not current campaign state |
| `Data/*Names.txt`, `*ShipNames*.dat`, `*WarInfo*.dat` | Officer names, ship-name pools, nation war/scenario settings | Custom nations; retain case/era conventions and template fields |
| `Data/MapData*.dat` | Stock possession/site geography | Base site choices, custom nation geography |
| `Data/IDes/*`, `Designs/*`, `ShipParts/*` | Individual design assets and dependencies | Spawner catalog; .sdf/.tdf cannot be assumed identical to .des blocks |
| `Data/ResearchAreas*.dat`, `Gundata.dat`, `TorpedoData.dat` | Technology/weapon definitions | Existing managers and compatibility checks |
| `Data/AircraftBasicData*.dat`, aircraft .acs files | Aircraft generation/shape data | Aircraft validation; not a proven expense formula |
| `Scenarios/*.NSC`, `*.ndt`, `*.act` | Tactical setup, nations and aircraft | Useful parser examples; do not mix scenario indices with campaign IDs |
| `Flags/`, `Images/`, `Data/Graphics/` | Existing artwork and geometric components | Runtime references; presence does NOT establish redistribution/public-domain rights |
| `Manuals/`, PDFs | Documentation assets | Inventory only in this audit; new manual research remains optional future work |
| EXE/DLL, launcher, sounds, layers | Runtime/opaque assets | No planned save edit requires changing these |

Installed extension counts: 1,237 .tdf, 229 .sdf, 1,120 .eqs, 358 .tus,
18 .hus, 77 .dat, 44 .acs, 349 .bmp, 261 .jpg; other formats are listed in
FEATURE_DATA_CATALOG.md. .eqs/.tus/.hus samples contain polygon point data;
they are graphics geometry, not automatically expense tables.

## Shared implementation requirements

Use `document.py`, `save.py`, `validation.py` and the existing staged-edit model.
Keep reads separate from writes. Validate a complete batch before mutating live
state; use Save/Save As with configured backups, stale-source checks and reload
verification. No manager should quietly rewrite unknown fields or partial files.

Nation0 is the player. Diplomacy uses player slot 0 and AI slots 1..8, not the
stored NationNumber as an array suffix. Extra stored nation records are not
necessarily selectable nations. Ship `Id` is permanent; `ShipN` is roster-local.
Air-unit `HomeBase` and `AircraftTypeId`, hull `DesignRefId` and `CommanderId`,
and officer-file division memberships must be considered before changing IDs.

Use existing `busy.py` progress handling, `table_sort.py`, settings and backup
workflow. Keep expensive parsing out of repeated UI row callbacks. Resolve game
and save roots through Settings, never hard-code this user's directory.
Tests should use synthetic fixtures and disposable copies; no proprietary game
assets, live saves or extracted executable data belong in GitHub or end-user ZIPs.

## Milestone 01 — 0.9.5: reliability, tutorials and verified data

### #22 Fix budget calculator

**Sources:** BCS General/Nation/Ships/CoastalArtillery/Submarines/AircraftTypes/
AirUnits; OFF officer counts; saved screenshots and existing budget guides.
**Reuse:** `economy.py`, `economy_gui.py`, tests/test_budget_comparison.py,
BUDGET_CALCULATOR_RESEARCH.md and BUDGET_GAME3_EXPERIMENTS.md.

Inputs already available: General FleetSize/Year/Month, nation BaseResources,
BudgetModifier, ResearchPct, Funds, UnrestLevel, IntelligenceSpending, DockBuilding,
training/current-pending settings, NavalAcademy, PilotTraining and MissileStorage.
Hull and installation records supply Cost, MonthlyCost, Maintenance, InPlay,
Halted, Hurry, Status, Fate, SearchRadarClass and FCRadarClass.

Implemented on develop: provisional income; research from estimated monthly
income; 80 per intelligence level per target; normal/accelerated/halted surface
construction; normal unfinished fortification construction; supported radar and
status maintenance adjustments. Unknown components remain marked unavailable.
A submarine with an explicit MonthlyCost can be included, but ordinary inspected
submarine records do not supply that field. Do not replace missing values with 0.

Latest Game3 verified totals:

| Component | Evidence |
|---|---|
| Ship maintenance | Budget tooltip 3445; all 53 surface rows total 3424; residual 21 belongs here |
| Coastal artillery | Batteries 48 + MTB 220 = 268 |
| Airbases | 19 x 94 + 2 x 80 = 1946 |
| Submarines | Seven completed x 55 = 385 |
| Actual maintenance | 3445 + 268 + 1946 + 385 = 6044 |
| All-active estimate | 6130; separate estimate with wartime caveat, not additive |
| Missile storage | Tooltip 1967; not additive to the above sum; accounting unresolved |
| Naval aircraft | Air-group footer and budget both 18194 |
| Construction | Carriers 1876 + 1883, Battery 39 2400, Ho Hsie 295 = 6454 |
| Extra training | Priorities 1096 + academy 340 = 1436 in baseline |

Completed battery/airbase observations fit round-to-even(Maintenance x .75);
MTB uses full Maintenance. This is measured in Game3, not established universally.
The general inventory found no explicit aircraft/submarine cost keys in their
campaign records. Research percentage arithmetic is supported; the income input
is still provisional. Keep the disclaimer and do not force the balance to look exact.

**Implementation sequence:** add source-aware component breakdowns; implement
only supported recurring infrastructure rules with evidence-labelled scope;
retain unknown submarine/aircraft costs; expand regression cases with the
verified table. Distinguish construction charges from commissioned maintenance.

**Research required, not attempted here:** the 21 ship residual; nation income
and possession effects; submarine construction/maintenance by type/date; aircraft
and elite-pilot costs; academy/training base and delay; missile-storage accounting;
dock expansion and special construction; wartime/repair modifiers; cross-save
scope of the .75 infrastructure factor. Exit requires reconciliation or explicit
remaining estimates, not a hard-coded Game3 total.

### #27 Validate Aircraft and Fortifications Managers

**Sources:** Game6 BCS (all nine nations), installed IDes templates and MapData,
Game3's observed Airbase100/80 and battery costs. **Reuse:** `aircraft.py`,
`aircraft_gui.py`, `aircraft_year_defaults.py`, `fortifications.py`,
`infrastructure_gui.py`, AIRCRAFT.md and FORTIFICATIONS.md.

Aircraft models: `[AircraftTypes] ACTypesNo`, `ATnId/Nation/Purpose/Name/
Manufacturer/Year/BaseModelYear/DevelopmentTime/Obsolete/AvailableAircraft`,
performance and weapon fields listed in the catalog. Air units are separate:
`AirUnitNo`, `AUnId/Nation/AircraftTypeId/HomeBase/AircraftNumber/
DesiredAircraftNumber/Role/Experience/CarrierCapable/NightCapable/Elite`.
Model creation does not create or assign an air unit. Equivalent-year table
selection must not change the campaign design year. Preserve unknown model fields.

Installations: `[NationNCoastalArtillery] CACount`, flattened `Shipn` records.
Supported families include coastal/turreted/missile batteries, MTB, airship and
airbases. Preserve Id and HomeBase links; honor General GameMaxAirbaseSize and
assigned current/desired aircraft capacity. Site names come from stock MapData;
ownership comes from the loaded campaign. New built records and under-construction
records require different defaults. Existing supported new records do not deduct
funds, create squadrons or alter the live game installation.

**Deliverable:** matrix of player/AI, role, equivalent year, installation family,
capacity/site, Save/Save As, backup restore, reload and several-turn results.
Use synthetic tests for ID/counter integrity and copied saves for game checks.
**Research required:** actual multi-turn behavior, unsupported role/technology
combinations, missile/airship costs, cross-nation template costs, and sizes not
represented by measured fixtures. Do not mark validation complete from tests alone.

### #28 Diplomacy research prerequisite

**Sources:** BCS General War/TotalWar/AIWarLength and nation Tension/Allied/
AITensionN/AIAllianceN plus war-related fields in the catalog. Existing
DIPLOMACY.md and the previously supplied diplomacy reference package are prior
evidence; the package was not re-derived or experimentally extended here.
**Supported mapping:** player pair targets the other nation's scalar Tension or
Allied; AI pairs use both reciprocal array fields indexed by save slot.
`diplomacy.py` verifies the nine-nation layout and treats alliance values read-only.
The 0..20 tension limit is an editor guardrail, not a universal engine range.

**Deliverable:** transition specification distinguishing confirmed fields from
unresolved global/reciprocal cleanup. **Research required:** war entry/exit,
coalitions, alliance numeric meanings and duration, peace/treaty aftermath,
multiple concurrent enemies and delayed effects. Raw Tension=50 with War=1 is
only an observed wartime pattern; do not invent a complete war decoder.

### #16 Current-version tutorials

**Sources:** actual current Privateer UI, existing guides, INSTALL.md,
packaging/END_USER_INSTALL.txt, settings.py/settings_gui.py and gui.py.
**Coverage:** first launch, install root, save root (parent of Game1 etc.), backups
and directory, Browse/Reload, validation, Save/Save As, each manager, sorting,
progress windows and staged Apply/Cancel behavior. Settings persist in
%APPDATA%/Privateer/settings.json, with the existing override mechanism.

**Deliverable:** task-based Windows tutorials with an actual screenshot for every
referenced screen/setting and a recovery example. Target released 0.9.8,
including read-only submarine inventory; refresh obsolete descriptions. Existing screenshots and
the Google Doc are prior material, not freshly captured in this audit.
**Research required:** final UI screenshots and user-facing explanations of any
unverified behaviors. No screenshots were synthesized for this task.

### #29 Public-domain asset sourcing

**Available:** installed Flags, Images, Data/Graphics, launcher artwork; these are
reference inventories only. No license-to-redistribute or public-domain status
can be inferred from installation. Custom-mod artwork has the same limitation.
**Deliverable:** asset register with source URL, creator/date, explicit status
evidence, jurisdiction notes, file hash, intended use and conventional edits.
**Research required:** authoritative source selection and rights verification.
No asset sourcing was attempted. No AI-generated images, flags or logos.

## Milestone 02 — 0.10.0: #19 Submarine Manager

**Source:** `[NationNSubmarines]` in every numbered BCS. Exact observed fields:
`SubCount`, `SubnName`, `Availability`, `Accuracy`, `SubType`, `Fate`, `YearBuilt`,
`RemainingBuildTime`, `Halted`, `Sunk`, `Active`, `InPlay`, `LocationAreaName`,
`DestinationAreaName`, `OrderedAreaName`. Not every building record has a current
location. No permanent Id or MonthlyCost/Maintenance field was observed in this
roster family; do not pretend submarine slots are surface-hull identities.

Game3 SubType=3 examples are long-range submarines. Seven ready examples have
RemainingBuildTime=0 and InPlay=1; Ho Hsie has InPlay=0, remaining time 18 and
YearBuilt=0. Historical sunk records retain values in other fields, including
nonzero remaining time: never use remaining time alone to classify active builds.
Blank Fate on live submarines is normal. Sunk/Fate must precede ordinary status.

**Implementation update:** read-only inventory shipped in 0.9.8; see
[Submarine Manager](SUBMARINES.md). Future work may allow narrowly verified
changes with complete batch validation.
Preserve unknown fields and nation ownership container. Reuse parser, staged
editing, backups and stale-source detection; extend the dedicated submarine module
instead of forcing records into surface Ship models requiring Id/design fields.

**Research required:** all SubType labels, meaning/ranges of Availability/Accuracy/
Active, deployment rules, removal/history effects, creation initialization,
SubCount versus Nation SubNumber and global counters, whether external tactical
references use slot/name, and type/date-dependent costs. Gate creation/removal
until linked operations are known. Acceptance: player/AI copied-save reload and
turn progression, historical records intact and exact unrelated-file preservation.

## Milestone 03 — 0.11.0: #21 Wars and alliances

Depends on #28. Reuse `Diplomacy.targets`, unique-field validation and atomic
staging, but add a distinct transition API rather than extending raw tension
entry to unverified ranges. Model before/after reciprocal and global state,
show affected nations before Apply, and preserve unsupported layouts unchanged.
No guessed flag meanings or blanket clearing of war fields.

**Research required:** all transition semantics listed under #28. Available files
identify candidate state, not a sufficient safe write set. Acceptance requires
multi-nation before/after fixtures, stale-save rejection, rollback/no partial
writes and multiple in-game turns. Existing ordinary tension editing remains
separate from this future feature.

## Milestone 04 — 1.0.0: #30 Built-in ship spawning (parent #14)

**Sources:** installed Data/IDes individual .sdf/.tdf designs and other design
folders; saved DesignFilesN.des; BCS NationNShips and NationN counters.
Installed individual design samples are section/key text with Data, Weights,
Armor, Guns, Torpedoes and component sections. Saved .des libraries are a
separate positional v10139 format; copying an .sdf into .des is not a conversion.

**Reuse:** `ship_transfers.py` roster/library helpers and design-copy/remapping,
`save.py` positional design parser, `ship_status.py`, `ships_gui.py` display rows.
A hull needs a fresh permanent Id; DesignRefId points to the destination design
ID; the roster slot and Nation ShipCount must remain contiguous/consistent.
Nation DesignIDCount, library counts/ordinals and General IDNo must be considered.
Never reuse a template hull's logs, commander assignment or battle history.
BuildingNationIdx should reflect the chosen creation policy, not a copied donor
by accident; unlike a transfer, creation has no original physical hull.

**Plan:** inventory and preview designs; validate format/version and dependencies;
convert only supported individual formats; stage design plus hull as one change;
allocate IDs after scanning the relevant shared identity space; define explicit
built/under-construction behavior and costs; verify reload and subsequent turns.
Carrier aircraft/base/division links remain gated unless implemented and tested.

**Research required:** .sdf/.tdf -> positional-library conversion, minimal new-hull
initialization, game-generated counters, linked equipment/design dependencies,
build/crew/commission defaults, and compatibility across nations/eras. Transfer
code proves copying an existing hull works within its constraints; it does NOT
prove fresh spawning works. No spawner was implemented during this audit.

## Milestone 05 — 2.0.0: custom nations and custom designs

### #17 Custom nation builder

Preserve and review `feature/custom-nation-maker` at the SHA above. Its
`custom_nation.py`, `custom_nation_gui.py`, tests/test_custom_nation.py and
branch-only CUSTOM_NATIONS.md already form a prototype; do not rebuild blindly.

**Observed sources:** installed BNat era templates, stock MapData, name/WarInfo
files and flag references; user examples under `C:/Users/Yunda/Documents/Codex/
RTW Nations` (Byzantium, Holy Roman Empire and prior Ottoman reference).
The prototype maps .n00 to BNat1890.dat and .n20 to BNat1920.dat templates;
its documented era compatibility remains subject to release validation.

**Prototype outputs:** Data/<Nation>.n00/.n20, ShipNames.dat/ShipNames20.dat,
Names.txt, WarInfo.dat/WarInfo20.dat, four 60x40 BMP flags, INSTALL.txt and
privateer-nation.json. Names default to CLASS-NUMBER (BB-01, KE-05, CV-30).
Its fields cover identity, leaders/government variants, admiral/unit names,
economy/dock/treaty values, traits, research advantages, gun qualities and flags.
It inherits template possessions and unknown fields. Export is separate from
installing and from changing an existing campaign.

**Implementation:** audit existing validation and Windows path/encoding handling;
retain unknown template fields; validate all referenced resources; define safe
install/uninstall manifests and collisions; require user-supplied or verified
public-domain imagery under the current roadmap. Do not assume prototype
placeholder generation satisfies the later asset policy.

**Research required:** era-specific loading and government flag changes, clean
campaign generation, ownership/geography compatibility, different MapData era
sets, design compatibility, package redistribution rights and custom territories.
New territory requires more than editing a nation name; map coordinates and
battle/site references are unresolved. Do not merge the branch for this audit.

### #31 Custom-design spawning; #14 parent completion

Depends on #30's validated hull creation, staging and ID handling. Accept selected
local custom design files with a readable preview and explicit supported format
versions. Verify referenced parts, nation/era compatibility and design identity.
Never use filename alone as identity or import unknown formats speculatively.

**Research required:** third-party format variants, missing asset behavior,
conversion rules not covered by phase 1, and interoperability with custom nations.
Reuse phase 1 tests plus duplicate import, malformed file, absent component,
foreign-nation, Save As and turn-progression cases. Parent #14 remains open until
both phases pass; do not double-count it as a third implementation project.

## Milestone 06 — 2.0.1: visuals and documentation polish

### #23 Graphics/pictures and #25 Logo

Consume the approved #29 asset register. Integrate with final UI and Windows
packaging only after layout stabilizes. Inspect icon dimensions, scaling,
contrast, image loading, package footprint and missing-file behavior. Installed
historical-looking photos are not automatically public domain. No AI imagery.
**Research required:** approved source assets and provenance. Neither game files
nor this audit supply that missing authorization/evidence.

### #32 Tutorials for new features

Depends on milestones 02-05 and final imagery/layout. Add submarine, diplomacy,
built-in/custom spawning and custom-nation export/install walkthroughs. Each
referenced control needs an actual final-UI screenshot. Include staged changes,
unsupported cases, backups, recovery and in-game verification. **Research required:**
completed feature behavior and current screenshots; do not document proposals as
shipped functionality. This patch version assumes presentation/docs-only scope;
new functionality would require reconsidering the version target.

## Milestone 07 — 3.0.0: #33 AAR Logger

The issue requests easier battle after-action report export; detailed requirements
are still pending. Supabase/Pro is exploratory, not an approved dependency,
paid feature, cloud upload or architecture decision.

**Observed candidate sources:**

- BCS hull NumberOfLogEntries/LogEntryN, Fate, BattleStars and NationNLosses.
- BattleInfo.bbi: BattlePossession, BattleArea, BattleIndex, BattleSize,
  BattleOpponentIndex.
- .sac sections: BattleType, Environment, Locations, Sides/SideN, ForceN,
  DivisionN, SunkShips, Minefields, Reports, AIReports, AirFormations.
- Reports: Side, Course, Delay, MinuteStamp, TimeH/TimeM, Location, class counts,
  Text and OriginatorAsText. These may include sightings, not confirmed outcomes.
- Tactical ship fields include Id/Nation/DesignId, hit counts, damage, sinking,
  survivors, ammunition and weapons state. Meanings and final-state timing remain
  to be validated before presenting them as final losses.
- TLog.log: readable event lines. TTime.log: separate time-like entries.
- Air Combat Log.skv: semicolon header fields include Time, Number Of Attacking
  AC, Role, AircraftType, Home Base, Attack Value, Number Of Defending AC,
  Resistance Value, Destroyed and Damaged. Repeated header names need positional
  or attacker/defender-qualified columns, not a dictionary that loses duplicates.
- AA Log.skv and Bombing Log.skv may be empty or differently shaped. Preserve
  delimiter, missing values and source filename. .sta is positional and undecoded.

**Proposed implementation boundaries:** start with read-only local snapshots,
source manifest/hash, explicit report provenance, missing-data markers and user
export. Use structured normalized battle/event/participant records internally;
select output formats only after owner requirements. Distinguish tactical
observations from confirmed outcomes, and raw reports from narrative summaries.

**Research required:** association of logs to one battle, whether files are
replaced or cumulative, timestamp alignment, campaign-to-tactical identity,
which state is final, duplicate events, player visibility/spoilers, encoding,
export formats, UI workflow, required report fields and any future cloud policy.
No attempt to solve those questions or send game data externally was made.

## Implementation order and completion gates

Follow milestones 01 through 07, keeping the custom-nation prototype isolated.
Within each feature: read-only inventory -> verified mapping -> synthetic
regression fixtures -> staged transaction -> copied-save reload -> in-game
multi-turn evidence -> tutorial update -> release review. Unknown semantics
remain visible/read-only or blocked; do not turn empirical examples into global
constants. No milestones or issues were closed or reordered by this audit.

The accompanying catalog is a field-name and file-family reference, not a license
to edit every field. Raw inventories remain local under outputs/feature-audit;
only this guide, a derived schema catalog and roadmap metadata are suitable for
repository publication. No full game assets or personal save payloads are included.

## Content-research checkpoints

See [FEATURE_RESEARCH_PROGRESS.md](FEATURE_RESEARCH_PROGRESS.md) for manual/page references, newly recovered prior diplomacy evidence, conflicts and the exact resume point. The completed sequence runs through checkpoint 8; later corrections supersede early inventory-only statements. These supplement the inventory above; unknown formulas remain unknown.
