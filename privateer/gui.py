"""Thin Tk interface; all mutations remain in :mod:`privateer.save`."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from .model import ECONOMY_ADJUSTMENTS
from .save import RTW3Save


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Privateer — Rule the Waves 3 Save Editor")
        self.geometry("900x650")
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
        self.table.bind("<<TreeviewSelect>>", self._select_nation)
        editor = ttk.LabelFrame(self, text="Edit selected nation's economy", padding=8)
        editor.pack(fill="x", padx=8)
        self.funds_operation, self.funds_amount = self._economy_control(editor, "Funds", 0)
        self.resources_operation, self.resources_amount = self._economy_control(
            editor, "Base Resources", 1
        )
        ttk.Label(
            editor,
            text="Enter a positive or negative amount. Percentage adjustments are rounded to the nearest whole number.",
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))
        actions = ttk.Frame(self, padding=8); actions.pack(fill="x")
        self.status = tk.StringVar(value="No save loaded")
        ttk.Label(actions, textvariable=self.status).pack(side="left")
        ttk.Button(actions, text="Validate", command=self.validate_save).pack(side="right")
        ttk.Button(actions, text="Save As…", command=self.save_as).pack(side="right", padx=6)
        ttk.Button(actions, text="Save", command=self.save_changes).pack(side="right")

    @staticmethod
    def _economy_control(parent, label: str, row: int):
        operation = tk.StringVar(value=ECONOMY_ADJUSTMENTS[0])
        amount = tk.StringVar()
        ttk.Label(parent, text=label, width=18).grid(row=row, column=0, sticky="w", pady=2)
        ttk.Combobox(
            parent, textvariable=operation, values=ECONOMY_ADJUSTMENTS,
            state="readonly", width=23,
        ).grid(row=row, column=1, sticky="w", padx=(0, 8), pady=2)
        ttk.Entry(parent, textvariable=amount, width=24).grid(row=row, column=2, sticky="w", pady=2)
        return operation, amount

    def _select_nation(self, _event=None):
        self.funds_amount.set("")
        self.resources_amount.set("")

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
        selection = self.table.selection()
        if not selection:
            messagebox.showerror("Save refused", "Select a nation before editing its economy.")
            return
        funds = (self.funds_operation.get(), self.funds_amount.get()) if self.funds_amount.get().strip() else None
        resources = ((self.resources_operation.get(), self.resources_amount.get())
                     if self.resources_amount.get().strip() else None)
        try:
            if funds is not None or resources is not None:
                self.save_model.adjust_economy(int(selection[0]), funds=funds, base_resources=resources)
            backup = self.save_model.save()
        except Exception as exc: messagebox.showerror("Save refused", str(exc))
        else:
            nation = self.save_model.nation(int(selection[0]))
            self.table.set(selection[0], "funds", nation.funds)
            self.table.set(selection[0], "resources", nation.base_resources)
            self.funds_amount.set(""); self.resources_amount.set("")
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
