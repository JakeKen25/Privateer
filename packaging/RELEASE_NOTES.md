# Privateer 0.91

Privateer 0.91 is the first stable release of the Rule the Waves 3 save editor.
It provides a Windows desktop interface for common save edits, reduces the need
to alter raw campaign files by hand, and includes validation and backup tools for
safer experimentation.

## Available in this release

- Transfer complete ships between nations while preserving permanent hull IDs,
  original building nations, construction state, equipment, crew data, history,
  and unknown fields. Privateer copies and remaps the associated design into the
  receiving nation's design library.
- Review ship type, class, displacement, speed, armament, radar, ASW, build year,
  location, status, crew quality, and maintenance in a sortable transfer table.
- Adjust technology areas with cumulative level sliders and review the selected
  technology's effect and typical unlock year when available.
- Manage gun-caliber quality, national funds and resources, dockyard size,
  diplomatic tension, colony ownership, and the player admiral's name and
  prestige.
- Validate saves before writing, create backups by default, choose a custom
  backup location, and create edited copies with Save As.
- Sort tables by column and view progress while larger saves load, validate, and
  write.
- Run as a self-contained Windows application without installing Python.

## Known limitations

- Economy projections are estimates and still require refinement against the
  game's internal calculations.
- Relationship editing remains under development, and infrastructure
  fortification editing and Ship Spawner are placeholders.
- Transfers involving aircraft carriers or certain active campaign-division
  relationships are blocked until their linked records can be handled safely.

Keep a known-good backup and test important edits in a copied save slot.
