# Numeric budget estimates (development first pass)

Development update, 2026-11-07: income, research, intelligence, academy and
dock expansion now use the supplied formula document where the required inputs
are available. Eight matching saved campaigns reproduced the displayed yearly
budget and research amounts; the other expenditure rules remain estimates.
The player-nation rules have not established the AI-nation differences.

Updated 2026-10-07. The owner requested a value in every calculator field while
awaiting formulas from the RTW3 developer. This supersedes the earlier policy of
showing unavailable costs and withholding monthly balance. It does not establish
that the missing game formulas have been solved.

Open Economy and Unrest Manager. All rows show numbers; total expenses sum the
displayed expense components and estimated balance is monthly income minus that
total. All-active maintenance is a separate reference and is never added again.
The calculator reads saves but does not write projected costs or assumptions.
Funds, resources and unrest edits still require the normal Apply and Save flow.

## Calculation rules and their evidence

| Component | Current estimate | Evidence / limitation |
|---|---|---|
| Annual income | Add possession income, divide by 101, apply minimum budget modifier, fleet size and campaign modifiers, rounding as documented | Matches eight matching screenshots. If game map data cannot be matched, falls back to the earlier estimate; UI labels those rows as fallback. |
| Monthly income | Annual estimate / 12, nearest even | Matches the supplied examples. |
| Research | Round annual budget × ResearchPct / 100, add HFR bonus if applicable, then divide by 12 and round | Matches eight matching screenshots; HFR bonus needs further validation. |
| Surface maintenance | Saved Maintenance plus class-2 radar adjustment (DD +2, CL/CV +4); AF full, RF half, MB fifth, nearest-even | Measured examples; other equipment, officers, age, repair and war effects unresolved. Historical/museum hulls excluded. |
| Battery/airbase maintenance | Saved Maintenance × 0.75, nearest-even | Game3 fit, generalized as a reference assumption. MTB uses full saved value. Other installation families use the same provisional factor. |
| Submarine maintenance | Saved Maintenance if supplied; otherwise 55 per live completed boat | 55 is the observed Game3 long-range cost. Applying it to other types/eras is a fallback, not a discovery. Sunk/history excluded. |
| Surface construction | MonthlyCost; accelerated ×1.15 with half-up rounding; halted floor(Maintenance / 2) takes precedence | Controlled comparisons. Monthly premium is not a claim about total build-cost premium. |
| Installation construction | Saved MonthlyCost for unfinished live records | Completed records excluded even if MonthlyCost remains positive. |
| Submarine construction | Saved MonthlyCost if supplied; otherwise 295 per unfinished live boat | Game3 Ho Hsie reference; generalized as a reference fallback. |
| Special sub/installation construction | Surface halt/hurry rules borrowed provisionally | Unverified beyond surface ships. Missing halted maintenance uses submarine fallback or zero for installations. |
| Dock expansion | Fleet-size base adjusted by dock size and industry | Supplied rule reproduces Game8's 324; other cases need validation. |
| Naval aircraft | Explicit saved spending if supplied; otherwise assigned aircraft × (18,194 / 1,956) | Blended Game3 average, approximately 9.301636. No role/era/elite-pilot or carrier-readiness correction. Includes sentinel-model units by aircraft count. |
| Extra training | Explicit saved spending if supplied; otherwise surface maintenance × 0.8 × combined priority percentage, plus academy | Percentages: gunnery 30%, night/torpedo/damage control 20% each. The 0.8 base factor fits Game3, not universally verified. Uses current flags, not pending flags. |
| Academy | Annual budget / 95, truncated; divide by 12, round, then round down to multiple of 10 | Reproduces Game3's 340 and Game8's 10; broader validation pending. |
| Player intelligence | 10 × fleet size × sum of target spending levels 0–3 | Reproduces Game8's 60 and Game9's 1,920. The previously observed 80 per level applies to fleet size 8. AI intelligence is unresolved. |

Aircraft pools are displayed in the explanation but not separately priced: the
reference average already comes from a total bill whose composition is unknown.
It can underestimate costs when there are few/no assigned aircraft but pools or
production exist. Missile storage is not added separately: the Game3 tooltip's
other four maintenance categories already sum to the displayed maintenance total.
The unexplained 21 difference between ship rows and aggregate ship maintenance
is not patched with a fixed surcharge.

Unavailable income inputs, invalid/unknown intelligence, missing rosters and
installation charges lacking a saved value use a disclosed zero fallback.
A numeric zero in these cases is not a confirmed absence of expense. Every result
retains the incomplete/estimated flag even when an example happens to match.

## Built-in assumptions and interface

Privateer 0.9.9 removes the bottom disclaimer, scrollable calculation notes,
and **Estimate assumptions…** button and dialog. The calculator uses the same
built-in default rates and formulas; this interface cleanup does not change
estimated totals or the ±10% balance range. Estimated/provisional row labels remain.
Only Funds, Base resources and Unrest level are editable campaign values here.

The backend still accepts explicit assumptions for research and automated checks,
but users cannot change these rates in the manager. The rules and limitations in
this guide document the fallbacks previously explained inside the window.
Published 0.9.8 still contains the older assumption controls and information panel.

This first pass does not yet implement the supplied age, officer, aircraft,
submarine, full training, or invasion formulas. Those expense fallbacks remain;
issue #22 stays open until the full calculation has been implemented and checked.

Historical measurements remain in [Game3 experiments](BUDGET_GAME3_EXPERIMENTS.md)
and the [0.9.4 comparison](BUDGET_CALCULATOR_RESEARCH.md); those documents' earlier
implementation-status statements do not describe this numeric-estimate mode.

The monthly balance also shows a planning range of balance minus/plus 10% of
its absolute value, displayed to one decimal place. Negative balances retain
ordered lower/upper bounds; zero gives 0.0 to 0.0. This is a chosen planning
allowance, not a measured confidence interval or a change to income/expenses.

