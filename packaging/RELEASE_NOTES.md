# Privateer 0.9.10.2 Beta

This beta adds cross-save ship copying to Privateer 0.9.10.

- Ship Spawner offers **Copy from another save** and **Use built-in designs**. Built-in designs are not available yet.
- Browse another campaign, select ships from its nations, and stage copies. Apply accepts the batch; Cancel discards it. Save or Save As writes the destination campaign.
- Source saves remain unchanged. Copies receive new hull/design identities and use the receiving nation as their builder, including when the source nation does not exist in the destination.
- Copies retain equipment, crew, history, build year, damage, fleet status and construction progress. They arrive in the receiving nation's home area without commanders or movement orders. Duplicate names get a copy suffix.
- Fixed a table theme callback error.

Carriers and aircraft-capable ships remain unsupported, as do historical losses, scrapped and museum ships. Copied equipment is not scaled to campaign technology or date. Built-in designs are disabled. Back up your campaign before testing.

The budget calculator remains an estimate with a ±10% monthly-balance planning range; underlying calculations are still under review. Aircraft creation still needs further in-game validation.

The ship-copy workflow has passed targeted automated checks and user testing. This is a prerelease for broader testing; Privateer 0.9.10 remains the latest stable release.

Download **Privateer-0.9.10.2-Windows-x64.zip**, extract the complete folder, and run **Privateer.exe**. Python is not required. See the [Ship Spawner guide](https://github.com/JakeKen25/Privateer/wiki/Ship-Spawner).
