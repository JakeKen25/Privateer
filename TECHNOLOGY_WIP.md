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

Validation: six technology unittest cases passed, including cumulative increases,
decreases, no unlocks, maximum level, save/reload, gap preservation, and invalid
inputs. Tk GUI checks passed for 22 sliders, selected-level details, filtering,
Reset, Cancel, Apply, and the gun placeholder. The full pytest suite has not run
because pytest is unavailable in the current runtimes.

Gun validation: three unit tests and GUI checks passed for all quality values,
19 rows, 133 radio buttons, Reset, Apply, Cancel, and byte-preserving save/reload.
