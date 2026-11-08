# Budget formula first pass, 2026-11-07

The supplied formula document is an unverified research lead, not confirmed
game source. The first calculator pass implements player income, research,
intelligence, academy costs and dock expansion. The remaining expense lines
still use the earlier estimates. The monthly balance range remains in place.

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

## Remaining work

Implement and compare maintenance, all-active maintenance, ship and submarine
construction, base expansion, aircraft, training priorities and invasion costs.
Validate pending training flags, age and repair cases, war modifiers, officer
effects and AI budgets against additional examples. Do not treat the total or
monthly balance as exact until the remaining components are validated.

