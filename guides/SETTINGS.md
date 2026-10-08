# Program settings

## Game and save locations

**First Run Configuration** appears before initial setup is complete. Use
**Browse…** beside each location:

- **Rule the Waves 3 location:** installation folder containing `Data`.
- **Save game location:** parent `Save` folder containing `Game1`, `Game2`, etc.
- **Backup location:** optional destination for retained backups.

Choose **Save configuration**, or **Skip for now** to postpone setup. In ordinary
Settings, choose **Apply** to persist changes or **Cancel** to discard them.
Main-window **Browse** selects one complete `GameX` folder, not the parent folder.

## Backup preferences

Open **Settings** from the lower-right corner of the main window. Settings are
saved immediately when **Apply** is selected and persist between Privateer
sessions. On Windows they are stored in `%APPDATA%\Privateer\settings.json`.
Game save folders and the Privateer installation are not used for preferences.

**Create backups** is enabled by default. Hover over the checkbox to see its
description. When enabled, an in-place **Save** retains a complete copy of the
original save folder. Choose **Browse…** to place retained backups in a specific
directory; leave the location blank to place them beside the original save.

When retained backups are disabled, the backup-location controls are unavailable.
Privateer still makes an internal temporary recovery copy during the multi-file
commit and deletes it after a successful save. This protects against a partial
write without retaining a user backup afterward.

## Appearance

In development 0.9.8.1, enable **Dark mode** in Settings and choose **Apply**.
The theme updates immediately across Privateer and persists between launches.
Clear the checkbox and Apply to restore light mode (the default). Cancel leaves
the theme unchanged. Striped tables retain their alternating bands. This is an
application preference and never changes game saves. Windows-owned file pickers,
message dialogs and title bars may follow the Windows theme instead.
