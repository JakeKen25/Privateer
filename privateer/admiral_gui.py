"""Nation0 player admiral editor."""

import tkinter as tk
from tkinter import messagebox, ttk


class AdmiralWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        if nation_index != 0:
            self.destroy()
            raise ValueError("The Admiral Manager is available only for the Nation0 player")
        self.save, self.nation = save, save.nation(0)
        fields = self.nation.section.fields()
        if "AdmiralName" not in fields or "Prestige" not in fields:
            self.destroy()
            raise ValueError("The player nation is missing AdmiralName or Prestige")
        self.title(f"Admiral Manager — {self.nation.name}")
        self.resizable(False, False)
        self.transient(parent)
        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Player admiral — {self.nation.name}",
                  font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(body, text="Admiral name").grid(row=1, column=0, sticky="w", padx=(0, 16), pady=(14, 6))
        self.admiral_name = tk.StringVar(value=fields["AdmiralName"])
        name_entry = ttk.Entry(body, textvariable=self.admiral_name, width=30)
        name_entry.grid(row=1, column=1, sticky="ew", pady=(14, 6))
        ttk.Label(body, text="Prestige").grid(row=2, column=0, sticky="w", padx=(0, 16), pady=6)
        self.prestige = tk.StringVar(value=fields["Prestige"])
        ttk.Entry(body, textvariable=self.prestige, width=30).grid(row=2, column=1, sticky="ew", pady=6)
        ttk.Label(body, text="Changes remain staged until Save or Save As is selected.").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(8, 14))
        buttons = ttk.Frame(body)
        buttons.grid(row=4, column=0, columnspan=2, sticky="e")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Apply", command=self.apply).pack(side="right", padx=(0, 8))
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()
        name_entry.focus_set()

    def apply(self):
        try:
            prestige = int(self.prestige.get().strip().replace(",", ""))
            self.save.set_admiral(0, name=self.admiral_name.get(), prestige=prestige)
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Invalid admiral details", str(exc), parent=self)
            return
        self.master.status.set("Unsaved changes")
        self.destroy()
