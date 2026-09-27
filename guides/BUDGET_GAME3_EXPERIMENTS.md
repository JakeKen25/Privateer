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



## September 26 follow-up: maintenance, intelligence and construction

Controlled ship-list and save comparisons support nearest-even rounding after
status multipliers: AF 100%, RF 50%, MB 20%. Chao Ching (no radar) costs
35/18/7. Class-2 search radar DD examples cost 37/18/7; cruiser examples
show 112 -> 116 active and 80 -> 84 active; carriers show 255 -> 259.
The calculator now includes the observed +2 DD and +4 CL/CV class-2 search
radar adjustments. These remain empirical rules; other radar classes and ship
types need verification. Fire-control radar had no additional visible charge
in these examples. Halted surface construction retains its separately verified
floor-half-maintenance rule.

The user confirmed intelligence costs are universally 80 per level per target:
low 80, medium 160, high 240, summed across targets without fleet-size scaling.
This supersedes the earlier fleet-size hypothesis. The historical Game8 value
of 60 remains a discrepancy to explain, not a reason to retain that hypothesis.

Construction reconciled exactly: Fu Chi Hen 1876 + Ho Pei 1883 + Battery 39
2400 + submarine Ho Hsie 295 = 6454. Battery 39 is an unfinished coastal
record with InPlay=0 and MonthlyCost=2400. Its displayed status 10 represents
construction time; its saved Status=0 must not be interpreted as completed.
Normal unfinished fortifications are included by InPlay and MonthlyCost.
Historical and completed records are excluded from construction.

Ho Hsie has RemainingBuildTime=18 but no saved MonthlyCost. The 295 observed
charge is not a universal submarine constant. Submarines with missing cost
fields remain explicitly excluded until their cost formula is established;
formats providing MonthlyCost can be summed directly. Thus the current live
Game3 calculator construction subtotal is 6159, with submarines identified as
missing. Fortification halt/acceleration rules also remain unverified.

Extra training reconciles as priorities plus academy: baseline 1096+340=1436;
latest Chao Ching mothball example 1071+340=1411. This does not establish a
general academy or training-base formula, so no fitted formula was added.

Remaining work: income and possession effects; aircraft and pilot expenses;
submarine construction/maintenance, dock expansion and special construction;
fortification recurring maintenance; other ship equipment/repair modifiers;
training base, academy costs and pending versus active doctrine settings.
The calculator retains its under-development warning and unknown-cost labels.


## September 26: budget tooltip and air-group totals (latest findings)

The current budget screenshot still shows maintenance 6044. Hovering over that
value exposes the following breakdown, transcribed from the user's screenshot:

| Tooltip item | Amount |
|---|---:|
| Ship maintenance | 3445 |
| Coastal artillery maintenance | 268 |
| Airbase maintenance | 1946 |
| Submarine maintenance | 385 |
| Missile storage | 1967 |

The first four entries sum exactly: 3445 + 268 + 1946 + 385 = 6044.
Missile storage is displayed in the tooltip but is NOT an additional amount
in that sum. Adding it again would double-count or otherwise misclassify costs.
Its actual accounting treatment is unresolved; visibility in a tooltip alone
does not establish whether it is charged, embedded elsewhere, or informational.

The user reports the adjacent 6130 value is an estimate with all ships active,
with a warning that actual wartime costs may increase it. It is not a second
actual expense and must not be added to maintenance. Its difference from 6044
is not, by itself, a measurement of reserve/mothball savings.

### Reconciliation with individual lists and saved fields

All 53 surface-ship rows total 3424 (CL 568, CV 1198, DD 1658). Therefore the
remaining 21 belongs specifically to the difference between aggregate SHIP
maintenance (3445) and displayed surface-ship rows (3424). Do not assign this
residual to fortifications or submarines, or patch it with a constant 21.
Possible mechanisms still require evidence; no cause has been established.

Completed infrastructure rows reconcile exactly with the tooltip:

- Six batteries: 48; eleven MTB squadrons: 220; combined coastal artillery: 268.
- Nineteen size-100 airbases at 94 plus two size-80 airbases at 80: 1946.
- Seven completed long-range submarines at 55: 385.

The observed completed battery/airbase charges fit 75% of saved Maintenance,
rounded to nearest-even: 6 -> 4, 13 -> 10, 126 -> 94, 106 -> 80.
MTB squadrons instead display their full saved Maintenance of 20 each.
This is an empirical Game3 pattern, still needing verification in other saves.
The current calculator has not yet implemented these recurring infrastructure
charges or a general submarine cost formula.

Battery 39 remains under construction: its displayed 2400 is construction,
not maintenance. Ho Hsie likewise contributes 295 construction, not the 55
charged for each completed submarine. Construction remains reconciled at 6454.

### Air-group management screenshot

The footer reports:

| Field | Value |
|---|---:|
| Single-engined aircraft | 1330 |
| Multi-engined aircraft | 626 |
| Total aircraft ASW value | 436 |
| Authorized aircraft in carrier-capable units | 326 |
| Training capacity for carrier aircrew | 359 |
| Total aircraft maintenance | 18194 |
| Total airbase maintenance | 1946 |

Aircraft maintenance matches the budget's Naval aircraft line exactly. Airbase
maintenance separately matches the maintenance tooltip, so it must not also be
added to Naval aircraft. The aircraft counts are useful formula inputs, but
these totals alone do not establish per-aircraft prices or pilot-training rules.

These notes supersede the earlier broad uncertainty about which category holds
the 21 residual. No further game changes were requested for this documentation
update. Next research can resume with the ship aggregate/row discrepancy,
aircraft cost formula, submarine cost rules, income, or training/academy costs.
