# RTW3 feature data catalog

> Dated schema and roadmap snapshot. Issue/milestone listings below reflect
> the audit date, not current release status. See [current status](PROJECT_STATUS.md).

Companion to [FEATURE_IMPLEMENTATION_GUIDE.md](FEATURE_IMPLEMENTATION_GUIDE.md).

Generated from the 2026-09-26 read-only inventory. Field names are observed schema,
not verified write semantics. `#` replaces numeric indices, including indices embedded
inside field names; consult the original file before designing a parser. Counts are
field occurrences across scanned files, including autosaves and historical records,
not counts of distinct live entities. No raw save values are reproduced.

## Install inventory

Files: 3856; bytes: 146829059; read errors: 0.

| Extension | Files | Bytes |
|---|---:|---:|
| `(none)` | 2 | 0 |
| `.acs` | 44 | 199369 |
| `.act` | 9 | 1431499 |
| `.bmp` | 349 | 2546706 |
| `.config` | 3 | 9012 |
| `.cs` | 1 | 12475 |
| `.dat` | 77 | 14450816 |
| `.dll` | 5 | 1072264 |
| `.eqs` | 1120 | 2290144 |
| `.exe` | 2 | 12208584 |
| `.hus` | 18 | 35029 |
| `.ico` | 2 | 766876 |
| `.ill` | 1 | 17796 |
| `.jpg` | 261 | 13577228 |
| `.lyr` | 11 | 674256 |
| `.ndt` | 9 | 1862644 |
| `.nsc` | 9 | 497329 |
| `.pdf` | 6 | 18762853 |
| `.png` | 26 | 997759 |
| `.resx` | 9 | 79948 |
| `.sdf` | 229 | 4342795 |
| `.tdf` | 1237 | 23666108 |
| `.ttp` | 1 | 18950 |
| `.tus` | 358 | 782537 |
| `.txt` | 26 | 149259 |
| `.vdf` | 1 | 51 |
| `.wav` | 40 | 46376772 |

### Representative relative paths

- (none): `ShipParts/Set2/PlaceHolder`; `ShipParts/Set3/PlaceHolder`
- .acs: `Data/Airship.acs`; `Data/DefaultAircraftShape.acs`; `Data/DefaultAircraftShape3.acs`
- .act: `Scenarios/Denmark Strait.act`; `Scenarios/Dogger Bank.act`; `Scenarios/Eastern Solomons.act`
- .bmp: `Flags/Airfield.bmp`; `Flags/AlliesGbIt.bmp`; `Flags/Anchor.bmp`
- .config: `Launcher.exe.config`; `Launcher/MutiLauncherSettings/MutiLauncherSettings.config`; `Launcher/Settings/LauncherSettings.Config`
- .cs: `Launcher/Localization/stringsEnglish.Designer.cs`
- .dat: `Data/AircraftBasicData.dat`; `Data/AircraftBasicData3.dat`; `Data/AircraftIcon.dat`
- .dll: `libSteamWrapper.dll`; `Microsoft.Toolkit.Forms.UI.Controls.WebView.dll`; `Steamworks.NET.dll`
- .eqs: `Data/Graphics/AAA CIWS AK 630.eqs`; `Data/Graphics/AAA CIWS Phalanx bottom.eqs`; `Data/Graphics/AAA CIWS Phalanx top.eqs`
- .exe: `Launcher.exe`; `RTW3.exe`
- .hus: `Data/Graphics/HullAMC.hus`; `Data/Graphics/HullAV.hus`; `Data/Graphics/HullB.hus`
- .ico: `Launcher/Icons/Matrix_DesktopIcon.ico`; `Launcher/Icons/Slitherine_DesktopIcon.ico`
- .ill: `Data/tmpShip.ill`
- .jpg: `Images/AAA.jpg`; `Images/aces.jpg`; `Images/Advance.jpg`
- .lyr: `Data/NoGo.LYR`; `Data/NoGo2.LYR`; `Data/NoGoN.LYR`
- .ndt: `Scenarios/Denmark Strait.ndt`; `Scenarios/Dogger Bank.ndt`; `Scenarios/Eastern Solomons.ndt`
- .nsc: `Scenarios/Denmark Strait.NSC`; `Scenarios/Dogger Bank.nsc`; `Scenarios/Eastern Solomons.NSC`
- .pdf: `End Users Agreement.pdf`; `whatsnew.pdf`; `Manuals/RTW3 FAQ v1.00.pdf`
- .png: `Launcher/Buttons/LauncherButton.png`; `Launcher/Buttons/LauncherButtonLarge.png`; `Launcher/Buttons/LauncherButtonLargeMX.png`
- .resx: `Launcher/Localization/stringsBrazilian Portuguese.resx`; `Launcher/Localization/stringsChinese.resx`; `Launcher/Localization/stringsEnglish.resx`
- .sdf: `Designs/10 in Coastal Battery.sdf`; `Designs/12 in coastal battery in turrets.sdf`; `Designs/6 in Coastal Battery.sdf`
- .tdf: `Data/IDes/4 in Field Battery.tdf`; `Data/IDes/4 in Field BatteryA.tdf`; `Data/IDes/AMC0X0.tdf`
- .ttp: `Data/tmpShip.ttp`
- .tus: `Data/Graphics/ADHT1.tus`; `Data/Graphics/ADHT2.tus`; `Data/Graphics/ADHT3.tus`
- .txt: `Data/Austria-HungaryNames.txt`; `Data/BuldCampEventConditions.txt`; `Data/chengenationcodeforevents.txt`
- .vdf: `Save/steam_autocloud.vdf`
- .wav: `Sounds/AirAttack1.wav`; `Sounds/AirAttack2.wav`; `Sounds/AirAttack3.wav`

## Saves inventory

Files: 164; bytes: 259702708; read errors: 0.

| Extension | Files | Bytes |
|---|---:|---:|
| `.bbi` | 5 | 612 |
| `.bcs` | 13 | 126199244 |
| `.dat` | 9 | 401511 |
| `.des` | 81 | 125832176 |
| `.log` | 10 | 220061 |
| `.off` | 14 | 1317506 |
| `.sac` | 10 | 4841988 |
| `.skv` | 12 | 3516 |
| `.sta` | 9 | 886029 |
| `.txt` | 1 | 65 |

### Representative relative paths

- .bbi: `Game2/BattleInfo.bbi`; `Game3/BattleInfo.bbi`; `Game6/BattleInfo.bbi`
- .bcs: `Game1/RTWGame1.bcs`; `Game2/Autosave.bcs`; `Game2/RTWGame2.bcs`
- .dat: `Game1/MapData1.dat`; `Game2/MapData2.dat`; `Game3/MapData3.dat`
- .des: `Game1/DesignFiles0.des`; `Game1/DesignFiles1.des`; `Game1/DesignFiles2.des`
- .log: `Game2/TLog.log`; `Game2/TTime.log`; `Game3/TLog.log`
- .off: `Game1/RTWGame1.off`; `Game2/Autosave.off`; `Game2/RTWGame2.off`
- .sac: `Game2/Autosave.sac`; `Game2/RTWGame2.sac`; `Game3/Autosave.sac`
- .skv: `Game2/AA Log.skv`; `Game2/Air Combat Log.skv`; `Game2/Bombing Log.skv`
- .sta: `Game1/RTWGame1.sta`; `Game2/RTWGame2.sta`; `Game3/RTWGame3.sta`
- .txt: `Game1/RTW3_SAVE_EDITOR_LOG.txt`

## Open issue coverage

