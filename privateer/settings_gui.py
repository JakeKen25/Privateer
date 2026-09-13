"""Application settings editor."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .settings import AppSettings
from .tooltip import Tooltip


class SettingsWindow(tk.Toplevel):
    BACKUP_DESCRIPTION = (
        "Determines whether a backup is created when Privateer edits an existing save."
    )

    def __init__(self, parent, settings):
        super().__init__(parent)
        self.title("Privateer Settings")
        self.resizable(False, False)
        self.transient(parent)
        body = ttk.Frame(self, padding=18)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Program options", font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))

        self.create_backups = tk.BooleanVar(value=settings.create_backups)
        self.backup_directory = tk.StringVar(value=settings.backup_directory)
        self.backup_check = ttk.Checkbutton(
            body, text="Create backups", variable=self.create_backups,
            command=self.update_backup_controls)
        self.backup_check.grid(row=1, column=0, columnspan=3, sticky="w")
        self.backup_tooltip = Tooltip(self.backup_check, self.BACKUP_DESCRIPTION)

        self.directory_label = ttk.Label(body, text="Backup location")
        self.directory_label.grid(row=2, column=0, sticky="w", pady=(16, 0), padx=(0, 10))
        self.directory_entry = ttk.Entry(body, textvariable=self.backup_directory,
                                         width=48, state="readonly")
        self.directory_entry.grid(row=2, column=1, sticky="ew", pady=(16, 0))
        self.browse_button = ttk.Button(body, text="Browse…", command=self.browse)
        self.browse_button.grid(row=2, column=2, padx=(8, 0), pady=(16, 0))
        self.directory_hint = ttk.Label(
            body, text="Leave blank to place each backup beside its original save folder.")
        self.directory_hint.grid(row=3, column=1, columnspan=2, sticky="w", pady=(4, 16))

        buttons = ttk.Frame(body)
        buttons.grid(row=4, column=0, columnspan=3, sticky="e")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Apply", command=self.apply).pack(side="right", padx=(0, 8))
        self.update_backup_controls()
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()

    def update_backup_controls(self):
        enabled = self.create_backups.get()
        self.directory_label.state(["!disabled"] if enabled else ["disabled"])
        self.directory_hint.state(["!disabled"] if enabled else ["disabled"])
        self.directory_entry.configure(state="readonly" if enabled else "disabled")
        self.browse_button.configure(state="normal" if enabled else "disabled")

    def browse(self):
        initial = self.backup_directory.get().strip() or None
        selected = filedialog.askdirectory(
            parent=self, title="Choose backup folder", initialdir=initial)
        if selected:
            self.backup_directory.set(selected)

    def apply(self):
        updated = AppSettings(self.create_backups.get(), self.backup_directory.get().strip())
        try:
            updated.save()
        except (OSError, ValueError) as exc:
            messagebox.showerror("Unable to save settings", str(exc), parent=self)
            return
        self.master.settings = updated
        self.destroy()
