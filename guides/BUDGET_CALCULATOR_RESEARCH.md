# Budget calculator comparison: Games 1–9

Research date: 2026-09-22. Related issue: [#22](https://github.com/JakeKen25/Privateer/issues/22).

This is a read-only investigation of the 0.9.4 calculator, not a formula replacement.
No save, executable, or application code was changed. Source baseline: `a9937c364a3cda9439171e30d7662c61eaaa4064`.

## Evidence and alignment

The supplied `Calculator/Game1.png` through `Game9.png` were visually transcribed and
compared with the corresponding numbered BCS files and MapData files. Screenshots
are in the user's `Documents/Codex/RTW Screenshots/Calculator` folder; saves are in
`Documents/My Games/Rule the Waves 3/Save`.

Nation0's nation, year/month, funds, and research percentage agree in every pair.
That supports comparison but does not prove that every setting was unchanged between
the save and screenshot. No game turn or controlled experiment was run.

| Game | Player nation | Date |
|---|---|---|
| 1 | Germany | January 1920 |
| 2 | China | June 1907 |
| 3 | China | December 1945 |
| 4 | Soviet Union | January 1935 |
| 5 | Austria-Hungary | January 1900 |
| 6 | USA | October 1971 |
| 7 | USA | December 1970 |
| 8 | Spain | January 1935 |
| 9 | China | December 1926 |

The companion [JSON observations](../developmentResources/budget-calculator/games-1-9-comparison.json)
retain all displayed values (including both maintenance boxes), backend projections,
selected inputs, aggregate record counts, and SHA-256 hashes of each input file.
They do not contain full game saves or installed game data.

## In-game figures versus current Privateer results

Each cell is **in-game / Privateer 0.9.4**. Maintenance means the left-hand amount
included in total expenses. The second maintenance box is recorded separately in JSON.

### Income and balance

| Game | Annual budget | Monthly budget | Expenses | Balance |
|---|---:|---:|---:|---:|
| 1 | 86,240 / 86,400 | 7,187 / 7,200 | 3,428 / 3,659 | 3,759 / 3,541 |
| 2 | 49,390 / 18,996 | 4,116 / 1,583 | 49,305 / 51,075 | -45,189 / -49,492 |
| 3 | 395,520 / 72,384 | 32,960 / 6,032 | 33,388 / 23,497 | -428 / -17,465 |
| 4 | 160,480 / 60,000 | 13,373 / 5,000 | 15,057 / 12,862 | -1,684 / -7,862 |
| 5 | 72,000 / 24,000 | 6,000 / 2,000 | 5,327 / 4,977 | 673 / -2,977 |
| 6 | 1,949,230 / 335,292 | 162,436 / 27,941 | 147,045 / 126,701 | 15,391 / -98,760 |
| 7 | 1,930,070 / 331,980 | 160,839 / 27,665 | 144,260 / 122,330 | 16,579 / -94,665 |
| 8 | 14,520 / 16,800 | 1,210 / 1,400 | 1,288 / 443 | -78 / 957 |
| 9 | 310,720 / 61,788 | 25,893 / 5,149 | 24,596 / 37,934 | 1,297 / -32,785 |

### Expense components

| Game | Maintenance | Construction | Aircraft | Research | Training | Intelligence |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 2,566 / 2,795 | 0 / 0 | 0 / 0 | 862 / 864 | 0 / 0 | 0 / 0 |
| 2 | 8,529 / 15,878 | 37,661 / 35,039 | 0 / 0 | 412 / 158 | 2,703 / 0 | 0 / 0 |
| 3 | 6,044 / 19,014 | 3,759 / 3,759 | 18,194 / 0 | 3,955 / 724 | 1,436 / 0 | 0 / 0 |
| 4 | 5,583 / 4,889 | 7,573 / 7,573 | 831 / 0 | 1,070 / 400 | 0 / 0 | 0 / 0 |
| 5 | 1,603 / 1,573 | 3,244 / 3,244 | 0 / 0 | 480 / 160 | 0 / 0 | 0 / 0 |
| 6 | 41,030 / 97,369 | 31,921 / 26,538 | 47,428 / 0 | 16,244 / 2,794 | 10,422 / 0 | 0 / 0 |
| 7 | 38,663 / 97,369 | 25,522 / 22,194 | 47,188 / 0 | 16,084 / 2,767 | 16,803 / 0 | 0 / 0 |
| 8 | 593 / 387 | 324 / 0 | 253 / 0 | 48 / 56 | 10 / 0 | 60 / 0 |
| 9 | 12,087 / 17,618 | 4,026 / 20,316 | 2,080 / 0 | 0 / 0 | 4,483 / 0 | 1,920 / 0 |

## Findings supported by these samples

### Income is not a universal BaseResources × 2.4

The current function rounds BaseResources / 5 to monthly income and multiplies that
by 12 for annual income. This is incorrect for all nine annual budgets. For example,
Game5's BaseResources=10,000 produces 24,000 in Privateer versus 72,000 in game.
Game6 produces 335,292 versus 1,949,230.

The function does not use BudgetModifier, General.FleetSize, or possessions. These
inputs vary between the samples. The installed manual explains that naval spending
share and possessions affect income, that colonial income changes with time, and
that fleet size changes the budget. The exact combined formula remains unverified.
Do not replace one fixed multiplier with another fitted multiplier.

As an exploratory check, BaseResources × BudgetModifier × FleetSize / 10 gives the
exact Game5 annual budget and is much closer for several other saves, but does NOT
match the other eight. It is not a verified replacement formula.

In all nine screenshots, rounding annual budget / 12 to the nearest integer reproduces
the displayed monthly budget. Deriving annual income from rounded monthly income
loses information (Game1: 7,187 × 12 = 86,244, not 86,240).

### Research calculation is consistent once income is correct

Nearest-integer rounding of displayed monthly income × ResearchPct / 100 reproduces
all nine research amounts. The current research mismatches arise from wrong income
in these samples; none of the observations tests an exact half-integer rounding tie.
Funds are read correctly in all nine.

### Historical records inflate ship maintenance

`project_budget()` adds Maintenance for every ship that is not marked under
construction, without excluding final fates or museums. The roster still contains
historical hull records. In Game6, 74,431 of Privateer's 97,369 maintenance total comes
from records with final fates; the remaining live, commissioned surface ships have
22,938 in raw Maintenance fields. Neither total equals the actual 41,030 expense.

Status also matters. Game1's reference maintenance is 2,955 and actual is 2,566, a
difference of 389. That difference is reproduced by reducing Barfleur's stored 349
to floor(349 / 2)=174 and Benbow's 267 to floor(267 / 5)=53. This is a useful status
test case, not a complete maintenance formula.

The calculator ignores coastal installations and submarines entirely. Simply adding
all their stored values is not sufficient: in Game5, surface Maintenance sums to
1,573 and the six coastal Maintenance fields sum to 64, whereas the actual total is
1,603. Summing floor(Maintenance / 2) for those six batteries supplies exactly 30.
That single-case fit does not establish costs for airbases, missiles, or all nations.

The manual describes the extra maintenance display as an all-active-fleet prediction;
it is not an additional expense to sum. Current maintenance can exceed that reference
(Games4,6,7,9). Officer effects, repairs, working-up/foreign-service states, equipment,
submarine types, fortifications, and wartime behavior still need controlled checks.

### Construction: seven complete matches from surface-ship rules

Using only ships with a live fate and InPlay=0:

- Normal construction: MonthlyCost.
- Hurry=1: round(MonthlyCost × 1.15), separately for each ship.
- Halted=1: floor(Maintenance / 2), instead of MonthlyCost; give halted precedence.

This candidate calculation matches the full construction line for Games1,2,3,4,5,7,9.
The 15% is an observed monthly-charge adjustment, not a claim of 15% higher total
build cost. The manual describes faster construction with a separate total-cost premium.
The manual's description of halted costs refers to mothballed maintenance, so the
observed raw-field relationship should be tested before generalizing.

| Game | Candidate surface construction | In-game | Unexplained |
|---|---:|---:|---:|
| 1 | 0 | 0 | 0 |
| 2 | 37,661 | 37,661 | 0 |
| 3 | 3,759 | 3,759 | 0 |
| 4 | 7,573 | 7,573 | 0 |
| 5 | 3,244 | 3,244 | 0 |
| 6 | 29,866 | 31,921 | 2,055 |
| 7 | 25,522 | 25,522 | 0 |
| 8 | 0 | 324 | 324 |
| 9 | 4,026 | 4,026 | 0 |

Game2 has three hurried hulls: correcting their charges adds 2,622 to 35,039, giving
37,661. Game7's six hurried hulls add 3,328 to 22,194, giving 25,522.
Game9 has eight halted hulls: normal active construction costs 2,452 and halted hulls
contribute 1,574, giving 4,026 instead of Privateer's 20,316.

Game6 also has six submarines under construction. Its remaining 2,055 is a candidate
submarine-building expense, not yet independently verified by type. Game8 has no
surface ship construction and DockBuilding=15; its 324 construction charge is a
candidate dock-expansion cost. Neither category exists in the current calculator.
Construction delays, base expansion and fortification construction need more cases.

### Intelligence is stored on target nations

The player Nation0.IntelligenceSpending is zero in all nine saves, including the two
screenshots with spending. Game8 instead has Nation2.IntelligenceSpending=3 and
FleetSize=2, with 60 in-game spending. Game9 has level 3 on each of the eight other
nations and FleetSize=8, with 1,920 spending. A level-3 target charge of 30 × FleetSize
fits both: 1 × 30 × 2 = 60 and 8 × 30 × 8 = 1,920.

Costs for levels 1 and 2 remain unverified; do not assume linear scaling from these
level-3 samples. IntelEffort can differ from IntelligenceSpending, so they must not be
treated as interchangeable. Opponent-owned intelligence budgets cannot be inferred
from this player-target data.

### Aircraft and training are currently missing, not genuinely zero

None of the nine player records contains the optional NavalAircraftSpending,
AircraftSpending, ExtraTrainingSpending or TrainingSpending fields that Privateer
looks for. The code consequently returns zero for both categories in every save.

Aircraft expenses are nonzero in Games3,4,6,7,8,9. Game9 has no Nation0 air units but
still shows 2,080, so summing deployed unit aircraft alone cannot explain the line.
Aircraft pools, production/development, and their ongoing costs need investigation.

Training selections exist as GunneryTraining, NightFighting, TorpedoWarfare,
DamageControl, PilotTraining and pending-training fields. Game7 has a training
transition in progress; current and pending choices differ. The manual describes
percentage-based special-training expenses, but the correct cost base and transitional
behavior are not established by these snapshots. Game8 also shows 10 training expense
with the inspected player training flags zero. Do not hard-code zero or fit a formula
that only accounts for the large-fleet examples.

## Next implementation and verification sequence

1. Preserve these nine observed outputs as acceptance references. Separate unknown
   components from verified zero values in the eventual UI.
2. Verify income through controlled changes to BaseResources, BudgetModifier,
   FleetSize and one possession at a time, keeping original saves untouched.
3. Implement historical-hull exclusion and the verified construction cases with
   small synthetic fixtures; add submarine/dock/fortification costs after confirming
   their formulas. Keep maintenance and training work separate from construction.
4. Confirm intelligence levels 1 and 2, aircraft pools/production expenses, training
   changes, maintenance statuses, and both maintenance boxes using in-game checks.
5. Compare every displayed component, total, and balance against all nine references,
   then test another campaign. Retain the estimates disclaimer until unresolved costs
   are either explained or explicitly represented as unknown.

This investigation does not close issue #22. None of the candidate rules above has
been shipped to users.

## Sources and checks

- User-supplied Game1–Game9 screenshots and corresponding local BCS/MapData files.
- `privateer/economy.py`, `privateer/save.py`, and `privateer/ship_status.py` at the
  stated baseline. Backend projections use the existing parser/model and calculator;
  design files are unnecessary for that calculation and were not loaded.
- Installed `Manuals/Rule the Waves 3 Manual Patch 2026.pdf`: pages12–13 (economy),
  18 (fleet size), 31 (construction), 51–53 (maintenance/training), 63 (intelligence).
  Manual text is contextual evidence, not proof of exact engine rounding or field mappings.
- All nine screenshot expense sums, balances, monthly income rounding, research
  calculations and saved funds/research percentages were checked programmatically.
- No raw saves, manual copies, or screenshots are included in the repository.
