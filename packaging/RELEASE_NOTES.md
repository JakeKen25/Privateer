# Privateer 0.9.10

This release adds submarine spawning and management to the features in 0.9.9.1.

## Submarine Manager

- Spawn completed coastal, standard, minelaying, long-range and missile submarines using built-in reference data. No existing submarine or Game6 save is required.
- Choose Submarine Type and a destination home/service location. Editable names default to the next available Privateer number.
- Right-click to Rename, Delete or Repair. Repair sets Availability to 135 without changing other state.
- Spawn and right-click actions remain pending until Apply. Cancel discards the pending changes; Save or Save As writes accepted changes to disk.
- Removed the Submarine Manager (WIP) label. One minelayer choice uses Accuracy=0.

## User guide

The wiki is the primary end-user manual. Manager pages now describe the current released controls and workflows, without development logs or superseded instructions. Existing screenshots are retained.

## Notes

Submarine reference stats are fixed rather than scaled to campaign technology or year. Submarine transfers are unavailable. Aircraft creation still needs further in-game validation. The budget calculator remains an estimate with a +/-10% monthly-balance planning range; its underlying calculations remain under review.

30 targeted submarine/version tests and GUI Apply/Cancel checks passed during preparation of the submarine features.

## Installation

Download Privateer-0.9.10-Windows-x64.zip, extract the complete folder, and run Privateer.exe. Keep the runtime folder beside it. Python is not required. Close RTW3 before saving campaign edits and keep a known-good backup.
