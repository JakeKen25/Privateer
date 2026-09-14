# Relations manager (under development)

Right-click a nation and choose Relationship Manager. The window shows its eight
relationships in the verified player-slot-0 / AI-slots-1-through-8 layout. Names
come from the loaded save; NationNumber is never used as an array suffix. Extra
stored nation records are excluded, regardless of their name or ship count.

Enter integer values only for pairs you want to change. Player pairs update the
other nation's scalar Tension; AI pairs update both reciprocal AITension fields.
The basic editor accepts 0-20 as a conservative editor guardrail, not a claimed
engine range or war threshold. Values outside this range remain visible/read-only.
Asymmetric pairs show both originals and are only synchronized by an explicit edit.
Details show exact source fields and read-only alliance values without assigning
unverified strength or duration meanings. Self-relations cannot be edited.

Reset clears the entries. Cancel discards dialog edits. Apply stages the complete
validated batch in memory. Save/Save As use the existing validation and temporary
write workflow; Save follows the configured retained-backup policy. Tension edits additionally check
that source files have not changed since loading and before replacing the save.
Written document bytes are compared against the prepared in-memory payload. Audit
logs are retained in the saved folder. This does not lock RTW3 against concurrent
writes; close the game before saving edits.

Scope: ordinary numerical tensions. War creation, add-enemy, forced peace, alliance
editing, treaties, and territory changes are not implemented here. Raw player
Tension=50 with General/War=1 is labeled as matching the documented wartime pattern,
not as a universal engine status decoder. Existing war and alliance values are
preserved. Unsupported layouts and missing/duplicate target fields fail explicitly.

Reference: user-supplied RTW3_Diplomacy_Codex_Reference_Package.zip, dated September
12, 2026. Base Tensions provides the mapping; Verified Add Enemy and Alliance Final
Findings supersede earlier experiments. Their evidence concerns RTW3 1.01.44.
No game data or personal saves are distributed with this implementation.

Validation: six diplomacy tests cover dynamic names, target selection, reciprocal
edits, ambiguity rejection, no-op preservation, backup/reload, and source conflicts.
The six technology and three gun tests also pass, along with all three GUI smoke
checks. No new in-game turn-progression test has been performed.

Opening Relationship Manager displays an under-development warning. Numeric columns
are labeled Current Tension Level and New Tension Level.
