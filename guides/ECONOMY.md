# Economy and infrastructure managers

Right-click a nation and choose **Economy and Unrest Manager** to edit Funds, Base Resources, and Unrest Level
in one window. Each value retains the existing Set value, Adjust by amount, and
Adjust by percentage operations. Blank rows remain unchanged, and Apply stages both
validated edits as one transaction.

The lower panel is a read-only planning calculator. Its original 2.4 annual
BaseResources multiplier came from one early Game1 example and is not a general
RTW3 budget formula. The [Games 1â€“9 comparison](BUDGET_CALCULATOR_RESEARCH.md)
documents the current discrepancies and supersedes that original assumption.

The development calculator now excludes ships with final fates and museum ships,
applies reserve/mothball reductions, and accounts for hurried and halted surface
construction. Player intelligence costs use target-nation records for the observed
levels 0 and 3; other levels and AI-nation intelligence remain uncalculated.

Provisional domestic income uses BaseResources × BudgetModifier × FleetSize / 10,
then derives monthly income and research with rounding. This is an explicitly
incomplete estimate: possession income and other engine adjustments remain
unverified. The comparison report records where this estimate differs from RTW3.

Missing aircraft and training costs display **Not calculated**, rather than zero.
Construction shows the surface-ship component; dock expansion, submarine and
fortification costs are flagged separately when relevant. Maintenance remains a
partial surface-ship estimate. **Calculated expenses (subtotal)** includes only
calculated components, and monthly balance is withheld while costs are incomplete.
No projected expense or income fields are written to the save.

The warning is always visible, including during input validation:
**Under development: calculator estimates may differ from the amounts shown in-game.
Uncalculated costs are not zero and are excluded from the subtotal.**

Choose **Infrastructure and Fortifications Manager** to edit the selected nation's existing `DockSize`
field. This controls the maximum displacement that can be built in that nation's
dockyards. See [Fortifications](FORTIFICATIONS.md) for the fortification editor.

Ship Spawner remains a WIP context-menu placeholder. **Admiral Manager** appears only
for Nation0, which RTW3 always uses as the player nation, and edits the stored
`AdmiralName` and `Prestige` fields.
All edits remain in memory until Save or Save As is selected in the main window.
