# Technology window (WIP)

Double-click Launch_Privateer.bat (requires Python 3.11+ with Tkinter).
Browse to your save folder, right-click a nation, and choose Manage Technology (WIP).

The window reads Data/ResearchAreas3.dat from the installed Steam game. If absent,
it asks you to locate that file. All 572 definitions in the currently installed
version are searchable and can be filtered by research area.

Each technology uses a 0/1 possession slider because RTW3 saves individual unlocks,
not a continuous national technology level. Clicking or focusing a slider displays
the selected technology's effect and typical base year in the bottom text box.
Missing or invalid save flags remain visible but cannot be edited.

Apply stages changes in memory; Cancel discards dialog changes. Use Save or Save As
in the main window to write changes through the existing backup/validation workflow.
Normal research progress, priorities, spending, gun quality, and undefined levels
are preserved. Gun quality editing and broader presets remain future work.

This project was based on the Downloads copy containing the economy editor, because
the local GitHub checkout had an older interface. Neither source copy nor any live
game save was modified during development.

Validation: new unittest cases pass for parsing, invalid data, atomic rejection,
byte-preserving edits, and save/reload. A Tk smoke test passed for all 572 rows,
filtering, sliders, details, and Apply on the included Game5 save in memory.
The existing pytest suite could not run because pytest is not installed in the
available Python runtimes. In-game behavior has not been verified; this remains WIP.
