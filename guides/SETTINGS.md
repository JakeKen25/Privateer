# Program settings

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
