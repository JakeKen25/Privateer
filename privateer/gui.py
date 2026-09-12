"""Thin Tk interface; all mutations remain in :mod:`privateer.save`."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from .model import ECONOMY_ADJUSTMENTS
from .save import RTW3Save
from .technology_gui import TechnologyWindow
from .guns_gui import GunCalibersWindow
from .diplomacy_gui import TensionWindow
from .colonies_gui import ColoniesWindow


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Privateer — Rule the Waves 3 Save Editor")
        self.geometry("900x560")
        self.save_model: RTW3Save | None = None
        bar = ttk.Frame(self, padding=8); bar.pack(fill="x")
        self.path = tk.StringVar(value="Select Rule the Waves 3 Save Folder")
        ttk.Label(bar, textvariable=self.path).pack(side="left", fill="x", expand=True)
        ttk.Button(bar, text="Browse…", command=self.open_folder).pack(side="right")
        self.player = tk.StringVar(value="Player Nation: —")
        ttk.Label(self, textvariable=self.player, padding=(8, 0)).pack(anchor="w")
        self.table = ttk.Treeview(self, columns=("player", "funds", "resources", "ships"), show="tree headings")
        self.table.heading("#0", text="Nation"); self.table.heading("player", text="Player")
        self.table.heading("funds", text="Funds"); self.table.heading("resources", text="Base Resources")
        self.table.heading("ships", text="Ships"); self.table.pack(fill="both", expand=True, padx=8, pady=8)
        self.table.bind("<Button-3>", self._show_nation_menu)
        self.nation_menu = tk.Menu(self, tearoff=False)
        self.nation_menu.add_command(label="Edit Funds", command=lambda: self._edit_economy("funds"))
        self.nation_menu.add_command(
            label="Edit Resources", command=lambda: self._edit_economy("base_resources")
        )
        self.nation_menu.add_separator()
        self.nation_menu.add_command(label="Manage Technology", command=self._manage_technology)
        self.nation_menu.add_command(label="Manage Gun Calibers", command=self._manage_gun_calibers)
        self.nation_menu.add_command(label="Manage Relations", command=self._manage_tension)
        self.nation_menu.add_command(label="Manage Colonies", command=self._manage_colonies)
        for label in (
            "Manage Ships (WIP)",
        ):
            self.nation_menu.add_command(
                label=label, command=lambda title=label: self._show_coming_soon(title)
            )
        actions = ttk.Frame(self, padding=8); actions.pack(fill="x")
        self.status = tk.StringVar(value="No save loaded")
        ttk.Label(actions, textvariable=self.status).pack(side="left")
        ttk.Button(actions, text="Validate", command=self.validate_save).pack(side="right")
        ttk.Button(actions, text="Save As…", command=self.save_as).pack(side="right", padx=6)
        ttk.Button(actions, text="Save", command=self.save_changes).pack(side="right")

    def _show_nation_menu(self, event):
        item = self.table.identify_row(event.y)
        if not item:
            return
        self.table.selection_set(item)
        self.table.focus(item)
        self.nation_menu.tk_popup(event.x_root, event.y_root)

    def _edit_economy(self, field: str):
        if not self.save_model or not self.table.selection():
            return
        item = self.table.selection()[0]
        nation = self.save_model.nation(int(item))
        label = "Funds" if field == "funds" else "Base Resources"
        current = getattr(nation, field)

        dialog = tk.Toplevel(self)
        dialog.title(f"Edit {label} — {nation.name}")
        dialog.resizable(False, False)
        dialog.transient(self)
        body = ttk.Frame(dialog, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Nation: {nation.name}").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(body, text=f"Current {label}: {current if current is not None else '—'}").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(2, 12)
        )
        operation = tk.StringVar(value=ECONOMY_ADJUSTMENTS[0])
        amount = tk.StringVar()
        ttk.Label(body, text="Adjustment").grid(row=2, column=0, sticky="w", padx=(0, 8))
        ttk.Combobox(
            body, textvariable=operation, values=ECONOMY_ADJUSTMENTS,
            state="readonly", width=23,
        ).grid(row=2, column=1, sticky="ew")
        ttk.Label(body, text="Value").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        entry = ttk.Entry(body, textvariable=amount, width=26)
        entry.grid(row=3, column=1, sticky="ew", pady=(8, 0))
        ttk.Label(
            body, text="Positive and negative values are accepted; percentages are rounded."
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 12))
        buttons = ttk.Frame(body)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e")
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right")

        def apply_change():
            if not amount.get().strip():
                messagebox.showerror("Invalid value", "Enter a value to apply.", parent=dialog)
                return
            adjustment = (operation.get(), amount.get())
            try:
                arguments = {field: adjustment}
                self.save_model.adjust_economy(nation.index, **arguments)
            except Exception as exc:
                messagebox.showerror("Invalid value", str(exc), parent=dialog)
                return
            updated_nation = self.save_model.nation(nation.index)
            self.table.set(item, "funds", updated_nation.funds)
            self.table.set(item, "resources", updated_nation.base_resources)
            self.status.set("Unsaved changes")
            dialog.destroy()

        ttk.Button(buttons, text="OK", command=apply_change).pack(side="right", padx=(0, 6))
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.bind("<Return>", lambda _event: apply_change())
        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.grab_set()
        entry.focus_set()

    def _manage_technology(self):
        if self.save_model and self.table.selection():
            TechnologyWindow(self, self.save_model, int(self.table.selection()[0]))

    def _manage_gun_calibers(self):
        if self.save_model and self.table.selection():
            GunCalibersWindow(self, self.save_model, int(self.table.selection()[0]))

    def _manage_tension(self):
        if self.save_model and self.table.selection():
            TensionWindow(self, self.save_model, int(self.table.selection()[0]))

    def _manage_colonies(self):
        if self.save_model and self.table.selection():
            ColoniesWindow(self, self.save_model, int(self.table.selection()[0]))

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
        folder = filedialog.askdirectory(title="Select Rule the Waves 3 Save Folder")
        if not folder: return
        try: self.save_model = RTW3Save.load(folder)
        except Exception as exc:
            messagebox.showerror("Unable to load save", f"{exc}\n\nThe save has not been modified."); return
        self.path.set(folder); self.table.delete(*self.table.get_children())
        selected = None
        for nation in self.save_model.nations:
            item = self.table.insert("", "end", iid=str(nation.index), text=nation.name, values=("Yes" if nation.is_player else "", nation.funds, nation.base_resources, len(nation.ships)))
            if nation.is_player: selected = item
        if selected is not None:
            self.table.selection_set(selected); self.table.focus(selected)
        player = next((n for n in self.save_model.nations if n.is_player), None)
        self.player.set(f"Player Nation: {player.name} (Nation{player.index})" if player else "Player Nation: ambiguous")
        self.status.set(self.save_model.player_detection_warning or "Loaded")

    def validate_save(self):
        if self.save_model: messagebox.showinfo("Validation", str(self.save_model.validate()))

    def save_changes(self):
        if not self.save_model: return
        try: backup = self.save_model.save()
        except Exception as exc: messagebox.showerror("Save refused", str(exc))
        else:
            self.status.set("Saved")
            messagebox.showinfo("Saved", f"Changes saved.\nBackup: {backup}")

    def save_as(self):
        if not self.save_model: return
        folder = filedialog.askdirectory(title="Choose parent for new save folder")
        name = simpledialog.askstring("Save As", "New folder name:") if folder else None
        if not name: return
        try: output = self.save_model.save_as(f"{folder}/{name}")
        except Exception as exc: messagebox.showerror("Save refused", str(exc))
        else: messagebox.showinfo("Saved", f"New save created: {output}")


def launch():
    MainWindow().mainloop()
