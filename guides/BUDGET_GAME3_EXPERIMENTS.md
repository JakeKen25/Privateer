# Game3 controlled budget comparisons — 2026-09-24

Source: six user-provided folders under `Documents/Codex/Privateer Calc`, each with a numbered RTWGame3.bcs and budget screenshot. Screen title identifies RTW3 1.01.44. Files were read only; no live game, executable, or save was modified.

## Baseline and controls

All six saves retain December 1, 1945. Annual income 395,520, monthly income 32,960, research 3,955 (12%), funds 17,107, intelligence zero, and the second maintenance box 6,130 are unchanged in all screenshots.

Compared with the unmodified BCS, all five variants share 244 field changes: these include blank-to-XXX values, IDs/report bookkeeping and added submarine location fields. They are not the individual experimental changes. After removing that common set, each variant has exactly its named ship setting change (two for halted + accelerated). Shared changes cannot automatically be assumed economically inert, but comparisons between variants isolate those ship flags.

MapData3.dat, RTWGame3.off, RTWGame3.sta and DesignFiles0.des match the baseline byte for byte in each variant. No player-nation field, aircraft-type field or air-unit field differs from baseline. Baseline active training selections: TorpedoWarfare=1, DamageControl=1, PilotTraining=1; GunneryTraining=NightFighting=0.

## Observed budget values

| Variant | Maintenance | Construction | Aircraft | Training | Total expenses | Balance |
|---|---:|---:|---:|---:|---:|---:|
| Unmodified | 6,044 | 3,759 | 18,194 | 1,436 | 33,388 | -428 |
| Single reserve | 5,908 | 3,759 | 18,036 | 1,392 | 33,050 | -90 |
| Single mothball | 5,826 | 3,759 | 18,036 | 1,366 | 32,942 | 18 |
| Single construction accelerated | 6,044 | 4,040 | 18,194 | 1,436 | 33,669 | -709 |
| Single construction halted | 6,044 | 2,009 | 18,194 | 1,436 | 31,638 | 1,322 |
| Single construction halted + accelerated | 6,044 | 2,009 | 18,194 | 1,436 | 31,638 | 1,322 |

All screenshot expense sums and monthly balances reconcile.

## Construction rules independently supported

The affected ship is CV Fu Chi Hen, Ship376, ID 9276:
Maintenance=253, MonthlyCost=1876, AircraftCapacity=64.

- Accelerated: Hurry 0→1. round(1876 × 1.15)=2157, an increase of 281. Total construction 3759+281=4040 exactly.
- Halted: Halted 0→1. floor(253/2)=126 replaces 1876. Total construction 3759−1876+126=2009 exactly.
- Halted + accelerated: both flags are 1; the total remains 2009. Halted takes precedence.

These rules already exist in the development calculator. The experiments validate them without requiring a production formula change.

## Status changes affect three expense categories

The affected ship is CV Hai Nan, Ship348, ID 8443:
Maintenance=268, MonthlyCost=1910, AircraftCapacity=70, EAM=0.
Only Status changes: 0→1 (reserve) or 0→2 (mothballed), beyond the shared changes described above.

| Change from baseline | Maintenance change | Aircraft change | Training change | Expense change |
|---|---:|---:|---:|---:|
| Reserve | -136 | -158 | -44 | -338 |
| Mothballed | -218 | -158 | -70 | -446 |

Current Privateer would reduce raw ship maintenance by 134 for reserve and 215 for mothballs. It therefore misses another 2 or 3 respectively even before other fleet costs.

An effective active maintenance charge of 272, reduced to 136 in reserve and 54 in mothballs, is consistent with both observed reductions. This is an inference, not proof of the adjustment from stored 268 to 272. Do not introduce a hard-coded +4 or a carrier multiplier from this one ship.

Both non-active statuses reduce aircraft spending by exactly 158 while the saved air-unit/type fields stay unchanged. Aircraft expense calculation must therefore consider ship readiness or another consequence of that readiness, not just aircraft counts. The specific rule remains unverified.

Training reductions are consistent with approximately 32% of the maintenance reduction (136×0.32≈44; 218×0.32≈70), but this does not establish the training cost base, rounding stage, or a universal percentage. The carrier/aircraft interaction and active pilot-training setting need separate experiments.

## Next narrowly targeted comparisons

Use this same baseline, without advancing the turn:

1. A non-carrier surface ship with zero aircraft capacity: active, reserve and mothballed, with budget screenshots. This separates general maintenance/status effects from carrier aviation.
2. One training selection changed at a time, capturing both current and pending settings. A setting that takes effect only later must not be treated as an immediate clean change.
3. A pilot-training-only change, if the game permits an immediate comparison, to isolate the aircraft/training interaction.
4. For income, a separate copied-save experiment changing BaseResources only is still needed; income never changes in this batch.

Keep the existing development warning. These experiments do not resolve income, total maintenance, aircraft or training formulas, and do not complete issue #22.
