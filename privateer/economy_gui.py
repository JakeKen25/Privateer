"""Combined economy and unrest editor with a budget projection."""

import tkinter as tk
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from .economy import BUDGET_DISCLAIMER, BudgetAssumptions, budget_context, project_budget
from .model import ECONOMY_ADJUSTMENTS, adjusted_integer


class EconomyWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save, self.nation = save, save.nation(nation_index)
        self.assumptions = BudgetAssumptions()
        self.budget_context = budget_context(save, self.nation)
        self.title(f"Economy and Unrest Manager — {self.nation.name}")
        self.resizable(False, False)
        self.transient(parent)
        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Economy and Unrest — {self.nation.name}",
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
            ("maintenance", "Maintenance (estimated)"),
            ("all_active_maintenance", "All-active maintenance (estimated)"),
            ("construction", "Construction (estimated)"),
            ("naval_aircraft", "Naval aircraft"), ("research", "Research"),
            ("extra_training", "Extra training"), ("intelligence", "Intelligence"),
            ("total_expenses", "Total expenses (estimated)"), ("monthly_balance", "Monthly balance (estimated)"),
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
        self.details = ScrolledText(body, height=5, width=76, wrap="word", font=("Segoe UI", 9))
        self.details.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        self.note.trace_add("write", lambda *_: self._show_notes())
        buttons = ttk.Frame(body)
        buttons.grid(row=8, column=0, columnspan=4, sticky="e")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Apply", command=self.apply).pack(side="right", padx=(0, 8))
        ttk.Button(buttons, text="Estimate assumptions…", command=self.edit_assumptions).pack(side="right", padx=(0, 8))
        self.refresh()
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()

    @staticmethod
    def _number(value):
        return "—" if value is None else f"{value:,}"

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
                                        base_resources=resources, funds=funds, assumptions=self.assumptions)
            for key, variable in self.lines.items():
                value = getattr(projection, key)
                variable.set(f"{value:,}")
            if projection.research is not None:
                self.lines["research"].set(f"{projection.research:,} ({projection.research_percent}%)")
            self.note.set("\n\n".join(projection.notes))
        except ValueError as exc:
            self.note.set(f"{exc}\nDisplayed budget retains the last valid estimate.")

    def _show_notes(self):
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", self.note.get())
        self.details.configure(state="disabled")

    def edit_assumptions(self):
        dialog = tk.Toplevel(self)
        dialog.title("Budget estimate assumptions")
        dialog.transient(self)
        frame = ttk.Frame(dialog, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Reference estimates, not confirmed game formulas.\nChanges apply to this calculator window only; game saves are untouched.",
                  justify="left").grid(row=0, column=0, columnspan=2, pady=(0, 12), sticky="w")
        labels = {
            "aircraft_rate": "Monthly cost per assigned aircraft",
            "submarine_maintenance": "Monthly submarine maintenance fallback",
            "submarine_construction": "Monthly submarine construction fallback",
            "infrastructure_factor": "Battery / airbase maintenance multiplier",
            "training_base_factor": "Training maintenance-base multiplier",
            "academy_cost": "Monthly academy cost when enabled",
            "dock_construction": "Monthly dock expansion fallback",
            "income_factor": "Income adjustment multiplier",
        }
        variables = {}
        for row, (key, label) in enumerate(labels.items(), 1):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)
            variables[key] = tk.StringVar(value=str(getattr(self.assumptions, key)))
            ttk.Entry(frame, textvariable=variables[key], width=24).grid(row=row, column=1, pady=4)
        def close():
            dialog.destroy()
            self.grab_set()
        def use():
            try:
                candidate = BudgetAssumptions(**{key: Decimal(value.get()) for key, value in variables.items()})
                context = budget_context(self.save, self.nation, candidate)
            except (ValueError, InvalidOperation) as exc:
                messagebox.showerror("Invalid estimate", str(exc) or "Enter a valid number.", parent=dialog)
                return
            self.assumptions, self.budget_context = candidate, context
            self.refresh()
            close()
        def reset():
            defaults = BudgetAssumptions()
            for key, variable in variables.items():
                variable.set(str(getattr(defaults, key)))
        buttons = ttk.Frame(frame)
        buttons.grid(row=len(labels)+1, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Defaults", command=reset).pack(side="left", padx=4)
        ttk.Button(buttons, text="Cancel", command=close).pack(side="left", padx=4)
        ttk.Button(buttons, text="Use estimates", command=use).pack(side="left", padx=4)
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.bind("<Escape>", lambda _: close())
        dialog.grab_set()

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
