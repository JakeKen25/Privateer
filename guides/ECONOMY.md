# Economy and infrastructure managers

Right-click a nation and choose **Economy and Unrest Manager** to edit Funds, Base Resources, and Unrest Level
in one window. Each value retains the existing Set value, Adjust by amount, and
Adjust by percentage operations. Blank rows remain unchanged, and Apply stages both
validated edits as one transaction.

The lower panel is a read-only planning calculator. Its original 2.4 annual
BaseResources multiplier came from one early Game1 example and is not a general
RTW3 budget formula. The [Games 1–9 comparison](BUDGET_CALCULATOR_RESEARCH.md)
documents the current discrepancies and supersedes that original assumption.

As of 0.9.4, Privateer totals stored Maintenance for all non-construction hull
records, including historical records, and MonthlyCost for construction hulls.
It does not yet account for hurried or halted construction, and it misses expense
categories such as submarine and dock construction. Its optional aircraft/training
spending fields are absent from the nine inspected saves, and its intelligence
lookup reads the player record instead of the target-nation records.

The calculator labels maintenance **Recorded ship maintenance**. The research
report distinguishes observed matches from candidate formulas and unresolved
costs. It does not change calculator behavior or write unknown expense fields.

The bottom of the calculator states that all displayed budget numbers are estimates
and that the underlying math still needs refinement.

Choose **Infrastructure and Fortifications Manager** to edit the selected nation's existing `DockSize`
field. This controls the maximum displacement that can be built in that nation's
dockyards. Fortifications remain a disabled placeholder until their storage and
side effects are verified.

Ship Spawner remains a WIP context-menu placeholder. **Admiral Manager** appears only
for Nation0, which RTW3 always uses as the player nation, and edits the stored
`AdmiralName` and `Prestige` fields.
All edits remain in memory until Save or Save As is selected in the main window.
