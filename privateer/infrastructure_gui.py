"""Nation infrastructure editor."""

import tkinter as tk
from tkinter import messagebox, ttk


class InfrastructureWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save, self.nation = save, save.nation(nation_index)
        self.title(f"Infrastructure Manager — {self.nation.name}")
        self.resizable(False, False)
        self.transient(parent)
        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Infrastructure — {self.nation.name}",
                  font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(body, text="Dockyard size").grid(row=1, column=0, sticky="w", padx=(0, 16), pady=(14, 5))
        self.dock_size = tk.StringVar(value="" if self.nation.dock_size is None else str(self.nation.dock_size))
        dock_entry = ttk.Entry(body, textvariable=self.dock_size, width=22,
                               state="normal" if self.nation.dock_size is not None else "disabled")
        dock_entry.grid(row=1, column=1, sticky="ew", pady=(14, 5))
        ttk.Label(body, text="Maximum ship displacement the nation can build in its own dockyards.").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 12))
        ttk.Label(body, text="Fortifications").grid(row=3, column=0, sticky="w", padx=(0, 16), pady=5)
        ttk.Entry(body, state="disabled", width=22).grid(row=3, column=1, sticky="ew", pady=5)
        ttk.Label(body, text="Fortification management will be added later.", state="disabled").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(0, 14))
        buttons = ttk.Frame(body)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Apply", command=self.apply,
                   state="normal" if self.nation.dock_size is not None else "disabled").pack(side="right", padx=(0, 8))
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()
        dock_entry.focus_set()

    def apply(self):
        try:
            value = int(self.dock_size.get().strip().replace(",", ""))
            self.save.set_dock_size(self.nation.index, value)
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Invalid dockyard size", str(exc), parent=self)
            return
        self.master.status.set("Unsaved changes")
        self.destroy()
