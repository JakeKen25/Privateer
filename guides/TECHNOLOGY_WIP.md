# Technology and gun caliber windows

Run Launch_Privateer.bat or the installed Privateer launcher. Load a save,
right-click a nation, and choose Technology Manager.

Each research area has one cumulative slider. Displayed levels run from 1 through
that area's highest defined technology; 0 means none. Selecting level 5 enables
levels 1-5 and disables higher defined levels. Display levels are one-based;
the underlying save's ResearchXLevelY identifiers remain zero-based.

The window reads the installed Data/ResearchAreas3.dat (or asks you to locate it).
The current installation defines 22 areas and 572 technologies. Search matches
area names and the technologies within them. Selecting a slider shows its current
technology's name, effect, and typical base year in the bottom text box.

Existing unlock gaps are marked and preserved until that area's slider changes.
Select an area to see its individual technologies in the right-hand checklist.
Uncheck any level to skip it without disabling later levels; check it again to
restore it. Click a technology's name for its effect and typical unlock year.
The slider displays the highest enabled level and marks gaps. Moving it applies
a fresh cumulative selection, replacing any checkbox exceptions in that area.
Missing or invalid save fields disable the corresponding area slider. Reset changes
restores the original state; Cancel discards all dialog edits. Apply stages the
changes in memory. Use Save or Save As to write through the existing validation
and backup workflow. Unknown fields, unused level slots, other nations, research
spending, priorities, progress, and gun values are preserved.

Caliber Manager opens a separate window with rows for 2-inch through 20-inch
guns and one radio button per quality: -3, -2, -1, 0, +1, +2, and Unavailable.
Unavailable corresponds to the game's sentinel value 9. Selecting a quality makes
that caliber available. Missing or unknown gun fields are visible but disabled.
Reset and Cancel discard staged gun changes; Apply stages them in the loaded save.
Only explicitly changed GunsN values are written, preserving research and other
nations. Existing ships are not automatically rebuilt.

Validation covers cumulative selection, individual exceptions, reset, invalid
inputs, and save/reload preservation of intermediate gaps. Tk checks also cover
slider/checkbox synchronization and filtering without changing staged flags.

Gun validation: three unit tests and GUI checks passed for all quality values,
19 rows, 133 radio buttons, Reset, Apply, Cancel, and byte-preserving save/reload.
