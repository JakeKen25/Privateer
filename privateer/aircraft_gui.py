"""Role-based aircraft creator with Game6 year-average stat defaults."""

import tkinter as tk
from tkinter import messagebox, ttk

from .aircraft import (
    ROLE_NAMES, average_defaults, aircraft_types, campaign_year,
    manufacturers_for_nation, suggested_template,
)
from .aircraft_game6_averages import APPLICABLE_FIELDS, FIELD_NAMES
from .table_sort import heading_text, sorted_with_blanks


FIELD_LABELS = {
    "CruiseAltitude": "Cruise altitude", "MaxFuel": "Maximum fuel",
    "Ceiling": "Ceiling", "Climb": "Climb", "MaxSpeed": "Maximum speed",
    "CruiseSpeed": "Cruise speed", "LtEndurance": "Light-load range",
    "MedEndurance": "Medium-load range", "HvyEndurance": "Heavy-load range",
    "Firepower": "Firepower", "Maneuver": "Maneuver", "Toughness": "Toughness",
    "Reliability": "Reliability code", "LtBombLoadSize": "Light bomb size",
    "LtBombLoadNumber": "Light bomb count", "MedBombLoadSize": "Medium bomb size",
    "MedBombLoadNumber": "Medium bomb count", "HvyBombLoadSize": "Heavy bomb size",
    "HvyBombLoadNumber": "Heavy bomb count", "Torpedo1": "Torpedo setting 1",
    "Torpedo2": "Torpedo setting 2", "Missile2": "Missile setting",
    "Radar": "Radar code", "Special": "Special code", "Bombing": "Bombing code",
    "Carrier": "Carrier capable (0/1)", "Floatplane": "Floatplane (0/1)",
    "AvailableAircraft": "Available aircraft stock",
}


class AircraftWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save = save
        self.nation = save.nation(nation_index)
        self.types = aircraft_types(save)
        self.year = campaign_year(save)
        self.template = None
        self.sort_column = "year"
        self.sort_reverse = True
        self.title(f"Aircraft Manager — {self.nation.name}")
        self.geometry("1020x760")
        self.minsize(860, 630)
        self.transient(parent)
        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Create aircraft model — {self.nation.name}",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(body, text=(
            "Choose an aircraft type and edit the Game 6 average stats. The design year is "
            "the current campaign year. A saved model supplies the remaining internal fields; "
            "squadrons are managed separately."
        ), wraplength=970).pack(anchor="w", pady=(2, 10))

        design = ttk.LabelFrame(body, text="Design", padding=10)
        design.pack(fill="x")
        self.role = tk.StringVar(value=ROLE_NAMES[0])
        self.manufacturer = tk.StringVar(value="Privateer")
        self.name = tk.StringVar(value=f"{ROLE_NAMES[0]} {self.year}")
        self.design_year = tk.StringVar(value=str(self.year))
        self.base_model_year = tk.StringVar(value=str(self.year))
        manufacturers = manufacturers_for_nation(self.types, self.nation.index)
        ttk.Label(design, text="Aircraft type").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Combobox(design, textvariable=self.role,
                     values=[ROLE_NAMES[key] for key in ROLE_NAMES],
                     state="readonly", width=22).grid(row=0, column=1, sticky="ew", padx=(0, 20))
        ttk.Label(design, text="Manufacturer").grid(row=0, column=2, sticky="w", padx=(0, 8))
        ttk.Combobox(design, textvariable=self.manufacturer, values=manufacturers,
                     state="readonly", width=27).grid(row=0, column=3, sticky="ew")
        ttk.Label(design, text="Model name").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(design, textvariable=self.name, width=22).grid(
            row=1, column=1, sticky="ew", padx=(0, 20), pady=(8, 0))
        ttk.Label(design, text="Design year").grid(row=1, column=2, sticky="w", pady=(8, 0))
        ttk.Entry(design, textvariable=self.design_year, state="readonly", width=27).grid(
            row=1, column=3, sticky="ew", pady=(8, 0))
        design.columnconfigure(1, weight=1)
        design.columnconfigure(3, weight=1)

        source_heading = ttk.Frame(body)
        source_heading.pack(fill="x", pady=(12, 4))
        ttk.Label(source_heading, text="Saved source model (optional selection)").pack(side="left")
        self.source_filter = tk.StringVar(value="Selected nation")
        ttk.Combobox(source_heading, textvariable=self.source_filter,
                     values=("Selected nation", "All nations"),
                     state="readonly", width=17).pack(side="right")
        self.count = tk.StringVar()
        ttk.Label(source_heading, textvariable=self.count).pack(side="right", padx=(0, 12))
        list_frame = ttk.Frame(body)
        list_frame.pack(fill="x", pady=(0, 8))
        self.columns = ("name", "role", "nation", "year", "speed")
        self.labels = {
            "name": "Aircraft model", "role": "Role", "nation": "Nation",
            "year": "Year", "speed": "Max speed",
        }
        self.table = ttk.Treeview(list_frame, columns=self.columns, show="headings", height=6)
        for key, width in (("name", 310), ("role", 145), ("nation", 155),
                           ("year", 70), ("speed", 100)):
            self.table.heading(key, text=self.labels[key],
                               command=lambda column=key: self.sort_by(column))
            self.table.column(key, width=width, minwidth=50)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.table.pack(fill="x")
        self.table.bind("<<TreeviewSelect>>", self.select_template)

        editor = ttk.LabelFrame(body, text="Average stats for this aircraft type and year", padding=10)
        editor.pack(fill="both", expand=True)
        canvas = tk.Canvas(editor, highlightthickness=0)
        form_scroll = ttk.Scrollbar(editor, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=form_scroll.set)
        form_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        form = ttk.Frame(canvas)
        window = canvas.create_window((0, 0), window=form, anchor="nw")
        form.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)
        self.stats = {key: tk.StringVar() for key in FIELD_NAMES}
        self.stat_widgets = {}
        for key in FIELD_NAMES:
            label = ttk.Label(form, text=FIELD_LABELS[key])
            entry = ttk.Entry(form, textvariable=self.stats[key], width=24)
            self.stat_widgets[key] = (label, entry)

        self.status = tk.StringVar()
        ttk.Label(body, textvariable=self.status, wraplength=970).pack(anchor="w", pady=(8, 4))
        buttons = ttk.Frame(body)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Apply", command=self.apply).pack(side="right", padx=(0, 8))
        self.role.trace_add("write", lambda *_: self.change_role())
        self.source_filter.trace_add("write", lambda *_: self.render())
        self.change_role()
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()

    def _purpose(self):
        return next(code for code, name in ROLE_NAMES.items() if name == self.role.get())

    def change_role(self):
        purpose = self._purpose()
        defaults, used_fallback = average_defaults(purpose, self.year)
        applicable = set(APPLICABLE_FIELDS[purpose])
        for key, value in defaults.items():
            self.stats[key].set(value if key in applicable else ("-1" if key == "Radar" else "0"))
        for widgets in self.stat_widgets.values():
            for widget in widgets:
                widget.grid_forget()
        for index, key in enumerate(APPLICABLE_FIELDS[purpose]):
            row, pair = divmod(index, 2)
            column = pair * 2
            label, entry = self.stat_widgets[key]
            label.grid(row=row, column=column, sticky="w", padx=(0, 8), pady=3)
            entry.grid(row=row, column=column + 1, sticky="ew", padx=(0, 25), pady=3)
        self.name.set(f"{self.role.get()} {self.year}")
        self.template = suggested_template(self.types, purpose, self.nation.index, self.year)
        own_role_models = any(int(model.fields["Purpose"]) == purpose and
                              int(model.fields["Nation"]) == self.nation.index
                              for model in self.types)
        self.source_filter.set("Selected nation" if own_role_models else "All nations")
        self.render()
        if self.table.exists(str(self.template.slot)):
            self.table.selection_set(str(self.template.slot))
            self.table.see(str(self.template.slot))
        note = ("No Game 6 models exist for this type in the campaign year; "
                "each stat uses the lowest year-average value for this type. "
                if used_fallback else
                f"Defaults use Game 6 {self.role.get().lower()} averages for {self.year}. ")
        self.status.set(note + "All shown values can be edited before Apply.")

    def render(self):
        selected = self.table.selection()[0] if self.table.selection() else None
        self.table.delete(*self.table.get_children())
        purpose = self._purpose()
        matching = [model for model in self.types
                    if int(model.fields["Purpose"]) == purpose]
        candidates = matching or self.types
        rows = []
        for model in candidates:
            if (self.source_filter.get() == "Selected nation" and
                    int(model.fields["Nation"]) != self.nation.index):
                continue
            owner = next((nation.name for nation in self.save.nations
                          if nation.index == int(model.fields["Nation"])),
                         f"Nation{model.fields['Nation']}")
            values = {
                "name": model.name, "role": model.role, "nation": owner,
                "year": model.fields["Year"], "speed": model.fields.get("MaxSpeed", ""),
            }
            rows.append((model, values))
        rows = sorted_with_blanks(
            rows, lambda row: row[1][self.sort_column],
            reverse=self.sort_reverse, numeric=self.sort_column in {"year", "speed"},
        )
        for model, values in rows:
            self.table.insert("", "end", iid=str(model.slot),
                              values=tuple(values[key] for key in self.columns))
        if selected and self.table.exists(selected):
            self.table.selection_set(selected)
        self.count.set(f"{len(rows)} source models")

    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column, self.sort_reverse = column, False
        for key, label in self.labels.items():
            self.table.heading(key, text=heading_text(
                label, key == column, self.sort_reverse))
        self.render()

    def select_template(self, _event=None):
        if self.table.selection():
            self.template = self.types[int(self.table.selection()[0])]

    def apply(self):
        if self.template is None:
            self.status.set("This save has no aircraft model available as a source")
            return
        changes = {
            "Manufacturer": self.manufacturer.get(), "Name": self.name.get(),
            "Year": self.design_year.get(), "BaseModelYear": self.base_model_year.get(),
            **{key: variable.get() for key, variable in self.stats.items()},
        }
        try:
            created = self.save.create_aircraft_type(
                self.nation.index, self.template.slot, changes,
                purpose=self._purpose(),
            )
        except (ValueError, TypeError) as error:
            messagebox.showerror("Unable to create aircraft", str(error), parent=self)
            return
        self.master.status.set(f"Unsaved changes — created {created.name}")
        self.destroy()
