# Numeric budget estimates (development calculator)

Development update, 2026-11-07: income, research, intelligence, academy and
dock expansion now use the supplied formula document where the required inputs
are available. Eight matching saved campaigns reproduced the displayed yearly
budget and research amounts. A second pass implements aircraft, in-service
submarine costs, unhalted submarine construction, base expansion, invasion,
and the peacetime maintenance era adjustment. Expense totals remain estimates.
The player-nation rules have not established the AI-nation differences.

Development update, 2026-11-10: a third pass adds player surface-ship and
installation maintenance, all-active maintenance, and current/pending training.
Eight available player budget comparisons now match every displayed component.
Keep all rows provisional while untested cases and save/screenshot alignment
are investigated; this is not independent proof of the supplied formulas.

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
| Surface maintenance | Apply officer, repair, age, radar, status, location and applicable peace-era rules | Matches available player screenshots. KE date encoding is inferred and uncertain near the boundary; missing map or officer data uses the earlier estimate. |
| Battery/airbase maintenance | Apply installation repair, location and status rules; include airship bases as airbases for the foreign-area multiplier | Game3 and Game9 match, including the four foreign airship bases responsible for the earlier 36 difference. |
| All-active maintenance | Apply the all-active calculation to surface ships and ordinary maintenance to installations and submarines | Matches available displayed reference figures; wartime behavior remains unverified. |
| Maintenance era adjustment | Apply peacetime multiplier based on year and government to the maintenance subtotal | Supplied rule; Game8 total now matches. Other maintenance components remain estimated. |
| Submarine maintenance | Type-based rate with year and war modifiers | Supplied rule; unknown types or missing years use a fallback. Broader validation pending. |
| Surface construction | MonthlyCost; accelerated ×1.15 with half-up rounding; halted floor(Maintenance / 2) takes precedence | Controlled comparisons. Monthly premium is not a claim about total build-cost premium. |
| Installation construction | Saved MonthlyCost for unfinished live records | Completed records excluded even if MonthlyCost remains positive. |
| Submarine construction | Type-based rate with year and industry modifiers | Supplied rule for active construction; unknown types use a fallback. Halted construction remains provisional. |
| Special sub/installation construction | Halted entries use a provisional half-maintenance fallback; hurried installations use 1.15 | These cases still need the supplied rules implemented and validated. |
| Dock expansion | Fleet-size base adjusted by dock size and industry | Supplied rule reproduces Game8's 324; other cases need validation. |
| Base expansion | (FleetSize + 1) × 100, or × 150 for base value ≥ 20, per owned expansion | Supplied rule; more in-game examples needed. |
| Naval aircraft | Role-based air-unit rates and modifiers, plus ship aircraft and airship sheds | Matches available aircraft screenshots for Games 1–6, 8 and 9. Unknown role, base or year uses the earlier blended fallback. |
| Extra training | Eligible ship maintenance × priority points × rate, plus academy | Current or pending priorities count once; excludes repairs and statuses 7 and 9. Matches available player screenshots. War and surprise attack cases need validation. |
| Academy | Annual budget / 95, truncated; divide by 12, round, then round down to multiple of 10 | Reproduces Game3's 340 and Game8's 10; broader validation pending. |
| Player intelligence | 10 × fleet size × sum of target spending levels 0–3 | Reproduces Game8's 60 and Game9's 1,920. The previously observed 80 per level applies to fleet size 8. AI intelligence is unresolved. |
| Invasion | Yearly budget ÷ 300, truncated, plus 100 when a target is active | Supplied rule; not yet checked against an active invasion screenshot. |

When the aircraft formula cannot resolve required data, a blended reference
average is used instead. Aircraft pools are not separately priced. Missile
storage is not added separately: the Game3 tooltip's
other four maintenance categories already sum to the displayed maintenance total.
The previous Game3 difference of 21 was accounted for by the calculated ship
maintenance and training eligibility rules, without a fixed surcharge.

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

Halted ship, submarine and installation construction remains provisional.
The inferred KE date encoding, officer effects, war and surprise attack cases,
and AI-nation differences need additional validation. Issue #22 stays open until
the remaining rules have been implemented and checked.

Historical measurements remain in [Game3 experiments](BUDGET_GAME3_EXPERIMENTS.md)
and the [0.9.4 comparison](BUDGET_CALCULATOR_RESEARCH.md); those documents' earlier
implementation-status statements do not describe this numeric-estimate mode.

The monthly balance also shows a planning range of balance minus/plus 10% of
its absolute value, displayed to one decimal place. Negative balances retain
ordered lower/upper bounds; zero gives 0.0 to 0.0. This is a chosen planning
allowance, not a measured confidence interval or a change to income/expenses.

