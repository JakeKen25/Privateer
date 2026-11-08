# Budget formula first pass, 2026-11-07

The supplied formula document is an unverified research lead, not confirmed
game source. The first calculator pass implements player income, research,
intelligence, academy costs and dock expansion. A second pass adds aircraft,
in-service submarine maintenance, active submarine construction, base expansion,
invasion, and the peace-era maintenance multiplier. The monthly balance range
remains in place; the full ship maintenance and training rules are incomplete.

## Comparison with saved campaigns

Using the installed `Data/MapData.dat` and current saved maps, yearly income
and research matched the recorded screenshot for each of Games 1–6, 8 and 9.
The USA 1971 example yields 1,949,230 yearly, 162,436 monthly and 16,244
research. Game 7 was replaced with a Game 6 copy and cannot be compared to its
older screenshot. Spain Game 8 yields intelligence 60 and academy 10; its
dock expansion calculation is 324. These comparisons do not prove rules that
were not exercised, including AI-nation budget differences and HFR research.

The game installation map and a campaign map can have different possession
slot numbers. The implementation matches the area and possession name when
the original slots do not match; ambiguous or unavailable map data falls back
to the old income estimate and marks the income labels as fallback.

## Second-pass comparison

Using the current saves, aircraft costs match the recorded screenshot figures
for all comparable cases, including Game3 18,194, Game4 831, Game6 47,428,
Game8 253 and Game9 2,080. Current Game6 construction matches the November
1971 screenshot at 29,866; Game3 matches the later 6,454 screenshot. Game8's
maintenance, construction, aircraft, research, training, intelligence and
balance all match its historical screenshot.

Surface maintenance remains approximate: Game3 calculates 6,023 versus 6,044
displayed, Game4 5,471 versus 5,583, and current Game6 35,169 versus 41,402.
The current Game6 training estimate is 9,050 versus 10,410 shown. Older
screenshots should not be treated as perfectly aligned with every current save
field. No active-invasion or halted-submarine screenshot was validated.

## Remaining work

Implement and compare full ship maintenance, all-active maintenance, halted
construction and training priorities; validate base expansion and invasion costs.
Validate pending training flags, age and repair cases, war modifiers, officer
effects and AI budgets against additional examples. Do not treat the total or
monthly balance as exact until the remaining components are validated.

