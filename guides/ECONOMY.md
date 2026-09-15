# Economy and infrastructure managers

Right-click a nation and choose **Economy and Unrest Manager** to edit Funds, Base Resources, and Unrest Level
in one window. Each value retains the existing Set value, Adjust by amount, and
Adjust by percentage operations. Blank rows remain unchanged, and Apply stages both
validated edits as one transaction.

The lower panel is a read-only planning calculator. For the supplied January 1920
Game1 Germany save, `BaseResources=30000` corresponds to the screenshot's 72,000
yearly budget and 6,000 monthly budget, giving the observed factor of 2.4 per year.
The saved `ResearchPct=8` produces the screenshot's 480 research expense. Privateer
also totals the saved Maintenance field for active hulls and MonthlyCost for ships
under construction. It reads direct spending fields for aircraft, extra training,
and intelligence when they exist.

The game screenshot reports maintenance of 2,909 while the 47 stored German hull
records total 2,795, leaving 114 that is not identified by a verified per-nation or
per-ship field. The calculator labels its figure **Recorded ship maintenance** and
states that RTW3 can add engine-calculated expenses. It does not invent or write
unknown expense fields.

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
