# Privateer

Privateer is a Python 3.11+ application for safely editing Rule the Waves 3 save
folders.  This first release provides a format-preserving core, validation,
transactional fleet transfers (including design cloning/remapping), economy and
technology APIs, deterministic distribution, backups, atomic writes, and a small
Tkinter front end.

See **[INSTALL.md](INSTALL.md)** for complete Windows, macOS, and Linux setup,
launch, validation, testing, updating, and troubleshooting instructions.

Developers and future Codex tasks should begin with the comprehensive
**[project handoff](docs/CODEX_HANDOFF.md)**. It records the intended product,
prototype limitations, observed real-save failure, required artifacts, correction
sequence, acceptance gates, and regression matrix.

Because RTW3 formats have varied, Privateer deliberately accepts only structures
it can identify. It recognizes `NationN`, `NationNShipM` (or `ShipM` carrying an
owner field), and `ShipDesignM` sections. Key/value separators, comments, unknown
fields, ordering, encoding, and line endings are retained.

```bash
python -m privateer                  # GUI
python -m privateer /path/to/Game7 --validate
pytest
```

Always test output in a copied game slot. `save()` creates a timestamped sibling
backup; `save_as()` preserves every unknown save-slot file.
