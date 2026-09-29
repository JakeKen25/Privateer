# Numeric budget estimates (local version 0.9.6)

Updated 2026-09-29. The owner requested a value in every calculator field while
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
| Annual income | BaseResources × BudgetModifier × FleetSize / 10 × income adjustment | Provisional domestic-income approximation; possessions and other adjustments unresolved. Default adjustment 1. |
| Monthly income | Annual estimate / 12, nearest integer | Display relationship observed in nine screenshots; exact engine tie behavior unknown. |
| Research | Monthly estimate × ResearchPct / 100, nearest integer | Observed relationship, but inherits income errors. |
| Surface maintenance | Saved Maintenance plus class-2 radar adjustment (DD +2, CL/CV +4); AF full, RF half, MB fifth, nearest-even | Measured examples; other equipment, officers, age, repair and war effects unresolved. Historical/museum hulls excluded. |
| Battery/airbase maintenance | Saved Maintenance × 0.75, nearest-even | Game3 fit, generalized as an adjustable assumption. MTB uses full saved value. Other installation families use the same provisional factor. |
| Submarine maintenance | Saved Maintenance if supplied; otherwise 55 per live completed boat | 55 is the observed Game3 long-range cost. Applying it to other types/eras is a fallback, not a discovery. Sunk/history excluded. |
| Surface construction | MonthlyCost; accelerated ×1.15 with half-up rounding; halted floor(Maintenance / 2) takes precedence | Controlled comparisons. Monthly premium is not a claim about total build-cost premium. |
| Installation construction | Saved MonthlyCost for unfinished live records | Completed records excluded even if MonthlyCost remains positive. |
| Submarine construction | Saved MonthlyCost if supplied; otherwise 295 per unfinished live boat | Game3 Ho Hsie reference; generalized as an adjustable fallback. |
| Special sub/installation construction | Surface halt/hurry rules borrowed provisionally | Unverified beyond surface ships. Missing halted maintenance uses submarine fallback or zero for installations. |
| Dock expansion | 324 monthly while DockBuilding > 0 | Unresolved Game8 charge used as an adjustable reference amount, not an engine formula. |
| Naval aircraft | Explicit saved spending if supplied; otherwise assigned aircraft × (18,194 / 1,956) | Blended Game3 average, approximately 9.301636. No role/era/elite-pilot or carrier-readiness correction. Includes sentinel-model units by aircraft count. |
| Extra training | Explicit saved spending if supplied; otherwise surface maintenance × 0.8 × combined priority percentage, plus academy | Percentages: gunnery 30%, night/torpedo/damage control 20% each. The 0.8 base factor fits Game3, not universally verified. Uses current flags, not pending flags. |
| Academy | 340 when NavalAcademy is enabled | Game3 observed amount; adjustable reference, not a derived formula. |
| Player intelligence | 80 × sum of valid target spending levels 0–3 | User-confirmed universal rate; no fleet-size multiplier. AI-owned budgets cannot be inferred from these fields. |

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

## Adjusting assumptions

Choose **Estimate assumptions…** to change the aircraft rate, submarine costs,
infrastructure/training factors, academy, dock expansion or income adjustment.
Defaults restores the reference values; Use estimates recalculates all affected
rows together. Entries must be finite, nonnegative numbers. These choices last
only while this calculator window remains open, and never alter game records.
The scrollable explanation identifies formulas, fallbacks and remaining gaps.

This implementation adds no general age, officer, missile, aircraft-development,
pilot-training or possession formula. Replace the fallbacks when developer
information or controlled evidence becomes available. Issue #22 remains open.

Historical measurements remain in [Game3 experiments](BUDGET_GAME3_EXPERIMENTS.md)
and the [0.9.4 comparison](BUDGET_CALCULATOR_RESEARCH.md); those documents' earlier
implementation-status statements do not describe this numeric-estimate mode.
