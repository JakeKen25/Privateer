# Privateer 1.0.6 Beta

This development build follows Privateer 1.0.5 Beta and adds air-wing management and same-campaign carrier transfers.

- Ship Spawner offers **Copy from another save** and **Import from SDF file**. Built-in designs are not available and are no longer shown as an option.
- SDF import supports custom and installed design folders, multiple copies, editable shared class names, and editable individual ship names.
- Removed the **(WIP)** marker from the Ship Spawner context-menu item.
- Browse another campaign, select ships from its nations, and stage copies. Apply accepts the batch; Cancel discards it. Save or Save As writes the destination campaign.
- Source saves remain unchanged. Copies receive new hull/design identities and use the receiving nation as their builder, including when the source nation does not exist in the destination.
- Copies retain equipment, crew, history, build year, damage, fleet status and construction progress. They arrive in the receiving nation's home area without commanders or movement orders. Duplicate names get a copy suffix.
- Fixed a table theme callback error.
- Added an Air Wing Manager for reviewing a nation's air wings and staging their reassignment to owned aircraft-capable ships.
- Same-campaign ship transfers now move air-wing nation references with carriers while preserving aircraft models, counts, and permanent base IDs.

Cross-save carrier copies remain unsupported because air-wing aircraft model references are not yet remapped. The Air Wing Manager does not yet validate aggregate deck capacity or in-game effects. Historical losses, scrapped and museum ships remain unavailable for transfer. Copied equipment is not scaled to campaign technology or date. SDF import remains experimental across ship types, especially carriers. Back up your campaign before testing.

The budget calculator remains an estimate with a ±10% monthly-balance planning range; underlying calculations are still under review. Aircraft creation still needs further in-game validation.

Ship copying has passed user testing. This Air Wing Manager and same-campaign carrier migration need in-game validation. SDF import is available for broader testing in this prerelease; Privateer 0.9.10 remains the latest stable release.

Download **Privateer-1.0.6-Windows-x64.zip**, extract the complete folder, and run **Privateer.exe**. Python is not required. See the [Ship Spawner guide](https://github.com/JakeKen25/Privateer/wiki/Ship-Spawner) and [Air Wing Manager guide](https://github.com/JakeKen25/Privateer/wiki/Air-Wing-Manager).
