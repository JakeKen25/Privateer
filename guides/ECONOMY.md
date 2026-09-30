# Economy and infrastructure managers

**Current calculator: local/development 0.9.8.** Every budget row displays
a numeric estimate. [Budget estimates](BUDGET_ESTIMATES.md) defines the current
rules and adjustable reference costs.

Right-click a nation and choose **Economy and Unrest Manager** to edit Funds, Base Resources, and Unrest Level
in one window. Each value retains the existing Set value, Adjust by amount, and
Adjust by percentage operations. Blank rows remain unchanged, and Apply stages all
validated edits as one transaction.

The lower panel is a read-only planning calculator. Its original 2.4 annual
BaseResources multiplier came from one early Game1 example and is not a general
RTW3 budget formula. The [Games 1-9 comparison](BUDGET_CALCULATOR_RESEARCH.md)
documents the current discrepancies and supersedes that original assumption.

The development calculator now excludes ships with final fates and museum ships,
applies reserve/mothball reductions, and accounts for hurried and halted surface
construction. Player intelligence costs use target-nation records for the observed
levels 0–3 at 80 per level per target. AI-nation intelligence uses a disclosed
zero fallback because player-target fields do not describe AI-owned spending.

Provisional domestic income uses BaseResources × BudgetModifier × FleetSize / 10,
then derives monthly income and research with rounding. This is an explicitly
incomplete estimate: possession income and other engine adjustments remain
unverified. The comparison report records where this estimate differs from RTW3.

Aircraft, training, academy, submarine and dock costs use reference estimates
when saved costs are absent. Recurring installations use the observed Game3 factor
provisionally. **Total expenses (estimated)** sums expense rows; **Monthly balance
(estimated)** subtracts that total from estimated income. All-active maintenance
is displayed separately and is not added to expenses. Choose **Estimate
assumptions…** to adjust fallback rates for this window. The scrollable explanation
discloses missing-data zero fallbacks and unresolved modifiers. No projected
expense, income or assumption fields are written to the save.

The warning is always visible, including during input validation:
**Estimated budget: every amount is numeric, but unresolved formulas use the
assumptions below. Total expenses and balance are estimates, not verified game costs.**

Choose **Infrastructure and Fortifications Manager** to edit the selected nation's existing `DockSize`
field. This controls the maximum displacement that can be built in that nation's
dockyards. See [Fortifications](FORTIFICATIONS.md) for the fortification editor.

Ship Spawner remains a WIP context-menu placeholder. **Admiral Manager** appears only
for Nation0, which RTW3 always uses as the player nation, and edits the stored
`AdmiralName` and `Prestige` fields.
All edits remain in memory until Save or Save As is selected in the main window.
