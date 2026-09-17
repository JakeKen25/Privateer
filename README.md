# Privateer

**Version 0.931 Beta**

Privateer is a save editor for **Rule the Waves 3**. It turns many manual,
error-prone save-file edits into guided tools so players can spend less time
decoding files and more time experimenting with campaigns. Try a different
technology path, adjust a nation's resources, transfer ships between nations, or
set up an unusual alternate-history scenario without editing dozens of raw
records by hand.

Privateer is an unofficial community project and is not affiliated with the
developers or publisher of Rule the Waves 3. The core software was written with
**ChatGPT Codex**, guided by human research, examples, testing, and design
decisions. Contributions from experienced programmers and modders are highly
welcome for future updates. I still have a lot to learn about the game's file
formats, and independent review and new discoveries will make the editor safer
and more capable.

## Major features

- **Transfer Ships** moves complete ships between nations. The transfer keeps
  the hull's permanent identity, original building nation, construction state,
  equipment, crew data, history, and fields Privateer does not yet understand.
  It also copies and remaps the associated design record into the receiving
  nation's design library.
- **Technology Manager** presents each technology area as a level slider. Moving
  a slider to a level includes all earlier levels and displays the selected
  technology's effect and typical year when that information is available.
- **Caliber Manager** provides the available quality setting for each supported
  gun caliber.
- **Economy and Unrest Manager** edits funds, base resources, and unrest together and shows an
  estimated in-game budget breakdown as values change. Further refinement is
  still needed to ensure that the editor's calculator matches in-game statistics.
- **Infrastructure and Fortifications Manager** edits national dockyard size. Fortification editing
  is still under development but is planned for a future release.
- **Relationship Manager** edits the tension level between nations. This area is
  still under development while alliances and wars are researched.
- **Colony Manager** identifies colonies by their named map regions and changes
  ownership through the campaign's `MapDataX.dat` file. National home regions
  are identified and locked against transfer.
- **Admiral Manager** changes the player admiral's name and prestige. It is
  available only for Nation0, which RTW3 uses as the player nation.
- **Aircraft Manager** creates aircraft models for a selected nation. Choose a
  type, set a manufacturer and name, and edit performance, armament, carrier
  capability, and available stock. The form uses the campaign year and starts
  with Game 6 averages for that aircraft type and year.
- **Validation, backups, and Save As** help protect campaigns. Backups are
  enabled by default, their destination is configurable, and settings persist
  between sessions.
- **Sortable tables and progress windows** make larger saves easier to browse
  and show when loading, validation, or saving is still in progress.

Ship Spawner remains a work-in-progress placeholder.

## Ship transfers

Ship transfer is one of Privateer's central features and is not covered by most
editing or modding guides. The transfer window lists type, name, class,
displacement, speed, main gun caliber, radar, ASW value, build year, location,
status, crew quality, maintenance, and armament. Every column can be sorted in
either direction, and the fleet can be filtered without repeatedly rescanning the
raw save data.

When a ship moves, Privateer transfers its complete ship-instance record and
copies the referenced design into the destination nation's `DesignFilesN.des`.
It assigns a valid destination-local design ID and updates the ship's design
reference while leaving the donor design intact. `BuildingNationIdx` is preserved,
so a transferred ship continues to show the nation that originally built it.

Transfers involving aircraft carriers are currently blocked because their air
groups have linked records that are not fully decoded. Transfers involving the
player are also blocked while active campaign divisions are present. These
restrictions prevent Privateer from silently producing incomplete save data.
See [the ship-transfer guide](guides/SHIPS.md) for the technical behavior and
known limits.

## Installing and running

Windows users can download `Privateer-<version>-Windows-x64.zip` from the GitHub
Releases page. Extract the complete folder and run `Privateer.exe`; a separate
Python installation is not required. The archive includes its own `INSTALL.txt`
with first-use, update, and uninstall instructions.

Close Rule the Waves 3 before editing a campaign. Select the complete `GameX`
save-slot folder, validate it, and use **Save As** for the first game-level test.
Keep a known-good backup even when using Privateer's automatic backup feature.

See [INSTALL.md](INSTALL.md) for complete Windows instructions, developer setup,
validation, updating, and troubleshooting.

## Python project

Privateer is implemented in Python 3.11+ with a Tkinter desktop interface. The
source preserves key/value separators, comments, unknown fields, ordering,
encoding, byte-order marks, and line endings wherever the supported save format
allows it. For the supplied RTW3 1.01.44 saves, it recognizes `NationN`, flattened
`NationNShips` rosters, positional `v10139` design libraries, and the associated
map and campaign data used by the current managers.

From a developer checkout:

```powershell
python -m privateer
python -m privateer "C:\Users\<name>\Documents\My Games\Rule the Waves 3\Save\Game7" --validate
python -m pytest
```

The repository retains the complete source, tests, example fixtures, file-format
notes, and Windows packaging tools. Privateer intentionally changes only formats
it can identify and validate; unknown or unresolved structures are preserved or
the affected operation is blocked.

## Contributing

Programmers, testers, and RTW3 file-format researchers are encouraged to
contribute. New format discoveries should include repeatable evidence from test
saves, and code changes should include focused tests for the behavior they add or
correct. Do not commit live campaigns, installed game data, credentials, or other
players' personal files.

Start with [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull
request. The project owner currently retains sole approval, merge, and release
authority.

Development takes place on `develop`. The `main` branch contains tested,
published releases. Create focused `feature/<name>` or `fix/<name>` branches from
`develop` and submit completed work back to `develop`. See
[BRANCHING.md](BRANCHING.md) for the complete release flow.

Version 0.931 Beta corrects aircraft defaults so a year without new designs is
interpolated from the nearest earlier and later yearly averages. The latest data
carries forward after the final observed year, while minimum fallback values
apply only to designs that predate every observed model of that type. Budget
calculations remain estimates, and features identified as under development
still require additional file-format research and in-game validation.
