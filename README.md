# Privateer

**Version 0.9.0 (beta)**

Privateer is a Python 3.11+ prototype for safely inspecting Rule the Waves 3 save
folders. It currently parses real flattened ship rosters and positional v10139
design libraries, validates ship/design references, and provides a Tkinter front
end. Its ship-transfer manager moves complete hull records transactionally, copies
the referenced design into each receiving nation's library, and preserves permanent
hull IDs, original building nations, and opaque ship/design data.

See **[INSTALL.md](INSTALL.md)** for complete Windows, macOS, and Linux setup,
launch, validation, testing, updating, and troubleshooting instructions.

End users should download `Privateer-<version>-Windows-x64.zip` from the GitHub
Releases page, extract the complete folder, and run `Privateer.exe`; Python is not
required. The archive includes `INSTALL.txt` with setup, first-use, update, and
uninstall instructions. Developers should clone the repository to retain the full
source, tests, fixtures, technical documentation, and packaging tools.

Because RTW3 formats have varied, Privateer deliberately accepts only structures
it can identify. For supplied RTW3 1.01.44 saves it recognizes `NationN`,
flattened `NationNShips` rosters, and positional `v10139` design libraries.
Key/value separators, comments, unknown fields, ordering, encoding, BOM state,
and line endings are retained.

```bash
python -m privateer                  # GUI
python -m privateer /path/to/Game7 --validate
pytest
```

Version 0.9.0 is the basic-feature beta. Treat the application as pre-release
software and test output only in a copied
game slot. `save()` creates a retained backup by default; Settings can relocate or
disable retained backups. `save_as()` preserves every unknown save-slot file.

The Settings button in the lower-right corner controls backup creation and location.
Preferences persist in the user's application-data directory. All header-based
tables support ascending and descending sorting by clicking a column heading.

The nation context menu includes **Economy Manager**, a combined editor for Funds and Base
Resources, with a live budget projection based on the verified Game1 relationships.
The infrastructure manager edits dockyard size and includes a disabled fortification
placeholder. Admiral Manager edits the Nation0 player's name and prestige and is
hidden for every other nation. Ship Spawner remains a WIP placeholder. See
**[ECONOMY.md](ECONOMY.md)** for the calculator's verified inputs and limitations.

Ship transfers support the confirmed flattened roster and positional `v10139`
design formats. Transfers involving carrier air groups or active campaign divisions
are blocked until those linked structures are decoded and validated.

Animated progress windows remain visible while Privateer loads, validates, saves,
or creates a save copy. Management-window launches use the same progress treatment.
Flattened ship fields are indexed once during save loading and reused by the fleet
table, including filtering and sorting, instead of rescanning the full roster for
every displayed hull.
