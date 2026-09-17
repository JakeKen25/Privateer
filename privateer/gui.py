"""Thin Tk interface; all mutations remain in :mod:`privateer.save`."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from .save import RTW3Save
from .technology_gui import TechnologyWindow
from .guns_gui import GunCalibersWindow
from .diplomacy_gui import TensionWindow
from .colonies_gui import ColoniesWindow
from .ships_gui import ShipTransfersWindow
from .economy_gui import EconomyWindow
from .infrastructure_gui import InfrastructureWindow
from .admiral_gui import AdmiralWindow
from .aircraft_gui import AircraftWindow
from .busy import run_background, show_while_opening
from .settings import AppSettings
from .settings_gui import SettingsWindow
from .table_sort import heading_text, sorted_with_blanks
from .version import display_version


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Privateer {display_version()} — Rule the Waves 3 Save Editor")
        self.geometry("900x560")
        self.save_model: RTW3Save | None = None
        self.main_sort_column = None
        self.main_sort_reverse = False
        try:
            self.settings = AppSettings.load()
        except ValueError as exc:
            self.settings = AppSettings()
            self.after_idle(lambda: messagebox.showwarning(
                "Settings reset", f"{exc}\n\nDefault settings will be used.", parent=self))
        bar = ttk.Frame(self, padding=8); bar.pack(fill="x")
        self.path = tk.StringVar(value="Select Rule the Waves 3 Save Folder")
        ttk.Label(bar, textvariable=self.path).pack(side="left", fill="x", expand=True)
        ttk.Button(bar, text="Browse…", command=self.open_folder).pack(side="right")
        self.reload_button = ttk.Button(
            bar, text="Reload", command=self.reload_save, state="disabled")
        self.reload_button.pack(side="right", padx=(0, 6))
        self.player = tk.StringVar(value="Player Nation: —")
        ttk.Label(self, textvariable=self.player, padding=(8, 0)).pack(anchor="w")
        self.table = ttk.Treeview(self, columns=("player", "funds", "resources", "ships"), show="tree headings")
        self.main_heading_labels = {
            "nation": "Nation", "player": "Player", "funds": "Funds",
            "resources": "Base Resources", "ships": "Ships"}
        self.table.heading("#0", text="Nation", command=lambda: self.sort_main_table("nation"))
        for key in ("player", "funds", "resources", "ships"):
            self.table.heading(key, text=self.main_heading_labels[key],
                               command=lambda column=key: self.sort_main_table(column))
        self.table.pack(fill="both", expand=True, padx=8, pady=8)
        self.table.bind("<Button-3>", self._show_nation_menu)
        self.nation_menu = tk.Menu(self, tearoff=False)
        self._populate_nation_menu(None)
        actions = ttk.Frame(self, padding=8); actions.pack(fill="x")
        self.status = tk.StringVar(value="No save loaded")
        ttk.Label(actions, textvariable=self.status).pack(side="left")
        ttk.Button(actions, text="Settings", command=self.open_settings).pack(side="right")
        ttk.Button(actions, text="Validate", command=self.validate_save).pack(side="right", padx=6)
        ttk.Button(actions, text="Save As…", command=self.save_as).pack(side="right", padx=6)
        ttk.Button(actions, text="Save", command=self.save_changes).pack(side="right")
        if not self.settings.first_run_complete:
            self.after_idle(self.open_first_run_configuration)

    def _show_nation_menu(self, event):
        item = self.table.identify_row(event.y)
        if not item:
            return
        self.table.selection_set(item)
        self.table.focus(item)
        self._populate_nation_menu(int(item))
        self.nation_menu.tk_popup(event.x_root, event.y_root)

    def _populate_nation_menu(self, nation_index):
        self.nation_menu.delete(0, "end")
        self.nation_menu.add_command(label="Economy and Unrest Manager", command=self._manage_economy)
        self.nation_menu.add_command(label="Infrastructure and Fortifications Manager", command=self._manage_infrastructure)
        if nation_index == 0:
            self.nation_menu.add_command(label="Admiral Manager", command=self._manage_admiral)
        self.nation_menu.add_separator()
        self.nation_menu.add_command(label="Technology Manager", command=self._manage_technology)
        self.nation_menu.add_command(label="Caliber Manager", command=self._manage_gun_calibers)
        self.nation_menu.add_command(label="Relationship Manager", command=self._manage_tension)
        self.nation_menu.add_command(label="Colony Manager", command=self._manage_colonies)
        self.nation_menu.add_command(label="Transfer Ships", command=self._manage_ships)
        self.nation_menu.add_command(label="Aircraft Manager", command=self._manage_aircraft)
        self.nation_menu.add_separator()
        self.nation_menu.add_command(label="Ship Spawner (WIP)",
                                     command=lambda: self._show_coming_soon("Ship Spawner (WIP)"))

    def _manage_economy(self):
        self._open_manager(EconomyWindow, "Preparing economy and unrest data…")

    def _manage_infrastructure(self):
        self._open_manager(InfrastructureWindow, "Loading infrastructure and fortifications…")

    def _manage_admiral(self):
        self._open_manager(AdmiralWindow, "Loading player admiral…")

    def _manage_technology(self):
        self._open_manager(TechnologyWindow, "Loading technology data…")

    def _manage_gun_calibers(self):
        self._open_manager(GunCalibersWindow, "Opening gun caliber manager…")

    def _manage_tension(self):
        self._open_manager(TensionWindow, "Loading relations…")

    def _manage_colonies(self):
        self._open_manager(ColoniesWindow, "Loading colonies…")

    def _manage_ships(self):
        self._open_manager(ShipTransfersWindow, "Preparing ship data…")

    def _manage_aircraft(self):
        self._open_manager(AircraftWindow, "Loading aircraft models…")

    def open_settings(self):
        SettingsWindow(self, self.settings)

    def open_first_run_configuration(self):
        SettingsWindow(self, self.settings, first_run=True)

    def sort_main_table(self, column):
        if self.main_sort_column == column:
            self.main_sort_reverse = not self.main_sort_reverse
        else:
            self.main_sort_column, self.main_sort_reverse = column, False
        self.table.heading("#0", text=heading_text(
            self.main_heading_labels["nation"], column == "nation", self.main_sort_reverse))
        for key in ("player", "funds", "resources", "ships"):
            self.table.heading(key, text=heading_text(
                self.main_heading_labels[key], key == column, self.main_sort_reverse))
        self.render_main_table()

    def render_main_table(self, selected=None):
        if not self.save_model:
            return
        selected = selected or (self.table.selection()[0] if self.table.selection() else None)
        rows = []
        for nation in self.save_model.nations:
            values = {
                "nation": nation.name, "player": "Yes" if nation.is_player else "",
                "funds": nation.funds, "resources": nation.base_resources,
                "ships": len(nation.ships)}
            rows.append((nation, values))
        if self.main_sort_column:
            rows = sorted_with_blanks(
                rows, lambda row: row[1][self.main_sort_column],
                reverse=self.main_sort_reverse,
                numeric=self.main_sort_column in {"funds", "resources", "ships"})
        self.table.delete(*self.table.get_children())
        for nation, values in rows:
            self.table.insert("", "end", iid=str(nation.index), text=nation.name,
                              values=tuple(values[key] for key in
                                           ("player", "funds", "resources", "ships")))
        if selected is not None and self.table.exists(str(selected)):
            self.table.selection_set(str(selected)); self.table.focus(str(selected))

    def _open_manager(self, window_class, message):
        if not self.save_model or not self.table.selection():
            return
        nation_index = int(self.table.selection()[0])
        show_while_opening(
            self, message,
            lambda: window_class(self, self.save_model, nation_index),
            lambda exc: messagebox.showerror("Unable to open window", str(exc), parent=self),
        )

    def _show_coming_soon(self, title: str):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self)
        body = ttk.Frame(dialog, padding=20)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Feature coming soon").pack(pady=(0, 14))
        ttk.Button(body, text="OK", command=dialog.destroy).pack()
        dialog.bind("<Return>", lambda _event: dialog.destroy())
        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.grab_set()

    def open_folder(self):
        initial = self.settings.save_game_directory
        options = {"initialdir": initial} if initial and Path(initial).is_dir() else {}
        folder = filedialog.askdirectory(
            title="Select Rule the Waves 3 Save Folder", **options)
        if not folder: return
        self._load_folder(folder)

    def reload_save(self):
        if not self.save_model:
            return
        if self.save_model.modified and not messagebox.askyesno(
            "Discard unsaved changes?",
            "Reloading will discard all unsaved changes. Continue?",
            parent=self,
        ):
            return
        selected = self.table.selection()[0] if self.table.selection() else None
        self._load_folder(
            self.save_model.folder,
            selected=selected,
            loading_message="Reloading and indexing save files…",
            loaded_status="Reloaded",
        )

    def _load_folder(
        self, folder, *, selected=None,
        loading_message="Loading and indexing save files…", loaded_status="Loaded"
    ):
        run_background(
            self, loading_message, lambda: RTW3Save.load(folder),
            lambda save: self._finish_open(folder, save, selected, loaded_status),
            lambda exc: messagebox.showerror(
                "Unable to load save", f"{exc}\n\nThe save has not been modified.", parent=self),
        )

    def _finish_open(self, folder, save, selected=None, loaded_status="Loaded"):
        self.save_model = save
        self.path.set(str(folder))
        self.reload_button.configure(state="normal")
        player_nation = next((nation for nation in save.nations if nation.is_player), None)
        if selected is None or not any(str(nation.index) == str(selected) for nation in save.nations):
            selected = str(player_nation.index) if player_nation else None
        self.render_main_table(selected)
        player = next((n for n in self.save_model.nations if n.is_player), None)
        self.player.set(f"Player Nation: {player.name} (Nation{player.index})" if player else "Player Nation: ambiguous")
        self.status.set(self.save_model.player_detection_warning or loaded_status)

    def validate_save(self):
        if self.save_model:
            run_background(
                self, "Validating save and design references…", self.save_model.validate,
                lambda report: messagebox.showinfo("Validation", str(report), parent=self),
                lambda exc: messagebox.showerror("Validation failed", str(exc), parent=self),
            )

    def save_changes(self):
        if not self.save_model: return
        def saved(backup):
            self.status.set("Saved")
            detail = f"Backup: {backup}" if backup else "Backups are disabled in Settings."
            messagebox.showinfo("Saved", f"Changes saved.\n{detail}", parent=self)
        run_background(
            self, "Saving and verifying files…",
            lambda: self.save_model.save(
                create_backup=self.settings.create_backups,
                backup_directory=self.settings.backup_directory or None),
            saved,
            lambda exc: messagebox.showerror("Save refused", str(exc), parent=self),
        )

    def save_as(self):
        if not self.save_model: return
        initial = self.settings.save_game_directory
        options = {"initialdir": initial} if initial and Path(initial).is_dir() else {}
        folder = filedialog.askdirectory(title="Choose parent for new save folder", **options)
        name = simpledialog.askstring("Save As", "New folder name:") if folder else None
        if not name: return
        run_background(
            self, "Creating and verifying the new save…",
            lambda: self.save_model.save_as(f"{folder}/{name}"),
            lambda output: messagebox.showinfo("Saved", f"New save created: {output}", parent=self),
            lambda exc: messagebox.showerror("Save refused", str(exc), parent=self),
        )


def launch():
    MainWindow().mainloop()

