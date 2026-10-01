# Possession values and annual budget: 2026-09-30

Read-only comparison of the current numbered BCS and matching MapData files in
nine save slots against the recorded budget screenshots. No formula, save or
release was changed. This extends the [original comparison](BUDGET_CALCULATOR_RESEARCH.md).

## Source fields and alignment

MapDataX.dat, [MapAreas]: MapAreaAPossessionBOwner, Name, Value, Oil and BaseValue.
Ownership was matched to the player Nation0 Name in RTWGameX.bcs. Income inputs
are Nation0 BaseResources and BudgetModifier, and General FleetSize. BuildAreaName
was used only for a geographical comparison, not to identify economic colonies.

All eight usable cases retain the original screenshot's nation, year/month,
BaseResources, BudgetModifier and FleetSize. Their map-file SHA-256 values match
the original comparison dataset exactly. This does not prove every other budget
modifier was unchanged; BCS files have been used for intervening experiments.

Game7 no longer matches: it is now Great Britain, January 1900; the recorded
screenshot was USA, December 1970. Its map hash differs. It is excluded from
budget-fit conclusions. Its current owned Value total is 415, of which 215 comes
from entries below 200. A matching new budget screenshot is needed to use it.

## Results

The gap is screenshot annual budget minus the unrounded candidate
BaseResources × BudgetModifier × FleetSize / 10. Using the unrounded candidate
keeps integer rounding separate from the substantive discrepancy.

| Save | Nation / year | All owned Value | Owned Value below 200 | Candidate annual budget | Screenshot annual budget | Gap |
|---|---|---:|---:|---:|---:|---:|
| 1 | Germany / 1920 | 412 | 12 | 86,400 | 86,240 | -160 |
| 2 | China / 1907 | 430 | 30 | 50,649.6 | 49,390 | -1,259.6 |
| 3 | China / 1945 | 442 | 42 | 386,073.6 | 395,520 | +9,446.4 |
| 4 | Soviet Union / 1935 | 417 | 17 | 160,000 | 160,480 | +480 |
| 5 | Austria-Hungary / 1900 | 204 | 4 | 72,000 | 72,000 | 0 |
| 6 | USA / 1971 | 878 | 78 | 2,011,780.8 | 1,949,230 | -62,550.8 |
| 8 | Spain / 1935 | 400 | 0 | 14,000 | 14,520 | +520 |
| 9 | China / 1926 | 493 | 93 | 288,332.8 | 310,720 | +22,387.2 |

The below-200 column is an exploratory grouping, NOT a verified colony flag.
Value=200 occurs on major mainland possessions. Smaller entries include domestic
territories too, such as Dalmatia and East Prussia. Neither this cutoff nor being
outside BuildAreaName reliably identifies which possessions the engine charges.
For example, Southern China, Eastern Germany and Eastern Spain are outside their
nation's saved home sea area. USA mainland possessions span multiple sea areas.

Game3's full Value sum comprises Northern China 200, Southern China 200, Sumatra 5,
Formosa 5, Cochin China 5, Hainan 4, Kiautschou Bay 2, Liaotung Peninsula 5,
Northern Korea 5, Southern Korea 6 and Shanghai 5. The nine smaller entries sum
to 42. BaseValue is a separate naval-base field; it was not substituted for Value.
Oil ownership was also inspected but no income multiplier was inferred from it.

## What the evidence supports

The installed Rule the Waves 3 Manual Patch 2026, printed/PDF page 13, explicitly
states that controlled colonies/possessions add to budget, that possession value
is used when calculating acquisition/loss budget effects, and that colonial income
declines over time. Page 12 separately describes base resources and naval spending
share. These establish relevance, not an exact formula or implementation order.

A single positive additive constant times all owned Value, the below-200 sum,
or the outside-home-area sum cannot explain all eight residuals: several gaps are
negative. The same contradiction applies if that positive addition is inserted
before the positive budget/fleet multipliers. Spain additionally has zero in the
below-200 grouping but a positive 520 gap. Austria-Hungary has four but no gap.

For China alone, the gap per below-200 value is about 240.72 in 1926 and 224.91
in 1945, directionally consistent with declining colonial income. This is not
independent proof: resources, budget modifiers, possessions and campaign state
also differ. The 1907 Chinese case has a negative gap. No universal coefficient,
year-decay function or home-territory exclusion rule is established.

Conclusion: possessions are a documented budget input missing from Privateer's
current formula, but they do not establish that its domestic-income calculation
is otherwise correct. Do not absorb every residual into a fitted colonial rate.

## Next targeted comparison

On disposable copies of the same Game3 state, compare the displayed yearly budget
before and after changing one non-home possession's Value by a known amount,
keeping owner, date, BaseResources, BudgetModifier and FleetSize unchanged. Use
identical game loading/refresh steps for both copies; record whether the display
recalculates immediately. Do not advance only one copy and confound growth/events.
Then separately test owner changes and another year to identify applicability and
time scaling. These are proposed experiments, not tests performed in this audit.
