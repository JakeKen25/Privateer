# Privateer

Privateer is a Python 3.11+ prototype for safely inspecting Rule the Waves 3 save
folders. It currently parses real flattened ship rosters and positional v10139
design libraries, validates ship/design references, and provides a small Tkinter
front end. Real-format fleet transfers and design cloning remain deliberately
disabled until their complete serialization path is proven safe.

See **[INSTALL.md](INSTALL.md)** for complete Windows, macOS, and Linux setup,
launch, validation, testing, updating, and troubleshooting instructions.

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

Treat the application as pre-release software and test output only in a copied
game slot. `save()` creates a timestamped sibling backup; `save_as()` preserves
every unknown save-slot file.
