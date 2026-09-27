# Feature research progress and resume point

Checkpoint 1: 2026-09-26. Read-only content research; no game edits or new
experiments. This document supplements FEATURE_IMPLEMENTATION_GUIDE.md and
records source-specific discoveries rather than silently overriding earlier evidence.

## Reading order and current position

1. Installed manuals, FAQ and release history: relevant prose sections reviewed;
   graphical tables and remaining pages still pending detailed review.
2. User reference guides: diplomacy final findings and verified add-enemy procedure
   reviewed. Remaining package JSON/base-tension references and ship guide pending.
3. Self-describing installed data: next priority after remaining guides.
4. Campaign and tactical structured records: inventoried; targeted semantic review pending.
5. Positional/opaque formats: last; no executable analysis initiated.

PDF text was extracted locally from all six installed PDFs (248 pages total).
Extraction is indexing, NOT evidence that every page was read. Raw extracted text
stays outside the repository in outputs/feature-audit/manuals. Page numbers below
are one-based PDF pages; for the main manual these match visible page numbers.

### Sources and reviewed ranges

- Manuals/Rule the Waves 3 Manual Patch 2026.pdf (149 pages): contents/key-topic
  search, full prose on pp.12-13,31,34-35,51-56,63,65-66,106-114,126,145.
- Manuals/Rule the Waves Expanded Battles Manual EBOOK.pdf (40 pages):
  pp.13-19 and 34-35 relevant text; no complete visual-table verification yet.
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

## Next resume point

Read the remaining high-value user references (base/wartime tension documents,
JSON evidence and ship storage/transfer guide), then inspect self-describing
nation, research, map and design template contents. Finish the manual sections
covering AAR/battle results and graphical technology tables as needed. Keep a
source/page or filename/field citation per finding, preserve conflicts, and add
another checkpoint before moving into positional formats. Do not re-extract all
PDFs or repeat the completed inventory.
