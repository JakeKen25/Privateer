# Privateer 0.9.9

This release brings the changes developed since 0.9.8 into the published Windows build. The [user wiki](https://github.com/JakeKen25/Privateer/wiki) now documents 0.9.9.

## Added and improved

- **Dark mode:** enable it in Settings and Apply. It updates immediately and persists between launches, including manager controls and striped tables. Windows-owned dialogs and title bars may follow the system theme.
- **Relationship Manager:** Create Alliance, Break Treaty, Reset Tension to 0, Start War, and Ceasefire; a shared nation-by-nation matrix with War/Allied indicators and row/column striping; a compact 960 � 780 default window. Removed the old disclaimer and raw relationship-detail panel. War-budget changes remain outside scope.
- **Technology Manager:** alternating row colors and selection radio buttons synchronized with sliders and the selected research area.
- **Colony Manager:** ordinary possessions can transfer even inside a nation's home map area. Individual home provinces with saved Value at least 200 remain protected.
- **Transfer Ships:** corrected Reserve Fleet, Trade Protection, and Raider status labels, with museum/lifecycle safeguards. Original builder nation remains part of the ship's history.
- **Aircraft Manager:** opens even when the campaign has no aircraft models. The empty list says "No aircraft are detected in this save" and players can create the first model using built-in defaults, then save normally. Existing models remain available as templates. Creating a model does not create squadrons or unlock aviation technology.
- **Submarine Manager (WIP):** clarified the menu label; the existing searchable inventory remains read-only.
- **Economy and Unrest Manager:** removed the bottom information/disclaimer panel and Estimate assumptions dialog. Default calculations remain unchanged.
- Updated user guides, technical documentation, repository organization, and wiki maintenance instructions.

## Budget accuracy and remaining limits

**The budget calculator still presents a �10% monthly-balance planning range alongside its central estimate. Its base calculations remain under review.** The range is not a validated confidence interval; the game may fall outside it.

Aircraft creation, including first-model creation and early campaigns, still needs in-game validation. Supported war/alliance workflows and fortification edits have user-confirmed validation. AI-only war actions and multi-opponent ceasefires are unsupported. Carrier/air-group transfers remain blocked. Submarine editing, Ship Spawner, and custom-nation creation are not included.

## Validation

153 automated tests passed before release preparation. Additional Tk checks covered dark/light switching, persistent preferences, matrix layout, and opening/applying aircraft creation in an empty synthetic campaign. These checks do not replace in-game aircraft validation.

## Installation

Download **Privateer-0.9.9-Windows-x64.zip**, extract the entire archive, and run **Privateer.exe**. Keep the accompanying runtime folder beside the executable. Python is not required. Close RTW3 before saving edits and retain a known-good campaign backup.
