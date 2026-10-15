# Privateer 1.0.1 Beta

This beta builds on Privateer 1.0 Beta and includes cross-save ship copying and SDF ship import.

- Ship Spawner offers **Copy from another save** and **Import from SDF file**. Built-in designs are not available and are no longer shown as an option.
- SDF import supports custom and installed design folders, multiple copies, editable shared class names, and editable individual ship names.
- Removed the **(WIP)** marker from the Ship Spawner context-menu item.
- Browse another campaign, select ships from its nations, and stage copies. Apply accepts the batch; Cancel discards it. Save or Save As writes the destination campaign.
- Source saves remain unchanged. Copies receive new hull/design identities and use the receiving nation as their builder, including when the source nation does not exist in the destination.
- Copies retain equipment, crew, history, build year, damage, fleet status and construction progress. They arrive in the receiving nation's home area without commanders or movement orders. Duplicate names get a copy suffix.
- Fixed a table theme callback error.

Carriers and aircraft-capable ships remain unsupported for copying, as do historical losses, scrapped and museum ships. Copied equipment is not scaled to campaign technology or date. SDF import remains experimental across ship types, especially carriers. Back up your campaign before testing.

The budget calculator remains an estimate with a ±10% monthly-balance planning range; underlying calculations are still under review. Aircraft creation still needs further in-game validation.

Ship copying has passed user testing. SDF import is available for broader testing in this prerelease; Privateer 0.9.10 remains the latest stable release.

Download **Privateer-1.0.1-Windows-x64.zip**, extract the complete folder, and run **Privateer.exe**. Python is not required. See the [Ship Spawner guide](https://github.com/JakeKen25/Privateer/wiki/Ship-Spawner).
