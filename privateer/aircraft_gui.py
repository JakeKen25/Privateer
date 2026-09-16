"""Aircraft-model creator backed by existing RTW3 model templates."""

import tkinter as tk
from tkinter import messagebox, ttk

from .aircraft import EDITABLE_NUMERIC_FIELDS, ROLE_NAMES, aircraft_types
from .table_sort import heading_text, sorted_with_blanks


FIELD_LABELS = {
    "Year": "Year", "BaseModelYear": "Base model year",
    "MaxSpeed": "Maximum speed", "CruiseSpeed": "Cruise speed",
    "LtEndurance": "Light-load range", "MedEndurance": "Medium-load range",
    "HvyEndurance": "Heavy-load range", "Firepower": "Firepower",
    "Maneuver": "Maneuver", "Toughness": "Toughness",
    "Reliability": "Reliability code", "LtBombLoadSize": "Light bomb size",
    "LtBombLoadNumber": "Light bomb count", "MedBombLoadSize": "Medium bomb size",
    "MedBombLoadNumber": "Medium bomb count", "HvyBombLoadSize": "Heavy bomb size",
    "HvyBombLoadNumber": "Heavy bomb count", "Torpedo1": "Torpedo setting 1",
    "Torpedo2": "Torpedo setting 2", "Missile2": "Missile setting",
    "Carrier": "Carrier capable (0/1)", "Floatplane": "Floatplane (0/1)",
    "AvailableAircraft": "Available aircraft stock",
}


class AircraftWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save = save
        self.nation = save.nation(nation_index)
        self.types = aircraft_types(save)
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
            "Choose an existing model as a template, then edit its name and stats. "
            "Apply creates a model and available stock; squadron assignments are managed separately."
        ), wraplength=970).pack(anchor="w", pady=(2, 10))
        filters = ttk.Frame(body)
        filters.pack(fill="x")
        ttk.Label(filters, text="Role").pack(side="left")
        self.role_filter = tk.StringVar(value="All roles")
        roles = ["All roles", *[ROLE_NAMES[key] for key in sorted(ROLE_NAMES)]]
        ttk.Combobox(filters, textvariable=self.role_filter, values=roles,
                     state="readonly", width=20).pack(side="left", padx=(6, 12))
        self.nation_filter = tk.StringVar(value="Selected nation")
        ttk.Combobox(filters, textvariable=self.nation_filter,
                     values=("Selected nation", "All nations"),
                     state="readonly", width=17).pack(side="left")
        ttk.Label(filters, text="Search").pack(side="left", padx=(14, 6))
        self.search = tk.StringVar()
        ttk.Entry(filters, textvariable=self.search, width=30).pack(side="left")
        self.count = tk.StringVar()
        ttk.Label(filters, textvariable=self.count).pack(side="right")

        list_frame = ttk.Frame(body)
        list_frame.pack(fill="both", expand=False, pady=(10, 8))
        self.columns = ("name", "role", "nation", "year", "speed", "stock")
        self.labels = {
            "name": "Aircraft model", "role": "Role", "nation": "Nation",
            "year": "Year", "speed": "Max speed", "stock": "Available stock",
        }
        self.table = ttk.Treeview(list_frame, columns=self.columns, show="headings", height=8)
        for key, width in (("name", 260), ("role", 140), ("nation", 150),
                           ("year", 65), ("speed", 95), ("stock", 110)):
            self.table.heading(key, text=self.labels[key],
                               command=lambda column=key: self.sort_by(column))
            self.table.column(key, width=width, minwidth=50)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.select_template)

        editor = ttk.LabelFrame(body, text="New aircraft model", padding=10)
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
        self.inputs = {}
        fields = ("Manufacturer", "Name", *EDITABLE_NUMERIC_FIELDS)
        for index, key in enumerate(fields):
            row, pair = divmod(index, 2)
            column = pair * 2
            ttk.Label(form, text=FIELD_LABELS.get(key, key)).grid(
                row=row, column=column, sticky="w", padx=(0, 8), pady=3)
            value = tk.StringVar()
            self.inputs[key] = value
            ttk.Entry(form, textvariable=value, width=24).grid(
                row=row, column=column + 1, sticky="ew", padx=(0, 25), pady=3)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)
        self.template = None
        self.status = tk.StringVar(value="Select a model to copy")
        ttk.Label(body, textvariable=self.status).pack(anchor="w", pady=(8, 4))
        buttons = ttk.Frame(body)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Apply", command=self.apply).pack(side="right", padx=(0, 8))
        for variable in (self.role_filter, self.nation_filter, self.search):
            variable.trace_add("write", lambda *_: self.render())
        self.render()
        self.bind("<Escape>", lambda _event: self.destroy())
        self.grab_set()

    def render(self):
        selected = self.table.selection()[0] if self.table.selection() else None
        self.table.delete(*self.table.get_children())
        rows = []
        search = self.search.get().strip().casefold()
        for model in self.types:
            owner = next((nation.name for nation in self.save.nations
                          if nation.index == int(model.fields["Nation"])),
                         f"Nation{model.fields['Nation']}")
            if self.nation_filter.get() == "Selected nation" and int(model.fields["Nation"]) != self.nation.index:
                continue
            if self.role_filter.get() != "All roles" and model.role != self.role_filter.get():
                continue
            if search not in f"{model.name} {model.role} {owner}".casefold():
                continue
            values = {
                "name": model.name, "role": model.role, "nation": owner,
                "year": model.fields["Year"], "speed": model.fields.get("MaxSpeed", ""),
                "stock": model.fields.get("AvailableAircraft", ""),
            }
            rows.append((model, values))
        rows = sorted_with_blanks(
            rows, lambda row: row[1][self.sort_column],
            reverse=self.sort_reverse,
            numeric=self.sort_column in {"year", "speed", "stock"},
        )
        for model, values in rows:
            self.table.insert("", "end", iid=str(model.slot),
                              values=tuple(values[key] for key in self.columns))
        if selected and self.table.exists(selected):
            self.table.selection_set(selected)
        self.count.set(f"{len(rows)} / {len(self.types)} models")

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
        if not self.table.selection():
            return
        self.template = self.types[int(self.table.selection()[0])]
        for key, variable in self.inputs.items():
            original = self.template.fields.get(key, "0")
            variable.set(f"{original} New" if key == "Name" else original)
        self.status.set(
            f"Copying {self.template.role} model {self.template.name}; "
            f"new model will belong to {self.nation.name}."
        )

    def apply(self):
        if self.template is None:
            self.status.set("Select an existing aircraft model first")
            return
        try:
            created = self.save.create_aircraft_type(
                self.nation.index, self.template.slot,
                {key: variable.get() for key, variable in self.inputs.items()},
            )
        except (ValueError, TypeError) as error:
            messagebox.showerror("Unable to create aircraft", str(error), parent=self)
            return
        self.master.status.set(f"Unsaved changes — created {created.name}")
        self.destroy()
