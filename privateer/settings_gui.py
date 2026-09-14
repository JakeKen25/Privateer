"""Application settings editor."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .settings import AppSettings
from .tooltip import Tooltip


class SettingsWindow(tk.Toplevel):
    BACKUP_DESCRIPTION = (
        "Determines whether a backup is created when Privateer edits an existing save."
    )

    DEFAULT_INSTALL = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Rule the Waves 3")
    DEFAULT_SAVES = Path.home() / "Documents" / "My Games" / "Rule the Waves 3" / "Save"

    def __init__(self, parent, settings, first_run=False):
        super().__init__(parent)
        self.first_run = first_run
        self.title("First Run Configuration" if first_run else "Privateer Settings")
        self.resizable(False, False)
        self.transient(parent)
        body = ttk.Frame(self, padding=18)
        body.pack(fill="both", expand=True)
        heading = "First Run Configuration" if first_run else "Program options"
        ttk.Label(body, text=heading, font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))

        install_value = settings.rtw3_install_directory
        save_value = settings.save_game_directory
        if first_run and not install_value and self.DEFAULT_INSTALL.is_dir():
            install_value = str(self.DEFAULT_INSTALL)
        if first_run and not save_value and self.DEFAULT_SAVES.is_dir():
            save_value = str(self.DEFAULT_SAVES)
        self.rtw3_install_directory = tk.StringVar(value=install_value)
        self.save_game_directory = tk.StringVar(value=save_value)
        ttk.Label(body, text="Rule the Waves 3 location").grid(
            row=1, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(body, textvariable=self.rtw3_install_directory,
                  width=58, state="readonly").grid(row=1, column=1, sticky="ew")
        ttk.Button(body, text="Browse…", command=self.browse_install).grid(
            row=1, column=2, padx=(8, 0))
        ttk.Label(body, text="Select the game installation folder that contains the Data folder.").grid(
            row=2, column=1, columnspan=2, sticky="w", pady=(4, 12))

        ttk.Label(body, text="Save game location").grid(
            row=3, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(body, textvariable=self.save_game_directory,
                  width=58, state="readonly").grid(row=3, column=1, sticky="ew")
        ttk.Button(body, text="Browse…", command=self.browse_saves).grid(
            row=3, column=2, padx=(8, 0))
        ttk.Label(body, text="Select the folder that contains Game1, Game2, and other save slots.").grid(
            row=4, column=1, columnspan=2, sticky="w", pady=(4, 16))

        self.create_backups = tk.BooleanVar(value=settings.create_backups)
        self.backup_directory = tk.StringVar(value=settings.backup_directory)
        self.backup_check = ttk.Checkbutton(
            body, text="Create backups", variable=self.create_backups,
            command=self.update_backup_controls)
        self.backup_check.grid(row=5, column=0, columnspan=3, sticky="w")
        self.backup_tooltip = Tooltip(self.backup_check, self.BACKUP_DESCRIPTION)

        self.directory_label = ttk.Label(body, text="Backup location")
        self.directory_label.grid(row=6, column=0, sticky="w", pady=(16, 0), padx=(0, 10))
        self.directory_entry = ttk.Entry(body, textvariable=self.backup_directory,
                                         width=48, state="readonly")
        self.directory_entry.grid(row=6, column=1, sticky="ew", pady=(16, 0))
        self.browse_button = ttk.Button(body, text="Browse…", command=self.browse_backup)
        self.browse_button.grid(row=6, column=2, padx=(8, 0), pady=(16, 0))
        self.directory_hint = ttk.Label(
            body, text="Leave blank to place each backup beside its original save folder.")
        self.directory_hint.grid(row=7, column=1, columnspan=2, sticky="w", pady=(4, 16))

        buttons = ttk.Frame(body)
        buttons.grid(row=8, column=0, columnspan=3, sticky="e")
        cancel_text = "Skip for now" if first_run else "Cancel"
        apply_text = "Save configuration" if first_run else "Apply"
        ttk.Button(buttons, text=cancel_text, command=self.destroy).pack(side="right")
        ttk.Button(buttons, text=apply_text, command=self.apply).pack(side="right", padx=(0, 8))
        self.update_backup_controls()
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()

    def update_backup_controls(self):
        enabled = self.create_backups.get()
        self.directory_label.state(["!disabled"] if enabled else ["disabled"])
        self.directory_hint.state(["!disabled"] if enabled else ["disabled"])
        self.directory_entry.configure(state="readonly" if enabled else "disabled")
        self.browse_button.configure(state="normal" if enabled else "disabled")

    def _browse_directory(self, variable, title):
        initial = variable.get().strip()
        if not initial or not Path(initial).is_dir():
            initial = None
        selected = filedialog.askdirectory(parent=self, title=title, initialdir=initial)
        if selected:
            variable.set(selected)

    def browse_install(self):
        self._browse_directory(self.rtw3_install_directory, "Choose Rule the Waves 3 folder")

    def browse_saves(self):
        self._browse_directory(self.save_game_directory, "Choose save game folder")

    def browse_backup(self):
        initial = self.backup_directory.get().strip() or None
        selected = filedialog.askdirectory(
            parent=self, title="Choose backup folder", initialdir=initial)
        if selected:
            self.backup_directory.set(selected)

    def apply(self):
        install_directory = self.rtw3_install_directory.get().strip()
        save_directory = self.save_game_directory.get().strip()
        if self.first_run:
            if not install_directory or not Path(install_directory).is_dir():
                messagebox.showerror(
                    "Rule the Waves 3 location required",
                    "Select the Rule the Waves 3 installation folder.", parent=self)
                return
            if not save_directory or not Path(save_directory).is_dir():
                messagebox.showerror(
                    "Save game location required",
                    "Select the folder that contains the Rule the Waves 3 save slots.", parent=self)
                return
        updated = AppSettings(
            create_backups=self.create_backups.get(),
            backup_directory=self.backup_directory.get().strip(),
            rtw3_install_directory=install_directory,
            save_game_directory=save_directory,
            first_run_complete=self.first_run or self.master.settings.first_run_complete,
        )
        try:
            updated.save()
        except (OSError, ValueError) as exc:
            messagebox.showerror("Unable to save settings", str(exc), parent=self)
            return
        self.master.settings = updated
        self.destroy()

