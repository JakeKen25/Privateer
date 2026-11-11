# Economy and infrastructure managers

**Development interface: 1.0.6.5 Beta.** Every budget row displays a numeric
estimate. The calculator has improved accuracy; [Budget estimates](BUDGET_ESTIMATES.md)
describes the current rules, evidence and remaining fallbacks.

Right-click a nation and choose **Economy and Unrest Manager** to edit Funds, Base Resources, and Unrest Level
in one window. Each value retains the existing Set value, Adjust by amount, and
Adjust by percentage operations. Blank rows remain unchanged, and Apply stages all
validated edits as one transaction.

The lower panel is a read-only planning calculator. It uses the supplied budget
rules for income, aircraft, maintenance, training and several other costs when
the necessary data can be resolved. Eight save and screenshot comparisons match
the displayed values. If possession data is unavailable, the income rows are
marked as fallback. AI nation budgets, halted construction and other unusual
conditions need further validation.

**Total expenses (estimated)** sums the expense rows; **Monthly balance
(estimated)** subtracts that total from estimated income. All-active maintenance
is displayed separately and is not added to expenses. The former ±10% planning
range has been removed. Invalid input still displays an actionable error; the
message disappears when the input is corrected.

No projected expense, income or assumption fields are written to the save.
Calculations remain provisional. Consult [Budget estimates](BUDGET_ESTIMATES.md)
for missing-data zero fallbacks and unresolved modifiers; a numeric zero does not
necessarily establish that no cost exists.

Choose **Infrastructure and Fortifications Manager** to edit the selected nation's existing `DockSize`
field. This controls the maximum displacement that can be built in that nation's
dockyards. See [Fortifications](FORTIFICATIONS.md) for the fortification editor.

Ship Spawner supports copying ships from another save and importing SDF designs;
see [Ship Spawner](SHIP_SPAWNER.md). **Admiral Manager** appears only for Nation0,
which RTW3 always uses as the player nation, and edits the stored `AdmiralName`
and `Prestige` fields.
All edits remain in memory until Save or Save As is selected in the main window.

