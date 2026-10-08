# Economy and infrastructure managers

**Current interface: 0.9.9.** Every budget row displays
a numeric estimate. [Budget estimates](BUDGET_ESTIMATES.md) defines the current
rules and built-in reference costs. Published 0.9.8 retains the older information
panel and assumption controls; the 0.9.9 interface removes both.

Right-click a nation and choose **Economy and Unrest Manager** to edit Funds, Base Resources, and Unrest Level
in one window. Each value retains the existing Set value, Adjust by amount, and
Adjust by percentage operations. Blank rows remain unchanged, and Apply stages all
validated edits as one transaction.

The lower panel is a read-only planning calculator. Its original 2.4 annual
BaseResources multiplier came from one early Game1 example and is not a general
RTW3 budget formula. The [Games 1-9 comparison](BUDGET_CALCULATOR_RESEARCH.md)
documents the current discrepancies and supersedes that original assumption.

The calculator excludes ships with final fates and museum ships,
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
is displayed separately and is not added to expenses. The calculator uses its
built-in default rates; there is no assumption editor. The bottom disclaimer and
scrollable calculation notes have been removed. Estimated/provisional labels and
the ±10% monthly-balance planning range remain. Invalid input still displays an
actionable error; the message disappears when the input is corrected.

No projected expense, income or assumption fields are written to the save.
Calculations remain provisional. Consult [Budget estimates](BUDGET_ESTIMATES.md)
for missing-data zero fallbacks and unresolved modifiers; a numeric zero does not
necessarily establish that no cost exists.

Choose **Infrastructure and Fortifications Manager** to edit the selected nation's existing `DockSize`
field. This controls the maximum displacement that can be built in that nation's
dockyards. See [Fortifications](FORTIFICATIONS.md) for the fortification editor.

Ship Spawner remains a WIP context-menu placeholder. **Admiral Manager** appears only
for Nation0, which RTW3 always uses as the player nation, and edits the stored
`AdmiralName` and `Prestige` fields.
All edits remain in memory until Save or Save As is selected in the main window.
