"""Combined economy and unrest editor with a budget projection."""

import tkinter as tk
from tkinter import messagebox, ttk

from .economy import BUDGET_DISCLAIMER, budget_context, project_budget
from .model import ECONOMY_ADJUSTMENTS, adjusted_integer


class EconomyWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save, self.nation = save, save.nation(nation_index)
        self.budget_context = budget_context(save, self.nation)
        self.title(f"Economy and Unrest Manager â€” {self.nation.name}")
        self.resizable(False, False)
        self.transient(parent)
        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Economy and Unrest â€” {self.nation.name}",
                  font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(body, text="Funds, base resources, and unrest are staged together. The budget panel updates as you type.").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(2, 12))
        self.operations, self.amounts, self.projected = {}, {}, {}
        for row, (key, label, current) in enumerate((
            ("funds", "Funds", self.nation.funds),
            ("base_resources", "Base resources", self.nation.base_resources),
            ("unrest_level", "Unrest level", self.nation.unrest_level)), start=2):
            ttk.Label(body, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=4)
            operation = tk.StringVar(value=ECONOMY_ADJUSTMENTS[0])
            amount = tk.StringVar()
            projected = tk.StringVar(value=f"Current: {self._number(current)}")
            self.operations[key], self.amounts[key], self.projected[key] = operation, amount, projected
            ttk.Combobox(body, textvariable=operation, values=ECONOMY_ADJUSTMENTS,
                         state="readonly", width=22).grid(row=row, column=1, sticky="ew", pady=4)
            ttk.Entry(body, textvariable=amount, width=16).grid(row=row, column=2, sticky="ew", padx=8, pady=4)
            ttk.Label(body, textvariable=projected, width=24).grid(row=row, column=3, sticky="w", pady=4)
            operation.trace_add("write", lambda *_: self.refresh())
            amount.trace_add("write", lambda *_: self.refresh())

        panel = ttk.LabelFrame(body, text="Estimated monthly budget", padding=10)
        panel.grid(row=5, column=0, columnspan=4, sticky="ew", pady=(12, 8))
        self.lines = {}
        labels = (
            ("yearly_budget", "Yearly budget (provisional)"), ("monthly_budget", "Monthly budget (provisional)"),
            ("maintenance", "Ship maintenance (partial)"), ("construction", "Construction (partial)"),
            ("naval_aircraft", "Naval aircraft"), ("research", "Research"),
            ("extra_training", "Extra training"), ("intelligence", "Intelligence"),
            ("total_expenses", "Calculated expenses (subtotal)"), ("monthly_balance", "Monthly balance"),
            ("funds", "Funds"),
        )
        for row, (key, label) in enumerate(labels):
            ttk.Label(panel, text=label).grid(row=row, column=0, sticky="w", padx=(0, 24), pady=2)
            variable = tk.StringVar()
            self.lines[key] = variable
            ttk.Label(panel, textvariable=variable, width=16, anchor="e",
                      relief="sunken", padding=(4, 1)).grid(row=row, column=1, sticky="e", pady=2)
        ttk.Label(body, text=BUDGET_DISCLAIMER, wraplength=570, justify="left").grid(
            row=6, column=0, columnspan=4, sticky="w", pady=(0, 6))
        self.note = tk.StringVar()
        ttk.Label(body, textvariable=self.note, wraplength=570, justify="left").grid(
            row=7, column=0, columnspan=4, sticky="w", pady=(0, 12))
        buttons = ttk.Frame(body)
        buttons.grid(row=8, column=0, columnspan=4, sticky="e")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Apply", command=self.apply).pack(side="right", padx=(0, 8))
        self.refresh()
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()

    @staticmethod
    def _number(value):
        return "â€”" if value is None else f"{value:,}"

    def _value(self, key, current):
        raw = self.amounts[key].get().strip()
        return current if not raw else adjusted_integer(current, self.operations[key].get(), raw)

    def refresh(self):
        try:
            funds = self._value("funds", self.nation.funds)
            resources = self._value("base_resources", self.nation.base_resources)
            unrest = self._value("unrest_level", self.nation.unrest_level)
            self.projected["funds"].set(f"Projected: {self._number(funds)}")
            self.projected["base_resources"].set(f"Projected: {self._number(resources)}")
            self.projected["unrest_level"].set(f"Projected: {self._number(unrest)}")
            projection = project_budget(self.nation, context=self.budget_context,
                                        base_resources=resources, funds=funds)
            for key, variable in self.lines.items():
                value = getattr(projection, key)
                variable.set("Not calculated" if value is None else f"{value:,}")
            if projection.research is not None:
                self.lines["research"].set(f"{projection.research:,} ({projection.research_percent}%)")
            self.note.set(" ".join(projection.notes))
        except ValueError as exc:
            self.note.set(str(exc))

    def apply(self):
        changes = {}
        for key, current in (("funds", self.nation.funds),
                             ("base_resources", self.nation.base_resources),
                             ("unrest_level", self.nation.unrest_level)):
            raw = self.amounts[key].get().strip()
            if raw:
                changes[key] = (self.operations[key].get(), raw)
        if not changes:
            self.destroy()
            return
        try:
            self.save.adjust_economy(self.nation.index, **changes)
        except Exception as exc:
            messagebox.showerror("Unable to update economy", str(exc), parent=self)
            return
        self.master.render_main_table(str(self.nation.index))
        self.master.status.set("Unsaved changes")
        self.destroy()