| Issue | Feature | Target |
|---|---|---|
| [#14](https://github.com/JakeKen25/Privateer/issues/14) | Add ship spawner | 05 — 2.0.0 — Custom nations and custom-design spawning |
| [#16](https://github.com/JakeKen25/Privateer/issues/16) | Create tutorials | 01 — 0.9.5 — Reliability, tutorials, and verified data |
| [#17](https://github.com/JakeKen25/Privateer/issues/17) | Add custom nation builder | 05 — 2.0.0 — Custom nations and custom-design spawning |
| [#19](https://github.com/JakeKen25/Privateer/issues/19) | Build Submarine Manager | 02 — 0.10.0 — Submarine management |
| [#21](https://github.com/JakeKen25/Privateer/issues/21) | Add war/alliances to relationship manager | 03 — 0.11.0 — Wars and alliances |
| [#22](https://github.com/JakeKen25/Privateer/issues/22) | Fix budget calculator | 01 — 0.9.5 — Reliability, tutorials, and verified data |
| [#23](https://github.com/JakeKen25/Privateer/issues/23) | Add graphics/pictures | 06 — 2.0.1 — Public-domain visuals and documentation polish |
| [#25](https://github.com/JakeKen25/Privateer/issues/25) | Create/add logo | 06 — 2.0.1 — Public-domain visuals and documentation polish |
| [#27](https://github.com/JakeKen25/Privateer/issues/27) | Validate Aircraft and Fortifications Managers in-game | 01 — 0.9.5 — Reliability, tutorials, and verified data |
| [#28](https://github.com/JakeKen25/Privateer/issues/28) | Verify war and alliance state transitions before editor implementation | 01 — 0.9.5 — Reliability, tutorials, and verified data |
| [#29](https://github.com/JakeKen25/Privateer/issues/29) | Source and document public-domain photos and artwork | 01 — 0.9.5 — Reliability, tutorials, and verified data |
| [#30](https://github.com/JakeKen25/Privateer/issues/30) | Ship spawner phase 1: built-in designs | 04 — 1.0.0 — Ship spawning from built-in designs |
| [#31](https://github.com/JakeKen25/Privateer/issues/31) | Ship spawner phase 2: custom designs | 05 — 2.0.0 — Custom nations and custom-design spawning |
| [#32](https://github.com/JakeKen25/Privateer/issues/32) | Extend tutorials for submarines, diplomacy, spawning and custom nations | 06 — 2.0.1 — Public-domain visuals and documentation polish |
| [#33](https://github.com/JakeKen25/Privateer/issues/33) | Create AAR logger | 07 — 3.0.0 — AAR Logger |

## Save schemas

### `[AIReports]`

| Field pattern | Occurrences |
|---|---:|
| `Report#B` | 427 |
| `Report#BB` | 427 |
| `Report#BC` | 427 |
| `Report#CA` | 427 |
| `Report#CL` | 427 |
| `Report#Course` | 427 |
| `Report#DD` | 427 |
| `Report#Delay` | 427 |
| `Report#Location` | 427 |
| `Report#MinuteStamp` | 427 |
| `Report#OriginatorAsText` | 427 |
| `Report#Side` | 427 |
| `Report#TR` | 427 |
| `Report#Text` | 427 |

### `[AirFormations]`

| Field pattern | Occurrences |
|---|---:|
| `AF#ATRI` | 894 |
| `AF#AircraftDestroyed` | 894 |
| `AF#AircraftNumber` | 894 |
| `AF#AircraftType` | 894 |
| `AF#BombHits` | 894 |
| `AF#CarrierCapable` | 894 |
| `AF#CombinedStrikeSpeed` | 894 |
| `AF#ConfirmTargetLoc` | 894 |
| `AF#Course` | 894 |
| `AF#Damaged#` | 8940 |
| `AF#DamagedFlying` | 894 |
| `AF#Disruption` | 894 |
| `AF#Dogleg` | 894 |
| `AF#Experience` | 894 |
| `AF#GroupIndex` | 894 |
| `AF#GuidedBombs` | 894 |
| `AF#HomeBaseScn` | 894 |
| `AF#Id` | 894 |
| `AF#IsFatigued` | 894 |
| `AF#Kills` | 894 |
| `AF#LeadFormationId` | 894 |
| `AF#LoadedNumber` | 894 |
| `AF#Loadout` | 894 |
| `AF#Location` | 894 |
| `AF#LossAirToAirF` | 894 |
| `AF#LossAirToAirO` | 894 |
| `AF#LossHAAFire` | 894 |
| `AF#LossLAAFire` | 894 |
| `AF#LossMAAFire` | 894 |
| `AF#LossOperational` | 894 |
| `AF#LossSAMFire` | 894 |
| `AF#MissileHits` | 894 |
| `AF#Mission` | 894 |
| `AF#Name` | 894 |
| `AF#Nation` | 894 |
| `AF#NightCapable` | 894 |
| `AF#OrderedState` | 894 |
| `AF#ParentFormationId` | 894 |
| `AF#PilotFatigue` | 894 |
| `AF#PriorityTarget` | 894 |
| `AF#Recon` | 894 |
| `AF#RemainingFuel` | 894 |
| `AF#Side` | 894 |
| `AF#StartATRI` | 894 |
| `AF#Status` | 894 |
| `AF#StatusCount` | 894 |
| `AF#TargetLoc` | 894 |
| `AF#TorpedoHits` | 894 |
| `AF#UnitId` | 894 |
| `AFID` | 10 |
| `AFNumber` | 10 |
| `AU#AircraftTypeId` | 894 |
| `ScoutCount` | 10 |

### `[AirUnits]`

| Field pattern | Occurrences |
|---|---:|
| `AU#AirKills` | 6446 |
| `AU#AircraftNumber` | 6446 |
| `AU#AircraftType` | 6446 |
| `AU#AircraftTypeId` | 6446 |
| `AU#AutoUpgrade` | 6446 |
| `AU#BombHits` | 6446 |
| `AU#CarrierCapable` | 6446 |
| `AU#DesiredAircraftNumber` | 6446 |
| `AU#Elite` | 6446 |
| `AU#Experience` | 6446 |
| `AU#HomeBase` | 6446 |
| `AU#Id` | 6446 |
| `AU#MissileHits` | 6446 |
| `AU#Name` | 6446 |
| `AU#Nation` | 6446 |
| `AU#NightCapable` | 6446 |
| `AU#Recon` | 6446 |
| `AU#Role` | 6446 |
| `AU#TorpedoHits` | 6446 |
| `AirUnitNo` | 13 |

### `[AircraftTypes]`

| Field pattern | Occurrences |
|---|---:|
| `ACTypesNo` | 13 |
| `AT#AvailableAircraft` | 5114 |
| `AT#BaseModelYear` | 5114 |
| `AT#Bombing` | 5114 |
| `AT#Carrier` | 5114 |
| `AT#Ceiling` | 5114 |
| `AT#Climb` | 5114 |
| `AT#CruiseAltitude` | 5114 |
| `AT#CruiseSpeed` | 5114 |
| `AT#DevelopmentTime` | 5114 |
| `AT#Firepower` | 5114 |
| `AT#Floatplane` | 5114 |
| `AT#HvyBombLoadNumber` | 5114 |
| `AT#HvyBombLoadSize` | 5114 |
| `AT#HvyEndurance` | 5114 |
| `AT#Id` | 5114 |
| `AT#LtBombLoadNumber` | 5114 |
| `AT#LtBombLoadSize` | 5114 |
| `AT#LtEndurance` | 5114 |
| `AT#Maneuver` | 5114 |
| `AT#Manufacturer` | 5114 |
| `AT#MaxFuel` | 5114 |
| `AT#MaxSpeed` | 5114 |
| `AT#MedBombLoadNumber` | 5114 |
| `AT#MedBombLoadSize` | 5114 |
| `AT#MedEndurance` | 5114 |
| `AT#Missile#` | 5114 |
| `AT#Name` | 5114 |
| `AT#Nation` | 5114 |
| `AT#Obsolete` | 5114 |
| `AT#Purpose` | 5114 |
| `AT#Radar` | 5114 |
| `AT#Reliability` | 5114 |
| `AT#ReliabilityKnown` | 5114 |
| `AT#Special` | 5114 |
| `AT#Torpedo#` | 10228 |
| `AT#Toughness` | 5114 |
| `AT#ValuesKnown` | 5114 |
| `AT#Version` | 5114 |
| `AT#Year` | 5114 |

### `[BATTLE INFO]`

| Field pattern | Occurrences |
|---|---:|
| `BattleArea` | 5 |
| `BattleIndex` | 5 |
| `BattleOpponentIndex` | 5 |
| `BattlePossession` | 5 |
| `BattleSize` | 5 |

### `[BattleType]`

| Field pattern | Occurrences |
|---|---:|
| `BattleType` | 10 |
| `ShipCount` | 10 |

### `[CampaignDivisions]`

| Field pattern | Occurrences |
|---|---:|
| `CampDiv#Abbreviation` | 266 |
| `CampDiv#CDivId` | 266 |
| `CampDiv#Commander` | 266 |
| `CampDiv#DivisionExperience` | 266 |
| `CampDiv#DivisionType` | 266 |
| `CampDiv#LeadDivision` | 266 |
| `CampDiv#Name` | 266 |
| `CampDiv#Role` | 266 |
| `CampDiv#ShipCount` | 266 |
| `CampDiv#ShipId#` | 761 |
| `CampDiv#Training` | 266 |
| `CampDivNo` | 14 |

### `[Division#]`

| Field pattern | Occurrences |
|---|---:|
| `AIControl` | 368 |
| `Accusmoke` | 368 |
| `Base` | 368 |
| `CappedDiv` | 368 |
| `Course` | 368 |
| `DivisionName` | 368 |
| `Force` | 368 |
| `ForceLeadDivision` | 368 |
| `Formation` | 368 |
| `HasBeenHome` | 368 |
| `InPort` | 368 |
| `KHS` | 368 |
| `LeadDiv` | 368 |
| `LockedAI` | 368 |
| `Losses` | 368 |
| `MinutesInCombat` | 368 |
| `Objective` | 368 |
| `OriginalCourse` | 368 |
| `OriginalSpeed` | 368 |
| `PortDelay` | 368 |
| `Reported` | 368 |
| `Role` | 368 |
| `Ship#AAKills` | 437 |
| `Ship#AirToSurfaceMissiles` | 437 |
| `Ship#AirTorpedoes` | 437 |
| `Ship#Ammo#` | 3933 |
| `Ship#AskedCount` | 437 |
| `Ship#BombHits` | 437 |
| `Ship#BombTarget` | 437 |
| `Ship#Bulkhead` | 437 |
| `Ship#Classname` | 437 |
| `Ship#Commander` | 437 |
| `Ship#Course` | 437 |
| `Ship#CrewQuality` | 437 |
| `Ship#CurrentASWValue` | 437 |
| `Ship#CurrentEndurance` | 437 |
| `Ship#CurrentFCPositions` | 437 |
| `Ship#CurrentFloatPoints` | 437 |
| `Ship#CurrentSecondariesPort` | 437 |
| `Ship#CurrentSecondariesStarboard` | 437 |
| `Ship#CurrentSpeed` | 437 |
| `Ship#CurrentSuperstructurePoints` | 437 |
| `Ship#CurrentTertiariesPort` | 437 |
| `Ship#CurrentTertiariesStarboard` | 437 |
| `Ship#DesignId` | 437 |
| `Ship#ElectricDisabled` | 437 |
| `Ship#EngineDamage` | 437 |
| `Ship#EngineDisabled` | 437 |
| `Ship#FCRadarClass` | 437 |
| `Ship#FT` | 437 |
| `Ship#FireLevel` | 437 |
| `Ship#FireTrend` | 437 |
| `Ship#FlightActivity` | 437 |
| `Ship#Flooding` | 437 |
| `Ship#GrateFoulLevel` | 437 |
| `Ship#HVU` | 437 |
| `Ship#HeavyHits` | 437 |
| `Ship#HitCount` | 437 |
| `Ship#Hits#` | 788 |
| `Ship#HitsScored#` | 1311 |
| `Ship#Id` | 437 |
| `Ship#InitialAmmo#` | 1311 |
| `Ship#InitialDivision` | 431 |
| `Ship#LL` | 437 |
| `Ship#LightHits` | 437 |
| `Ship#Locked` | 437 |
| `Ship#MediumHits` | 437 |
| `Ship#Mines` | 437 |
| `Ship#MissileHits` | 437 |
| `Ship#Mount#Destroyed` | 753 |
| `Ship#Mount#ReloadTime` | 753 |
| `Ship#Mount#Reloads` | 753 |
| `Ship#Mount#TorpsLeft` | 753 |
| `Ship#Name` | 437 |
| `Ship#Nation` | 437 |
| `Ship#NoRecovery` | 437 |
| `Ship#Nolaunch` | 437 |
| `Ship#ObsoleteDate` | 437 |
| `Ship#OrderedCourse` | 437 |
| `Ship#OrderedSpeed` | 437 |
| `Ship#OrderedStrikeDelay` | 437 |
| `Ship#OriginalEndurance` | 437 |
| `Ship#PF` | 437 |
| `Ship#RadarSightingLevel` | 437 |
| `Ship#RefitOverdue` | 437 |
| `Ship#RoundsFired#` | 1311 |
| `Ship#RoundsFiredAtMeLastTurn` | 437 |
| `Ship#RudderStatus` | 437 |
| `Ship#SAF` | 437 |
| `Ship#SSMHitsScored` | 437 |
| `Ship#SearchRadarClass` | 437 |
| `Ship#Side` | 437 |
| `Ship#SightingLevel` | 437 |
| `Ship#Sinking` | 437 |
| `Ship#SmokeFloats` | 437 |
| `Ship#Speed` | 437 |
| `Ship#Sunk` | 437 |
| `Ship#Surprised` | 437 |
| `Ship#Survivors` | 437 |
| `Ship#TimeToRaiseSteam` | 437 |
| `Ship#TorpedoHits` | 437 |
| `Ship#TorpedoHitsScored` | 437 |
| `Ship#Turret#Ammo#` | 4158 |
| `Ship#Turret#Destroyed` | 1386 |
| `Ship#Turret#Silenced` | 1386 |
| `Ship#Warned#` | 1748 |
| `Ship#Warned#AA` | 437 |
| `Ship#WarnedForFuelPercentage#` | 874 |
| `Ship#WarnedOut` | 437 |
| `ShipCount` | 368 |
| `Shortname` | 368 |
| `Side` | 368 |
| `Speed` | 368 |
| `SpottedByAir` | 368 |
| `SpottedByAir#` | 368 |
| `TacticalStance` | 368 |
| `TimeToRaiseSteam` | 368 |
| `Tr#` | 12873 |
| `TrackCount` | 368 |
| `TurnTogether` | 368 |
| `TurnsSinceDecision` | 368 |
| `WI` | 368 |
| `WithdrawMe` | 368 |

### `[EUT]`

| Field pattern | Occurrences |
|---|---:|
| `EUT#` | 1300 |

### `[Environment]`

| Field pattern | Occurrences |
|---|---:|
| `AirPriority#` | 20 |
| `Bias` | 10 |
| `CenterPoint` | 10 |
| `CheckedMorningMist` | 10 |
| `Day` | 10 |
| `DaySightingDistance` | 10 |
| `EA` | 10 |
| `EnvironmentFile` | 10 |
| `FFR` | 10 |
| `FirstMissile` | 10 |
| `FogBanks` | 10 |
| `GameEnded` | 10 |
| `Hour` | 10 |
| `LandLayer#` | 20 |
| `Length` | 10 |
| `Minute` | 10 |
| `Month` | 10 |
| `MorningMist` | 10 |
| `NightSightMod` | 10 |
| `NightSightingDistance` | 10 |
| `NoOrdersBS` | 10 |
| `OriginalDataPath` | 10 |
| `OriginalTitle` | 10 |
| `PlayerStartpos#` | 20 |
| `Precipitation` | 10 |
| `SeaState` | 10 |
| `SightMod` | 10 |
| `Size` | 10 |
| `Squalls` | 10 |
| `TimeElapsed` | 10 |
| `TimeOutLimit` | 10 |
| `Variation` | 10 |
| `WindDirection` | 10 |
| `Windspeed` | 10 |
| `Year` | 10 |

### `[Force#]`

| Field pattern | Occurrences |
|---|---:|
| `AIControl` | 147 |
| `ActivateAlternateOnSighting` | 147 |
| `ActivateOnSighting` | 147 |
| `AltRandomTimeToRaiseSteam` | 147 |
| `AltTimeToRaiseSteam` | 147 |
| `AlternatePoint` | 147 |
| `AlternateWPIndex` | 147 |
| `CSD` | 147 |
| `CapLevel` | 147 |
| `DivCount` | 147 |
| `DoNotEnterPort` | 147 |
| `EnterAll` | 147 |
| `FW` | 147 |
| `FlotillaAttack` | 147 |
| `ForceKind` | 147 |
| `HasChangedLead` | 147 |
| `Home` | 147 |
| `HomeDistance` | 147 |
| `InterceptRange` | 147 |
| `MainForce` | 147 |
| `Mission` | 147 |
| `Name` | 147 |
| `NightSearch` | 147 |
| `Objective` | 147 |
| `RandomTimeToRaiseSteam` | 147 |
| `RepeatSearch` | 147 |
| `SearchDistance` | 147 |
| `SearchInterval` | 147 |
| `SearchLimitLeft` | 147 |
| `SearchLimitRight` | 147 |
| `SearchPatternCurrent#` | 2646 |
| `SearchPatternOrdered#` | 2646 |
| `Side` | 147 |
| `TimeToRaiseSteam` | 147 |
| `TimeToTurnAway` | 147 |
| `TwoPhaseSearch` | 147 |
| `WPIndex` | 147 |
| `WS#Waypoint#LL` | 75 |

### `[General]`

| Field pattern | Occurrences |
|---|---:|
| `#RedMess` | 13 |
| `ACE` | 13 |
| `ACRequest` | 13 |
| `ACRequestRole` | 13 |
| `AIWarLength` | 13 |
| `AiAdvantage` | 13 |
| `AirbaseSize` | 13 |
| `ArmyOffensive` | 13 |
| `AutoBuildSubType` | 13 |
| `AutoBuildSubs` | 13 |
| `BattleAlliedNationIdx` | 13 |
| `BattleAreaName` | 13 |
| `BattleEnemyAlliedNationIdx` | 13 |
| `BattleIsSurpriseAttack` | 13 |
| `BattlePossessionName` | 13 |
| `CRI` | 13 |
| `CampaignStartYear` | 13 |
| `CancelledBB` | 13 |
| `CancelledCV` | 13 |
| `CarrierIntel` | 13 |
| `DPR#` | 169 |
| `Day` | 13 |
| `DeclineCount` | 13 |
| `EWAdvantage` | 13 |
| `EWAdvantageReported` | 13 |
| `EnemyDeclineCount` | 13 |
| `EnemyInvasionTargetName` | 13 |
| `EnemyVP` | 13 |
| `EvilPlan` | 13 |
| `FFC` | 13 |
| `FirstBB` | 13 |
| `FleetEx` | 13 |
| `FleetExHeldThisYear` | 13 |
| `FleetSize` | 13 |
| `GOR` | 13 |
| `GameMaxAirbaseSize` | 13 |
| `HardPeaceDeals` | 13 |
| `HasBeenBattle` | 13 |
| `HasBeenTreaty` | 13 |
| `HasShownScoutForce` | 13 |
| `IBP` | 13 |
| `IDNo` | 13 |
| `InvasionTargetName` | 13 |
| `JST` | 13 |
| `LastMissionIdx` | 13 |
| `LastTargetType` | 13 |
| `LendLeaseDone` | 13 |
| `MadScientist` | 13 |
| `MissileHits` | 13 |
| `Month` | 13 |
| `MuseumShip` | 13 |
| `NoBuyShipsRequest` | 13 |
| `NoScr` | 13 |
| `OAR#` | 221 |
| `PWS` | 13 |
| `ParliamentDelay` | 13 |
| `ProtLoss` | 13 |
| `Purge` | 13 |
| `RadarIntel` | 13 |
| `ResearchSpeed` | 13 |
| `ResearchVariation` | 13 |
| `RevolutionPending` | 13 |
| `SLWW` | 13 |
| `ScenarioInProgress` | 13 |
| `SubBanPoss` | 13 |
| `SubBanTime` | 13 |
| `TA#` | 78 |
| `TBN` | 13 |
| `TFW` | 13 |
| `TQ#` | 13 |
| `TechQuirk` | 13 |
| `TotalWar` | 13 |
| `Treaties` | 13 |
| `TreatyCalibreLimit` | 13 |
| `TreatyDisplacementLimit` | 13 |
| `TreatyTimeRemaining` | 13 |
| `TreatyTonnageBasePercentage` | 13 |
| `War` | 13 |
| `Year` | 13 |

### `[IntelReports]`

| Field pattern | Occurrences |
|---|---:|
| `Intel#` | 12408 |
| `ReportNo` | 13 |

### `[Locations]`

| Field pattern | Occurrences |
|---|---:|
| `Location#AirfieldText` | 282 |
| `Location#BaseGroup` | 282 |
| `Location#BaseValue` | 282 |
| `Location#Capacity` | 282 |
| `Location#EnterPortRange` | 282 |
| `Location#EntryPoint` | 282 |
| `Location#ExitNavPoint` | 282 |
| `Location#ForceStartPoint` | 282 |
| `Location#HasAirfield` | 282 |
| `Location#LabelOnly` | 282 |
| `Location#Location` | 282 |
| `Location#Name` | 282 |
| `Location#Nation` | 282 |
| `Location#OpLossDist` | 282 |
| `Location#Size` | 282 |
| `Location#SubmarineBase` | 282 |

### `[MapAreas]`

| Field pattern | Occurrences |
|---|---:|
| `MapArea#Commander` | 144 |
| `MapArea#MineLevel#` | 1296 |
| `MapArea#Possession#BaseValue` | 1101 |
| `MapArea#Possession#BuildingBase` | 1101 |
| `MapArea#Possession#Invaded` | 1101 |
| `MapArea#Possession#InvasionSupport` | 1101 |
| `MapArea#Possession#Name` | 1101 |
| `MapArea#Possession#Oil` | 1101 |
| `MapArea#Possession#Owner` | 1101 |
| `MapArea#Possession#Rebellion` | 1101 |
| `MapArea#Possession#TakenFrom` | 1101 |
| `MapArea#Possession#Value` | 1101 |
| `MapArea#PossessionCount` | 144 |
| `MapAreaCount` | 9 |

### `[Minefields]`

| Field pattern | Occurrences |
|---|---:|
| `Minefield#Density` | 973 |
| `Minefield#PlayerLaid` | 973 |
| `Minefield#Point#LL` | 34900 |
| `Minefield#Points` | 973 |
| `Minefield#Side` | 973 |
| `Minefield#StartMonth` | 973 |
| `Minefield#Title` | 973 |

### `[Nation#CoastalArtillery]`

| Field pattern | Occurrences |
|---|---:|
| `CACount` | 120 |
| `Ship#ASWValue` | 3820 |
| `Ship#AccomodationCramped` | 3820 |
| `Ship#Active` | 3820 |
| `Ship#AircraftCapacity` | 3820 |
| `Ship#AngledFlightDeck` | 3820 |
| `Ship#BattleStars` | 3820 |
| `Ship#BuildProgress` | 3820 |
| `Ship#BuildingNationIdx` | 3820 |
| `Ship#CLAA` | 3820 |
| `Ship#Classname` | 3820 |
| `Ship#ColonialService` | 3820 |
| `Ship#CommanderId` | 3820 |
| `Ship#Cost` | 3820 |
| `Ship#Course` | 3820 |
| `Ship#CrewQuality` | 3820 |
| `Ship#Deployed` | 3820 |
| `Ship#Description` | 3820 |
| `Ship#DesignRefId` | 3820 |
| `Ship#DestinationAreaName` | 3820 |
| `Ship#Displacement` | 3820 |
| `Ship#EAM` | 3820 |
| `Ship#EnemyBelt` | 3820 |
| `Ship#EnemyClassName` | 3820 |
| `Ship#EnemySpeed` | 3820 |
| `Ship#EnginePriority` | 3820 |
| `Ship#EngineYear` | 3820 |
| `Ship#EnhancedSonar` | 3820 |
| `Ship#FCRadarClass` | 3820 |
| `Ship#Fate` | 3820 |
| `Ship#FlightDeckCatapults` | 3820 |
| `Ship#FuelType` | 3820 |
| `Ship#HSSM` | 3820 |
| `Ship#Halted` | 3820 |
| `Ship#Helipad` | 3820 |
| `Ship#Hurry` | 3820 |
| `Ship#Id` | 3820 |
| `Ship#InPlay` | 3820 |
| `Ship#JetCapable` | 3820 |
| `Ship#LocationAreaName` | 3820 |
| `Ship#LogEntry#` | 11008 |
| `Ship#MMP` | 3820 |
| `Ship#MSG` | 3820 |
| `Ship#MSSM` | 3820 |
| `Ship#MainCalibre` | 3820 |
| `Ship#Maintenance` | 3820 |
| `Ship#Mine capacity` | 3820 |
| `Ship#Mines` | 3820 |
| `Ship#MonthlyCost` | 3820 |
| `Ship#Name` | 3820 |
| `Ship#NumberOfLogEntries` | 3820 |
| `Ship#ObsoleteDate` | 3820 |
| `Ship#OldASW` | 3820 |
| `Ship#OldStatus` | 3820 |
| `Ship#OrderedAreaName` | 3820 |
| `Ship#PlayerIntel` | 3820 |
| `Ship#RadarLimit` | 3820 |
| `Ship#Range` | 3820 |
| `Ship#Rebuild` | 3820 |
| `Ship#Reinforcement` | 3820 |
| `Ship#RepairTime` | 3820 |
| `Ship#SearchRadarClass` | 3820 |
| `Ship#ShipType` | 3820 |
| `Ship#Side` | 3820 |
| `Ship#Speed` | 3820 |
| `Ship#Status` | 3820 |
| `Ship#TPS` | 3820 |
| `Ship#TimeToRefit` | 3820 |
| `Ship#TowedArray` | 3820 |
| `Ship#Training` | 3820 |
| `Ship#Used` | 3820 |
| `Ship#YearBuilt` | 3820 |

### `[Nation#Losses]`

| Field pattern | Occurrences |
|---|---:|
| `AUXLost` | 120 |
| `BBLost` | 120 |
| `BCLost` | 120 |
| `BLost` | 120 |
| `CALost` | 120 |
| `CLLost` | 120 |
| `CVLLost` | 120 |
| `CVLost` | 120 |
| `DDLost` | 120 |
| `LTLost` | 120 |
| `MSLost` | 120 |
| `SSLost` | 120 |

### `[Nation#Ships]`

| Field pattern | Occurrences |
|---|---:|
| `Ship#ASWValue` | 37916 |
| `Ship#AccomodationCramped` | 37916 |
| `Ship#Active` | 37916 |
| `Ship#AircraftCapacity` | 37916 |
| `Ship#AngledFlightDeck` | 37916 |
| `Ship#BattleStars` | 37916 |
| `Ship#BuildProgress` | 37916 |
| `Ship#BuildingNationIdx` | 37916 |
| `Ship#CLAA` | 37916 |
| `Ship#Classname` | 37916 |
| `Ship#ColonialService` | 37916 |
| `Ship#CommanderId` | 37916 |
| `Ship#Cost` | 37916 |
| `Ship#Course` | 37916 |
| `Ship#CrewQuality` | 37916 |
| `Ship#Deployed` | 37916 |
| `Ship#Description` | 37916 |
| `Ship#DesignRefId` | 37916 |
| `Ship#DestinationAreaName` | 37916 |
| `Ship#Displacement` | 37916 |
| `Ship#EAM` | 37916 |
| `Ship#EnemyBelt` | 37916 |
| `Ship#EnemyClassName` | 37916 |
| `Ship#EnemySpeed` | 37916 |
| `Ship#EnginePriority` | 37916 |
| `Ship#EngineYear` | 37916 |
| `Ship#EnhancedSonar` | 37916 |
| `Ship#FCRadarClass` | 37916 |
| `Ship#Fate` | 37916 |
| `Ship#FlightDeckCatapults` | 37916 |
| `Ship#FuelType` | 37916 |
| `Ship#HSSM` | 37916 |
| `Ship#Halted` | 37916 |
| `Ship#Helipad` | 37916 |
| `Ship#Hurry` | 37916 |
| `Ship#Id` | 37916 |
| `Ship#InPlay` | 37916 |
| `Ship#JetCapable` | 37916 |
| `Ship#LocationAreaName` | 37916 |
| `Ship#LogEntry#` | 1360065 |
| `Ship#MMP` | 37916 |
| `Ship#MSG` | 37916 |
| `Ship#MSSM` | 37916 |
| `Ship#MainCalibre` | 37916 |
| `Ship#Maintenance` | 37916 |
| `Ship#Mine capacity` | 37916 |
| `Ship#Mines` | 37916 |
| `Ship#MonthlyCost` | 37916 |
| `Ship#Name` | 37916 |
| `Ship#NumberOfLogEntries` | 37916 |
| `Ship#ObsoleteDate` | 37916 |
| `Ship#OldASW` | 37916 |
| `Ship#OldStatus` | 37916 |
| `Ship#OrderedAreaName` | 37916 |
| `Ship#PlayerIntel` | 37916 |
| `Ship#RadarLimit` | 37916 |
| `Ship#Range` | 37916 |
| `Ship#Rebuild` | 37916 |
| `Ship#Reinforcement` | 37916 |
| `Ship#RepairTime` | 37916 |
| `Ship#SearchRadarClass` | 37916 |
| `Ship#ShipType` | 37916 |
| `Ship#Side` | 37916 |
| `Ship#Speed` | 37916 |
| `Ship#Status` | 37916 |
| `Ship#TPS` | 37916 |
| `Ship#TimeToRefit` | 37916 |
| `Ship#TowedArray` | 37916 |
| `Ship#Training` | 37916 |
| `Ship#Used` | 37916 |
| `Ship#YearBuilt` | 37916 |

### `[Nation#Submarines]`

| Field pattern | Occurrences |
|---|---:|
| `Sub#Accuracy` | 4931 |
| `Sub#Active` | 4931 |
| `Sub#Availability` | 4931 |
| `Sub#DestinationAreaName` | 4931 |
| `Sub#Fate` | 4931 |
| `Sub#Halted` | 4931 |
| `Sub#InPlay` | 4931 |
| `Sub#LocationAreaName` | 4673 |
| `Sub#Name` | 4931 |
| `Sub#OrderedAreaName` | 4931 |
| `Sub#RemainingBuildTime` | 4931 |
| `Sub#SubType` | 4931 |
| `Sub#Sunk` | 4931 |
| `Sub#YearBuilt` | 4931 |
| `SubCount` | 120 |

### `[Nation#]`

| Field pattern | Occurrences |
|---|---:|
| `AIAlliance#` | 960 |
| `AITension#` | 960 |
| `APShellPriority` | 120 |
| `AdmiralName` | 120 |
| `AdmiralRank` | 120 |
| `AicraftPriority#` | 240 |
| `AirSeaRescue` | 120 |
| `AirUnitName` | 120 |
| `AircraftNumber` | 120 |
| `Alarmed` | 120 |
| `Allied` | 120 |
| `AmmoDoctrine` | 120 |
| `AmmoLoadout` | 120 |
| `AskAS` | 120 |
| `AttentionToDetail` | 120 |
| `AvailableRadarSets` | 120 |
| `BKT#` | 360 |
| `BTL#` | 480 |
| `BaseResources` | 120 |
| `BlockadeAreaName` | 120 |
| `BlockadeModifier` | 120 |
| `Bombastic` | 120 |
| `BudgetModifier` | 120 |
| `BuildAreaName` | 120 |
| `BuildConstraint` | 120 |
| `BuildConstraintTime` | 120 |
| `BuildConstraintType` | 120 |
| `BuildingStrategy` | 120 |
| `CLGH` | 120 |
| `Cautious` | 120 |
| `Corruption` | 120 |
| `Coup` | 120 |
| `DBCS` | 120 |
| `DBS` | 120 |
| `DCAS` | 120 |
| `DCLS` | 120 |
| `DDNumber` | 120 |
| `DPG` | 120 |
| `DamageControl` | 120 |
| `DeckColor` | 120 |
| `DesignIDCount` | 120 |
| `DesignPriority` | 120 |
| `DisplacementLimit` | 120 |
| `DockBuilding` | 120 |
| `DockSize` | 120 |
| `EfficientShipbuildingIndustry` | 120 |
| `Enemy#` | 240 |
| `FAK` | 120 |
| `FBS` | 120 |
| `FLC` | 120 |
| `FileName` | 120 |
| `FlagFileName` | 120 |
| `FlagFileNameC` | 120 |
| `FlagFileNameF` | 120 |
| `FlagFileNameR` | 120 |
| `FlashFires` | 120 |
| `FleetMorale` | 120 |
| `FloatplaneSearchPriority` | 120 |
| `Funds` | 120 |
| `GGP` | 120 |
| `GlobalNavalPower` | 120 |
| `GovernmentChange` | 120 |
| `GovernmentType` | 120 |
| `GunneryTraining` | 120 |
| `Guns#` | 2280 |
| `HAK` | 120 |
| `HFR` | 120 |
| `HFV` | 120 |
| `HadRevolution` | 120 |
| `HasLostWar` | 120 |
| `HasOperationalCV` | 120 |
| `HasOperationalCVX` | 120 |
| `HiddenFlaws` | 120 |
| `IP` | 120 |
| `ImportantAreaName` | 120 |
| `InconsistentNavalPolicy` | 120 |
| `IntelEffort` | 120 |
| `IntelligenceSpending` | 120 |
| `Kamikaze` | 120 |
| `LAK` | 120 |
| `Leader` | 120 |
| `LeaderC` | 120 |
| `LeaderF` | 120 |
| `LeaderR` | 120 |
| `MAK` | 120 |
| `MSNumber` | 120 |
| `MagneticPistols` | 120 |
| `MissileStorage` | 120 |
| `MissileStorageTime` | 120 |
| `MobWarn` | 120 |
| `NSP` | 120 |
| `Name` | 120 |
| `Name#` | 120 |
| `NationNumber` | 120 |
| `NavalAcademy` | 120 |
| `NightFighting` | 120 |
| `OAK` | 120 |
| `OPN` | 120 |
| `OfficerRankAbbreviation#` | 600 |
| `OfficerRankName#` | 600 |
| `OxygenTorpedoesCX` | 120 |
| `OxygenTorpedoesDD` | 120 |
| `OxygenTorpedoesXX` | 120 |
| `PAL#` | 720 |
| `ParliamentName` | 120 |
| `PendingDamageControl` | 120 |
| `PendingGunneryTraining` | 120 |
| `PendingMissileStorage` | 120 |
| `PendingNightFighting` | 120 |
| `PendingTorpedoWarfare` | 120 |
| `PendingTrainingTime` | 120 |
| `PilotTraining` | 120 |
| `PoorEducation` | 120 |
| `PopSub` | 120 |
| `Prestige` | 120 |
| `RGP#` | 240 |
| `Research#Advantage` | 2760 |
| `Research#CurrentLevel` | 2760 |
| `Research#Level#` | 99360 |
| `Research#Prio` | 2760 |
| `Research#ResearchPoints` | 2760 |
| `Research#TSL` | 2760 |
| `ResearchPct` | 120 |
| `SAK` | 120 |
| `SAT` | 120 |
| `SHAAQ` | 120 |
| `SMA` | 120 |
| `SMD` | 120 |
| `SMX` | 120 |
| `SMY` | 120 |
| `SPoss#` | 720 |
| `ShipCount` | 120 |
| `ShipPrefix` | 120 |
| `StartPossessions` | 120 |
| `SubNumber` | 120 |
| `SubmarinePolicy` | 120 |
| `SurpriseAttack` | 120 |
| `TechLeakRisk` | 120 |
| `TechSharing` | 120 |
| `TechnicalExcellence` | 120 |
| `Tension` | 120 |
| `TorpedoWarfare` | 120 |
| `TreatyTonnageFactor` | 120 |
| `TreatyTonnageLimit` | 120 |
| `TroubleRegion` | 120 |
| `TurretStyle` | 120 |
| `UndevelopedShipbuildingIndustry` | 120 |
| `UnrestLevel` | 120 |
| `UnrestWarning` | 120 |
| `UseDivingMissiles` | 120 |
| `UseDivingShells` | 120 |
| `UseMissileTorps` | 120 |
| `UseSHAA` | 120 |
| `UseScoutForce` | 120 |
| `VP` | 120 |
| `Wars` | 120 |
| `WillGoToWar` | 120 |

### `[Objectives]`

| Field pattern | Occurrences |
|---|---:|
| `Objective#EndGame` | 3 |
| `Objective#Force` | 3 |
| `Objective#Goal` | 3 |
| `Objective#Location` | 3 |
| `Objective#Number` | 3 |
| `Objective#PointValue` | 3 |
| `Objective#ShipType` | 3 |
| `Objective#Side` | 3 |
| `Objective#Status` | 3 |
| `Objective#VisibleToEnemy` | 3 |

### `[Officers]`

| Field pattern | Occurrences |
|---|---:|
| `Officer#Ability` | 4846 |
| `Officer#AbilityKnown` | 4846 |
| `Officer#BattleStars` | 4846 |
| `Officer#Fate` | 4846 |
| `Officer#Id` | 4846 |
| `Officer#Name` | 4846 |
| `Officer#Rank` | 4846 |
| `Officer#Special` | 4846 |
| `Officer#Special#` | 4846 |
| `Officer#Status` | 4846 |
| `Officer#YearsInRank` | 4846 |
| `OfficerNo` | 14 |

### `[RAD]`

| Field pattern | Occurrences |
|---|---:|
| `RAD#` | 299 |

### `[Reports]`

| Field pattern | Occurrences |
|---|---:|
| `Report#B` | 71 |
| `Report#BB` | 71 |
| `Report#BC` | 71 |
| `Report#CA` | 71 |
| `Report#CL` | 71 |
| `Report#Course` | 71 |
| `Report#DD` | 71 |
| `Report#Delay` | 71 |
| `Report#Location` | 71 |
| `Report#MinuteStamp` | 71 |
| `Report#OriginatorAsText` | 71 |
| `Report#Side` | 71 |
| `Report#TR` | 71 |
| `Report#Text` | 71 |
| `Report#Time#` | 71 |
| `Report#TimeH` | 71 |
| `Report#TimeM` | 71 |

### `[Side#]`

| Field pattern | Occurrences |
|---|---:|
| `AlternateChance` | 20 |
| `FirstSighting` | 20 |
| `FlagFile` | 20 |
| `GTES` | 20 |
| `LandCAPdivName` | 20 |
| `Name` | 20 |
| `OD` | 20 |
| `ScenarioAccuracy` | 20 |
| `UnspecName` | 20 |

### `[Sides]`

| Field pattern | Occurrences |
|---|---:|
| `PlayerSide` | 10 |

### `[Submarines]`

| Field pattern | Occurrences |
|---|---:|
| `Submarine#Availability` | 9 |
| `Submarine#Downtime` | 9 |
| `Submarine#Fate` | 9 |
| `Submarine#Location` | 9 |
| `Submarine#Name` | 9 |
| `Submarine#OriginalLocation` | 9 |
| `Submarine#Reinforcement` | 9 |
| `Submarine#Side` | 9 |
| `Submarine#TorpsFired` | 9 |
| `Submarine#Type` | 9 |

### `[SunkShips]`

| Field pattern | Occurrences |
|---|---:|
| `Ship#AAKills` | 15 |
| `Ship#AirToSurfaceMissiles` | 15 |
| `Ship#AirTorpedoes` | 15 |
| `Ship#Ammo#` | 135 |
| `Ship#AskedCount` | 15 |
| `Ship#BombHits` | 15 |
| `Ship#BombTarget` | 15 |
| `Ship#Bulkhead` | 15 |
| `Ship#Classname` | 15 |
| `Ship#Commander` | 15 |
| `Ship#Course` | 15 |
| `Ship#CrewQuality` | 15 |
| `Ship#CurrentASWValue` | 15 |
| `Ship#CurrentEndurance` | 15 |
| `Ship#CurrentFCPositions` | 15 |
| `Ship#CurrentFloatPoints` | 15 |
| `Ship#CurrentSecondariesPort` | 15 |
| `Ship#CurrentSecondariesStarboard` | 15 |
| `Ship#CurrentSpeed` | 15 |
| `Ship#CurrentSuperstructurePoints` | 15 |
| `Ship#CurrentTertiariesPort` | 15 |
| `Ship#CurrentTertiariesStarboard` | 15 |
| `Ship#DesignId` | 15 |
| `Ship#ElectricDisabled` | 15 |
| `Ship#EngineDamage` | 15 |
| `Ship#EngineDisabled` | 15 |
| `Ship#FCRadarClass` | 15 |
| `Ship#FT` | 15 |
| `Ship#FireLevel` | 15 |
| `Ship#FireTrend` | 15 |
| `Ship#FlightActivity` | 15 |
| `Ship#Flooding` | 15 |
| `Ship#GrateFoulLevel` | 15 |
| `Ship#HVU` | 15 |
| `Ship#HeavyHits` | 15 |
| `Ship#HitCount` | 15 |
| `Ship#Hits#` | 521 |
| `Ship#HitsScored#` | 45 |
| `Ship#Id` | 15 |
| `Ship#InitialAmmo#` | 45 |
| `Ship#InitialDivision` | 15 |
| `Ship#LL` | 15 |
| `Ship#LightHits` | 15 |
| `Ship#Locked` | 15 |
| `Ship#MediumHits` | 15 |
| `Ship#Mines` | 15 |
| `Ship#MissileHits` | 15 |
| `Ship#Mount#Destroyed` | 22 |
| `Ship#Mount#ReloadTime` | 22 |
| `Ship#Mount#Reloads` | 22 |
| `Ship#Mount#TorpsLeft` | 22 |
| `Ship#Name` | 15 |
| `Ship#Nation` | 15 |
| `Ship#NoRecovery` | 15 |
| `Ship#Nolaunch` | 15 |
| `Ship#ObsoleteDate` | 15 |
| `Ship#OrderedCourse` | 15 |
| `Ship#OrderedSpeed` | 15 |
| `Ship#OrderedStrikeDelay` | 15 |
| `Ship#OriginalEndurance` | 15 |
| `Ship#PF` | 15 |
| `Ship#RadarSightingLevel` | 15 |
| `Ship#RefitOverdue` | 15 |
| `Ship#RoundsFired#` | 45 |
| `Ship#RoundsFiredAtMeLastTurn` | 15 |
| `Ship#RudderStatus` | 15 |
| `Ship#SAF` | 15 |
| `Ship#SSMHitsScored` | 15 |
| `Ship#SearchRadarClass` | 15 |
| `Ship#Side` | 15 |
| `Ship#SightingLevel` | 15 |
| `Ship#Sinking` | 15 |
| `Ship#SmokeFloats` | 15 |
| `Ship#Speed` | 15 |
| `Ship#Sunk` | 15 |
| `Ship#Surprised` | 15 |
| `Ship#Survivors` | 15 |
| `Ship#TimeToRaiseSteam` | 15 |
| `Ship#TorpedoHits` | 15 |
| `Ship#TorpedoHitsScored` | 15 |
| `Ship#Turret#Ammo#` | 186 |
| `Ship#Turret#Destroyed` | 62 |
| `Ship#Turret#Silenced` | 62 |
| `Ship#Warned#` | 60 |
| `Ship#Warned#AA` | 15 |
| `Ship#WarnedForFuelPercentage#` | 30 |
| `Ship#WarnedOut` | 15 |
| `ShipCount` | 10 |

### `[VERSION]`

| Field pattern | Occurrences |
|---|---:|
| `GAME VERSION` | 13 |

## Installed template schema families

Installed template keys may overlap campaign field names without sharing meaning.
Geometric and positional design conversion still requires a dedicated format specification.

### `[#]`

`Nation#APShellQuality`, `Nation#Accuracy`, `Nation#DamageControl`, `Nation#FlagFileName`, `Nation#FlashFires`, `Nation#Name`, `Nation#Name#`, `Nation#NightFighting`, `Nation#SmokeFloats`

### `[AP Projectiles #]`

`PicName`

### `[ASW technology #]`

`PicName`

### `[AirFormations]`

`AF#ATRI`, `AF#AircraftDestroyed`, `AF#AircraftNumber`, `AF#AircraftType`, `AF#BombHits`, `AF#CarrierCapable`, `AF#CombinedStrikeSpeed`, `AF#ConfirmTargetLoc`, `AF#Course`, `AF#Damaged#`, `AF#DamagedFlying`, `AF#Disruption`, `AF#Dogleg`, `AF#Experience`, `AF#GroupIndex`, `AF#GuidedBombs`, `AF#HomeBaseScn`, `AF#Id`, `AF#IsFatigued`, `AF#Kills`, `AF#LeadFormationId`, `AF#LoadedNumber`, `AF#Loadout`, `AF#Location`, `AF#LossAirToAirF`, `AF#LossAirToAirO`, `AF#LossHAAFire`, `AF#LossLAAFire`, `AF#LossMAAFire`, `AF#LossOperational`, `AF#LossSAMFire`, `AF#MissileHits`, `AF#Mission`, `AF#Name`, `AF#Nation`, `AF#NightCapable`, `AF#OrderedState`, `AF#ParentFormationId`, `AF#PilotFatigue`, `AF#PriorityTarget`, `AF#Recon`, `AF#RemainingFuel`, `AF#Side`, `AF#StartATRI`, `AF#Status`, `AF#StatusCount`, `AF#TargetLoc`, `AF#TorpedoHits`, `AF#UnitId`, `AFID`, `AFNumber`, `AU#AircraftTypeId`, `ScoutCount`

### `[AircraftTypes]`

`ACTypesNo`, `AT#AvailableAircraft`, `AT#BaseModelYear`, `AT#Bombing`, `AT#Carrier`, `AT#Ceiling`, `AT#Climb`, `AT#CruiseAltitude`, `AT#CruiseSpeed`, `AT#DevelopmentTime`, `AT#Firepower`, `AT#Floatplane`, `AT#HvyBombLoadNumber`, `AT#HvyBombLoadSize`, `AT#HvyEndurance`, `AT#Id`, `AT#LtBombLoadNumber`, `AT#LtBombLoadSize`, `AT#LtEndurance`, `AT#Maneuver`, `AT#Manufacturer`, `AT#MaxFuel`, `AT#MaxSpeed`, `AT#MedBombLoadNumber`, `AT#MedBombLoadSize`, `AT#MedEndurance`, `AT#Missile#`, `AT#Name`, `AT#Nation`, `AT#Obsolete`, `AT#Purpose`, `AT#Radar`, `AT#Reliability`, `AT#ReliabilityKnown`, `AT#Special`, `AT#Torpedo#`, `AT#Toughness`, `AT#ValuesKnown`, `AT#Version`, `AT#Year`

### `[Amphibious operations #]`

`PicName`

### `[Anti aircraft artillery #]`

`PicName`

### `[Anti submarine warfare #]`

`PicName`

### `[Armor]`

`ArmorScheme`, `B`, `BE`, `BU`, `CT`, `D`, `DE`, `PC`, `SEC`, `T`, `TT`

### `[Armour development #]`

`PicName`

### `[Basic Data]`

`GunRangeFactor`, `PenetrationFactor`, `ShipType#`

### `[Comments]`

`Austria-Hungary#`, `China#`, `France#`, `Germany#`, `Great Britain#`, `Italy#`, `Japan#`, `Russia#`, `Soviet Union#`, `Spain#`, `USA#`

### `[Data]`

`AADir`, `ASWMortar`, `ASWValue`, `AccMod`, `Accomodation`, `AddDA`, `AircraftCapacity`, `AllowedTurretPos`, `AluminiumSuperstructure`, `AngledFlightDeck`, `ArmorMod`, `BAChanged`, `BeltCoverage`, `BoxProtection`, `BuildDate`, `BuildYear`, `BuildingNation`, `Bulged`, `CIWS`, `ColonialService`, `Cost`, `DamageControl`, `DeckColor`, `DeckEdgeLifts`, `DeckPark`, `DesignDiscount`, `DesignSpeed`, `Displacement`, `EDL`, `EnemyClassName`, `EnginePriority`, `EnhancedSonar`, `ExtraDC`, `FCPOS`, `FCRadarClass`, `FinalMaintenance`, `Fire control`, `FlightDeck`, `FlightDeckArmor`, `FlightDeckCatapults`, `FloatMod`, `Freeboard`, `Fuel type`, `Hangar`, `HangarSideArmor`, `Helipad`, `HighSpottingPos`, `Hp`, `InclinedBelt`, `JetCapable`, `KGuns`, `LAA`, `MAA`, `MAADir`, `MSG`, `Maintenance`, `Mine capacity`, `MisidentifiedClassName`, `MissileMaintenancePoints`, `Name`, `Nation`, `OBelt`, `OSpeed`, `Obsolete date`, `OriginalSpeed`, `PictureName`, `RPG`, `RPG#`, `RadarLimit`, `Range`, `Ready`, `RofMod`, `RofModSec`, `SC`, `SearchRadarClass`, `SecDir`, `ShipType`, `Speed`, `TopHeavy`, `Torpedo defense`, `TowedArray`, `TurretEra#`, `TurretNation`, `UnitMachinery`, `WeightResult`

### `[Division#]`

`AIControl`, `Base`, `Course`, `DivisionName`, `Force`, `Formation`, `Historical`, `LeadDiv`, `Objective`, `Probability`, `RandomAngle`, `RandomDistance`, `RandomTimeToRaiseSteam`, `Role`, `Ship#AmmoLevel`, `Ship#Classname`, `Ship#Course`, `Ship#CrewQuality`, `Ship#CurrentEndurance`, `Ship#EngineDamage`, `Ship#FCRadarClass`, `Ship#Historical`, `Ship#LL`, `Ship#Mines`, `Ship#Name`, `Ship#Probability`, `Ship#RefitOverdue`, `Ship#SearchRadarClass`, `Ship#TimeToRaiseSteam`, `Shortname`, `Side`, `Speed`, `TimeToRaiseSteam`, `WI`

### `[Environment]`

`AirPriority#`, `Bias`, `BriefingCrossPoint`, `BriefingEnvironmentFile`, `CenterPoint`, `Day`, `DaySightingDistance`, `EnvironmentFile`, `FogBanks`, `Hour`, `LandLayer#`, `Length`, `Minute`, `Month`, `MorningMist`, `NightSightMod`, `NightSightingDistance`, `NoOrdersBS`, `PFStartPoint`, `PlayerStartpos#`, `Precipitation`, `ScenarioAuthor`, `SeaState`, `ShipCount`, `SightMod`, `SightingDistance`, `Size`, `Squalls`, `Variation`, `WindDirection`, `Windspeed`, `Year`

### `[Equipment#]`

`EquipmentFile`, `LocationAngle`, `LocationDistance`, `MT`, `Nominal`, `Pos`, `Reloads`, `Sponsoned`, `Tubes`

### `[Explosive shells #]`

`PicName`

### `[Fire control #]`

`PicName`

### `[Fleet tactics #]`

`PicName`

### `[Force#]`

`AIControl`, `ActivateAlternateOnSighting`, `ActivateOnSighting`, `AltRandomTimeToRaiseSteam`, `AltTimeToRaiseSteam`, `AlternatePoint`, `AlternateWPIndex`, `CapLevel`, `ForceToPreempt`, `Home`, `HomeDistance`, `InterceptRange`, `Kind`, `MainForce`, `Mission`, `Name`, `NightSearch`, `Objective`, `RandomTimeToRaiseSteam`, `ReactionAllowed`, `RepeatSearch`, `SearchDistance`, `SearchInterval`, `SearchLimitLeft`, `SearchLimitRight`, `Side`, `StartDate`, `StartPoint`, `TimeToRaiseSteam`, `TwoPhaseSearch`, `WPIndex`, `WS#Waypoint#LL`

### `[Funnels]`

`Funnel#Angle`, `Funnel#Distance`, `Funnel#Oval`, `Funnel#Pos`

### `[Guns]`

`Auto#`, `CDF`, `DP#`, `IE`, `MQ`, `Main`, `SQ`, `SecNo`, `SecTF`, `Secondary`, `TQ`, `TerNo`, `TerTF`, `Tertiary`, `TurretStyle`

### `[Hull construction #]`

`PicName`

### `[HullPoints]`

`HullPoint#Angle`, `HullPoint#Distance`

### `[Icon#]`

`IsLine`, `Point#Angle`, `Point#Distance`

### `[Light forces and torpedo warfare #]`

`PicName`

### `[Locations]`

`Location#BaseGroup`, `Location#BaseValue`, `Location#Capacity`, `Location#EnterPortRange`, `Location#EntryPoint`, `Location#ExitNavPoint`, `Location#ForceStartPoint`, `Location#LabelOnly`, `Location#Location`, `Location#Name`, `Location#Nation`, `Location#OpLossDist`, `Location#Size`, `Location#SubmarineBase`

### `[Machinery development #]`

`PicName`

### `[MapArea#]`

`MapArea#AdjacentArea#LP#`, `MapArea#AdjacentAreaNames#`, `MapArea#Climate`, `MapArea#IP#`, `MapArea#LR`, `MapArea#Name`, `MapArea#Possession#BaseENP#`, `MapArea#Possession#BaseEP#`, `MapArea#Possession#BaseLocs#`, `MapArea#Possession#BaseNP#`, `MapArea#Possession#BaseNames#`, `MapArea#Possession#BaseSizes#`, `MapArea#Possession#BaseValue`, `MapArea#Possession#CADirections#`, `MapArea#Possession#CAPositions#`, `MapArea#Possession#Location`, `MapArea#Possession#Name`, `MapArea#Possession#NaturalOwnerName`, `MapArea#Possession#Oil`, `MapArea#Possession#Owner`, `MapArea#Possession#Value`, `MapArea#Possession#WM#AttackingSide`, `MapArea#Possession#WM#BDR`, `MapArea#Possession#WM#BattleSize`, `MapArea#Possession#WM#CarrierStartPoints#`, `MapArea#Possession#WM#CenterPoint`, `MapArea#Possession#WM#Colonies`, `MapArea#Possession#WM#CruiserPatrolPoints#`, `MapArea#Possession#WM#DeclinePenalty`, `MapArea#Possession#WM#DefenderSurprised`, `MapArea#Possession#WM#Destroyers`, `MapArea#Possession#WM#FirstYear`, `MapArea#Possession#WM#HomePoints#`, `MapArea#Possession#WM#LastYear`, `MapArea#Possession#WM#LocalBaseExitNavPoint#`, `MapArea#Possession#WM#LocalBaseLocation#`, `MapArea#Possession#WM#LocalBaseName#`, `MapArea#Possession#WM#Location`, `MapArea#Possession#WM#MaxShipType`, `MapArea#Possession#WM#MeetAtCenterPoint`, `MapArea#Possession#WM#MerchantShipPoints#`, `MapArea#Possession#WM#ObjectiveType#`, `MapArea#Possession#WM#ObjectiveValue#`, `MapArea#Possession#WM#Objectives#`, `MapArea#Possession#WM#ObjectivesB#`, `MapArea#Possession#WM#PatrolWaypoints#`, `MapArea#Possession#WM#StartPoints#`, `MapArea#Possession#WM#StartpointRndDir#`, `MapArea#Possession#WM#StartpointRndDist#`, `MapArea#Possession#WM#SubmarinePoints#`, `MapArea#Possession#WM#Title`, `MapArea#Possession#WM#WaypointLL`, `MapArea#Possession#WM#WaypointRndDir`, `MapArea#Possession#WM#WaypointRndDist`, `MapArea#Possession#WM#WeatherZone`, `MapArea#Possession#WeatherZone`, `MapArea#PossessionCount`, `MapArea#SensitiveName`, `MapArea#TP`, `MapArea#UL`

### `[MapAreas]`

`MapArea#AdjacentArea#LP#`, `MapArea#AdjacentAreaNames#`, `MapArea#Climate`, `MapArea#IP#`, `MapArea#LR`, `MapArea#MineLevel#`, `MapArea#Name`, `MapArea#Possession#BaseENP#`, `MapArea#Possession#BaseLocs#`, `MapArea#Possession#BaseNames#`, `MapArea#Possession#BaseSizes#`, `MapArea#Possession#BaseValue`, `MapArea#Possession#BuildingBase`, `MapArea#Possession#CADirections#`, `MapArea#Possession#CAPositions#`, `MapArea#Possession#Invaded`, `MapArea#Possession#InvasionSupport`, `MapArea#Possession#Location`, `MapArea#Possession#Name`, `MapArea#Possession#NaturalOwnerName`, `MapArea#Possession#Oil`, `MapArea#Possession#Owner`, `MapArea#Possession#Rebellion`, `MapArea#Possession#TakenFrom`, `MapArea#Possession#Value`, `MapArea#Possession#WM#BattleSize`, `MapArea#Possession#WM#CenterPoint`, `MapArea#Possession#WM#CruiserPatrolPoints#`, `MapArea#Possession#WM#DeclinePenalty`, `MapArea#Possession#WM#DefenderSurprised`, `MapArea#Possession#WM#Destroyers`, `MapArea#Possession#WM#HomePoints#`, `MapArea#Possession#WM#LocalBaseExitNavPoint#`, `MapArea#Possession#WM#LocalBaseLocation#`, `MapArea#Possession#WM#LocalBaseName#`, `MapArea#Possession#WM#Location`, `MapArea#Possession#WM#MaxShipType`, `MapArea#Possession#WM#MeetAtCenterPoint`, `MapArea#Possession#WM#MerchantShipPoints#`, `MapArea#Possession#WM#ObjectiveType#`, `MapArea#Possession#WM#ObjectiveValue#`, `MapArea#Possession#WM#Objectives#`, `MapArea#Possession#WM#PatrolWaypoints#`, `MapArea#Possession#WM#StartPoints#`, `MapArea#Possession#WM#StartpointRndDir#`, `MapArea#Possession#WM#StartpointRndDist#`, `MapArea#Possession#WM#SubmarinePoints#`, `MapArea#Possession#WM#Title`, `MapArea#Possession#WM#WaypointLL`, `MapArea#Possession#WM#WaypointRndDir`, `MapArea#Possession#WM#WaypointRndDist`, `MapArea#Possession#WeatherZone`, `MapArea#PossessionCount`, `MapArea#SensitiveName`, `MapArea#UL`, `MapAreaCount`

### `[Minefields]`

`Minefield#Density`, `Minefield#Point#LL`, `Minefield#RandomAngle`, `Minefield#RandomDistance`, `Minefield#Side`

### `[Missile countermeasures #]`

`PicName`

### `[Missile technology #]`

`PicName`

### `[Nation#CoastalArtillery]`

`CACount`

### `[Nation#Losses]`

`AUXLost`, `BBLost`, `BCLost`, `BLost`, `CALost`, `CLLost`, `CVLLost`, `CVLost`, `DDLost`, `LTLost`, `MSLost`, `SSLost`

### `[Nation#Mission#]`

`AttackingSide`, `BDR`, `BattleSize`, `CarrierStartPoints#`, `CenterPoint`, `Colonies`, `CruiserPatrolPoints#`, `DeclinePenalty`, `DefenderSurprised`, `Destroyers`, `FirstYear`, `HomePoints#`, `LastYear`, `LocalBaseExitNavPoint#`, `LocalBaseLocation#`, `LocalBaseName#`, `Location`, `MaxShipType`, `MeetAtCenterPoint`, `MerchantShipPoints#`, `ObjectiveType#`, `ObjectiveValue#`, `Objectives#`, `ObjectivesB#`, `PatrolWaypoints#`, `StartPoints#`, `StartpointRndDir#`, `StartpointRndDist#`, `SubmarinePoints#`, `Title`, `WaypointLL`, `WaypointRndDir`, `WaypointRndDist`, `WeatherZone`

### `[Nation#Submarines]`

`SubCount`

### `[Nation#]`

`AIAlliance#`, `AITension#`, `APShellPriority`, `Accuracy`, `AdmiralName`, `AdmiralRank`, `AicraftPriority#`, `AirSeaRescue`, `AirUnitName`, `AircraftNumber`, `Alarmed`, `Allied`, `AmmoDoctrine`, `AmmoLoadout`, `AskAS`, `AttentionToDetail`, `Autocracy`, `AvailableRadarSets`, `BKT#`, `BTL#`, `BaseResources`, `BlockadeAreaName`, `BlockadeModifier`, `BlockadeModofier`, `Bombastic`, `BreakoutPoint`, `BreakoutPointRndDir`, `BreakoutPointRndDist`, `BudgetModifier`, `BuildAreaName`, `BuildConstraint`, `BuildConstraintTime`, `BuildConstraintType`, `BuildingStrategy`, `CLGH`, `Cautious`, `Colonies`, `Corruption`, `Coup`, `DBCS`, `DBS`, `DCAS`, `DCLS`, `DDNumber`, `DPG`, `DamageControl`, `DeckColor`, `DesignIDCount`, `DesignPriority`, `DisplacementLimit`, `DockBuilding`, `DockSize`, `EfficientShipbuildingIndustry`, `Enemy#`, `FAK`, `FBS`, `FLC`, `FileName`, `FlagFileName`, `FlagFileName#`, `FlagFileNameC`, `FlagFileNameF`, `FlagFileNameR`, `FlahFires`, `FlashFires`, `FleetMorale`, `FloatplaneSearchPriority`, `Friend`, `Funds`, `GGP`, `GlobalNavalPower`, `GovernmentChange`, `GovernmentType`, `GunneryTraining`, `Guns#`, `HAK`, `HBR`, `HFR`, `HFV`, `HadRevolution`, `HasLostWar`, `HasOperationalCV`, `HasOperationalCVX`, `HiddenFlaws`, `IFM`, `IP`, `ImportantAreaName`, `InconsistentNavalPolicy`, `IntelEffort`, `Intelligence`, `IntelligenceSpending`, `Isolationist`, `Kamikaze`, `LAK`, `Leader`, `Leader#`, `LeaderC`, `LeaderF`, `LeaderR`, `LiberalDemocracy`, `MAK`, `MSNumber`, `MagneticPistols`, `MissileStorage`, `MissileStorageTime`, `MobWarn`, `NSP`, `Name`, `Name#`, `NationName`, `NationNumber`, `NavalAcademy`, `Neutral`, `NightFighting`, `OAK`, `OPN`, `OfficerRankAbbreviation#`, `OfficerRankName#`, `OxygenTorpedoesCX`, `OxygenTorpedoesDD`, `OxygenTorpedoesXX`, `PAL#`, `ParliamentName`, `PendingDamageControl`, `PendingGunneryTraining`, `PendingMissileStorage`, `PendingNightFighting`, `PendingTorpedoWarfare`, `PendingTrainingTime`, `PilotTraining`, `PoorEducation`, `PopSub`, `Possession#`, `Prestige`, `RGP#`, `Research#Advantage`, `Research#CurrentLevel`, `Research#Level#`, `Research#Prio`, `Research#ResearchPoints`, `Research#TSL`, `ResearchPct`, `SAK`, `SAT`, `SHAAQ`, `SMA`, `SMD`, `SMX`, `SMY`, `SPoss#`, `ShipCount`, `ShipDesign`, `ShipPrefix`, `Sigint`, `StartPossessions`, `SubNumber`, `SubmarinePolicy`, `SurpriseAttack`, `TechLeakRisk`, `TechSharing`, `TechnicalExcellence`, `Tension`, `TorpedoDevelopment`, `TorpedoMounts`, `TorpedoWarfare`, `TreatyTonnageFactor`, `TreatyTonnageLimit`, `TroubleRegion`, `TurretStyle`, `UndevelopedShipbuildingIndustry`, `UnrestLevel`, `UnrestWarning`, `UseDivingMissiles`, `UseDivingShells`, `UseMissileTorps`, `UseSHAA`, `UseScoutForce`, `VP`, `Wars`, `WillGoToWar`, `sGovernmentType`

### `[Naval aviation, heavier than air #]`

`PicName`

### `[Naval aviation, lighter than air #]`

`PicName`

### `[Objectives]`

`Objective#AltLoc`, `Objective#EndGame`, `Objective#Force`, `Objective#Goal`, `Objective#IsMandatory`, `Objective#Location`, `Objective#Mandatory`, `Objective#Number`, `Objective#PointValue`, `Objective#ShipType`, `Objective#Side`, `Objective#VisibleToEnemy`

### `[Polygon#]`

`Color`, `IsLine`, `Point#Angle`, `Point#Distance`

### `[Radar and electronics #]`

`PicName`

### `[SearchAreas]`

`SearchArea#Category`, `SearchArea#Point#LL`, `SearchArea#Side`, `SearchArea#SpotChance`, `SearchArea#Title`

### `[SecondaryTurrets]`

`SecondaryTurret#Angle`, `SecondaryTurret#Distance`, `SecondaryTurret#Nominal`, `SecondaryTurret#Pos`, `SecondaryTurret#Used`

### `[Ship design #]`

`PicName`

### `[Shipboard aircraft operation #]`

`PicName`

### `[Side#]`

`AlternatePointChance`, `FlagFile`, `LandCAPdivName`, `Name`, `ScenarioAccuracy`, `UnspecName`

### `[Sponsons]`

`SponsonRadius#`

### `[Subdivision and damage control #]`

`PicName`

### `[Submarines #]`

`PicName`

### `[Submarines]`

`Submarine#Accuracy`, `Submarine#Availability`, `Submarine#Downtime`, `Submarine#InPlay`, `Submarine#Location`, `Submarine#Name`, `Submarine#RandomAngle`, `Submarine#RandomDistance`, `Submarine#Reinforcement`, `Submarine#Side`, `Submarine#SubType`

### `[Superstructure#]`

`Color`, `IsLine`, `Point#Angle`, `Point#Distance`

### `[TertiaryTurrets]`

`TertiaryTurret#Angle`, `TertiaryTurret#Distance`, `TertiaryTurret#Nominal`, `TertiaryTurrets#Used`

### `[Torpedo technology #]`

`PicName`

### `[TorpedoMount#]`

`EquipmentFile`, `LocationAngle`, `LocationDistance`, `MT`, `Nominal`, `Pos`, `Reloads`, `Sponsoned`, `Tubes`

### `[Torpedoes]`

`Calibre`, `Designation`, `TorpedoReloads`

### `[Turret#]`

`Guns`, `LocationAngle`, `LocationDistance`, `Nominal`, `Pos`, `ROFPenalty`, `Sponsoned`

### `[Turrets and gun mountings #]`

`PicName`

### `[Weights]`

`ArmorCost`, `ArmorWeight`, `EngineCost`, `EngineWeight`, `HullCost`, `HullWeight`
