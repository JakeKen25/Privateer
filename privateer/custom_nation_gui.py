"""Standalone custom-nation package maker."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .busy import run_background
from .custom_nation import (
    CustomNationConfig, TRAIT_FIELDS, config_from_template,
    export_custom_nation, load_era_templates,
)
from .technology import load_database


FIELD_LABELS = (
    ("name", "Nation name"), ("adjective", "Nationality adjective"),
    ("leader", "Default leader title"), ("leader_republic", "Republic leader title"),
    ("leader_fascist", "Fascist leader title"),
    ("leader_communist", "Communist leader title"),
    ("admiral_rank", "Admiral rank"), ("admiral_name", "Starting admiral"),
    ("air_unit_name", "Air unit name"), ("parliament_name", "Parliament name"),
    ("trouble_region", "Trouble-region phrase"), ("build_area", "Home build area"),
)

TRAIT_LABELS = {
    "Cautious": "Cautious", "GlobalNavalPower": "Global naval power",
    "AttentionToDetail": "Attention to detail",
    "TechnicalExcellence": "Technical excellence",
    "LiberalDemocracy": "Liberal democracy",
    "EfficientShipbuildingIndustry": "Efficient shipbuilding",
    "UndevelopedShipbuildingIndustry": "Undeveloped shipbuilding",
    "PoorEducation": "Poor education", "Autocracy": "Autocracy",
    "Bombastic": "Bombastic", "Isolationist": "Isolationist",
    "HiddenFlaws": "Hidden flaws", "Colonies": "Colonial power",
}


class CustomNationWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Custom Nation Maker")
        self.geometry("860x690")
        self.minsize(760, 620)
        self.transient(parent)
        install = getattr(parent.settings, "rtw3_install_directory", "")
        if not install or not (Path(install) / "Data").is_dir():
            messagebox.showerror(
                "Rule the Waves 3 location required",
                "Set the Rule the Waves 3 installation location in Settings first.",
                parent=self)
            self.destroy()
            return
        self.install_directory = install
        try:
            self.era_templates = load_era_templates(install)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Nation templates unavailable", str(exc), parent=self)
            self.destroy()
            return
        self.template_names = sorted(
            set(self.era_templates["n00"]) & set(self.era_templates["n20"]))
        if not self.template_names:
            messagebox.showerror(
                "Nation templates unavailable",
                "No nations are present in both the 1890 and 1920 template files.", parent=self)
            self.destroy()
            return

        self.variables = {key: tk.StringVar() for key, _label in FIELD_LABELS}
        self.template_name = tk.StringVar(value=self.template_names[0])
        self.government_type = tk.StringVar()
        self.dock_size = tk.StringVar()
        self.base_resources = tk.StringVar()
        self.budget_modifier = tk.StringVar()
        self.treaty_tonnage_factor = tk.StringVar()
        self.flag_code = tk.StringVar()
        self.ship_names_per_class = tk.StringVar(value="99")
        self.custom_flag_path = tk.StringVar()
        self.traits = {field: tk.BooleanVar() for field in TRAIT_FIELDS}
        self.research_advantages = {area: tk.BooleanVar() for area in range(1, 23)}
        self.gun_quality = {caliber: tk.StringVar() for caliber in range(2, 19)}
        try:
            technologies = load_database(Path(install) / "Data" / "ResearchAreas3.dat")
            self.research_names = {}
            for technology in technologies:
                self.research_names.setdefault(technology.area, technology.area_name)
        except (OSError, ValueError):
            self.research_names = {}

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Custom Nation Maker", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(
            body,
            text="Create an installable nation package for new 1890, 1900, 1920, or 1935 campaigns."
        ).pack(anchor="w", pady=(2, 10))

        notebook = ttk.Notebook(body)
        notebook.pack(fill="both", expand=True)
        identity = ttk.Frame(notebook, padding=14)
        capabilities = ttk.Frame(notebook, padding=14)
        technology = ttk.Frame(notebook, padding=14)
        output = ttk.Frame(notebook, padding=14)
        notebook.add(identity, text="Identity")
        notebook.add(capabilities, text="Capabilities")
        notebook.add(technology, text="Technology & Guns")
        notebook.add(output, text="Output")
        self._build_identity(identity)
        self._build_capabilities(capabilities)
        self._build_technology(technology)
        self._build_output(output)

        footer = ttk.Frame(body)
        footer.pack(fill="x", pady=(12, 0))
        ttk.Label(
            footer,
            text="Territories, relationships, bonus technology, and WarInfo inherit from the template."
        ).pack(side="left")
        ttk.Button(footer, text="Close", command=self.destroy).pack(side="right")
        ttk.Button(footer, text="Export Package…", command=self.export).pack(
            side="right", padx=(0, 8))
        self.template_name.trace_add("write", lambda *_: self.load_selected_template())
        self.load_selected_template()
        self.bind("<Escape>", lambda _event: self.destroy())

    def _build_identity(self, frame):
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Base template").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=4)
        ttk.Combobox(frame, textvariable=self.template_name, values=self.template_names,
                     state="readonly", width=34).grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(
            frame,
            text="The template supplies valid possessions, relationships, research, guns, and AI settings."
        ).grid(row=1, column=1, sticky="w", pady=(0, 10))
        for row, (key, label) in enumerate(FIELD_LABELS, 2):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=3)
            ttk.Entry(frame, textvariable=self.variables[key], width=52).grid(
                row=row, column=1, sticky="ew", pady=3)

    def _build_capabilities(self, frame):
        frame.columnconfigure(1, weight=1)
        numeric = (
            ("government_type", "Government type (0, 1, or 2)", self.government_type),
            ("dock_size", "Starting dock size", self.dock_size),
            ("base_resources", "Base resources", self.base_resources),
            ("budget_modifier", "Budget modifier", self.budget_modifier),
            ("treaty_tonnage_factor", "Treaty tonnage factor", self.treaty_tonnage_factor),
        )
        for row, (_key, label, variable) in enumerate(numeric):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)
            if variable is self.government_type:
                ttk.Combobox(frame, textvariable=variable, values=("0", "1", "2"),
                             state="readonly", width=12).grid(row=row, column=1, sticky="w", pady=4)
            else:
                ttk.Entry(frame, textvariable=variable, width=18).grid(
                    row=row, column=1, sticky="w", pady=4)
        separator_row = len(numeric)
        ttk.Separator(frame).grid(row=separator_row, column=0, columnspan=3,
                                  sticky="ew", pady=12)
        ttk.Label(frame, text="National traits", font=("Segoe UI", 10, "bold")).grid(
            row=separator_row + 1, column=0, columnspan=3, sticky="w", pady=(0, 6))
        for index, field in enumerate(TRAIT_FIELDS):
            row = separator_row + 2 + index // 2
            column = index % 2
            ttk.Checkbutton(frame, text=TRAIT_LABELS[field], variable=self.traits[field]).grid(
                row=row, column=column, sticky="w", padx=(0, 28), pady=3)

    def _build_output(self, frame):
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Flag file code").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=4)
        ttk.Entry(frame, textvariable=self.flag_code, width=18).grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(
            frame, text="Used for the normal, fascist, communist, and republican BMP filenames."
        ).grid(row=1, column=1, sticky="w", pady=(0, 12))
        ttk.Label(frame, text="Optional normal flag").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=4)
        ttk.Entry(frame, textvariable=self.custom_flag_path, state="readonly").grid(
            row=2, column=1, sticky="ew", pady=4)
        ttk.Button(frame, text="Browse…", command=self.browse_flag).grid(
            row=2, column=2, padx=(8, 0), pady=4)
        ttk.Label(
            frame,
            text="If omitted, Privateer creates a 60×40 placeholder flag. Other government flags are placeholders."
        ).grid(row=3, column=1, columnspan=2, sticky="w", pady=(0, 12))
        ttk.Label(frame, text="Names per ship class").grid(
            row=4, column=0, sticky="w", padx=(0, 12), pady=4)
        ttk.Spinbox(frame, from_=1, to=999, textvariable=self.ship_names_per_class,
                    width=10).grid(row=4, column=1, sticky="w", pady=4)
        ttk.Label(
            frame,
            text="Default names use CLASS-NUMBER, including BB-01, KE-05, and CV-30."
        ).grid(row=5, column=1, columnspan=2, sticky="w", pady=(0, 12))
        ttk.Separator(frame).grid(row=6, column=0, columnspan=3, sticky="ew", pady=12)
        ttk.Label(frame, text="Generated package", font=("Segoe UI", 10, "bold")).grid(
            row=7, column=0, columnspan=3, sticky="w")
        ttk.Label(
            frame,
            text=("Data: .n00 and .n20 definitions, ShipNames for both eras, officer names, "
                  "and matching WarInfo files\nFlags: four BMP flags\nRoot: INSTALL.txt and a machine-readable manifest"),
            justify="left"
        ).grid(row=8, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def _build_technology(self, frame):
        research = ttk.LabelFrame(frame, text="Research advantages", padding=10)
        research.pack(side="left", fill="both", expand=True, padx=(0, 8))
        for index, area in enumerate(range(1, 23)):
            label = self.research_names.get(area, f"Research area {area}")
            ttk.Checkbutton(
                research, text=f"{area}. {label}", variable=self.research_advantages[area]
            ).grid(row=index % 11, column=index // 11, sticky="w", padx=(0, 12), pady=2)

        guns = ttk.LabelFrame(frame, text="Starting gun quality", padding=10)
        guns.pack(side="left", fill="y", padx=(8, 0))
        values = ("1 — Good", "0 — Standard", "-1 — Below average", "-2 — Poor", "9 — Unavailable")
        for index, caliber in enumerate(range(2, 19)):
            row, column = index % 9, (index // 9) * 2
            ttk.Label(guns, text=f'{caliber}"').grid(
                row=row, column=column, sticky="e", padx=(0, 4), pady=2)
            ttk.Combobox(
                guns, textvariable=self.gun_quality[caliber], values=values,
                state="readonly", width=16
            ).grid(row=row, column=column + 1, sticky="w", padx=(0, 8), pady=2)

    def load_selected_template(self):
        name = self.template_name.get()
        template = self.era_templates["n00"].get(name)
        if template is None:
            return
        config = config_from_template(template)
        for key, _label in FIELD_LABELS:
            self.variables[key].set(getattr(config, key))
        self.government_type.set(str(config.government_type))
        self.dock_size.set(str(config.dock_size))
        self.base_resources.set(str(config.base_resources))
        self.budget_modifier.set(str(config.budget_modifier))
        self.treaty_tonnage_factor.set(str(config.treaty_tonnage_factor))
        self.flag_code.set(config.flag_code)
        for field, variable in self.traits.items():
            variable.set(bool((config.traits or {}).get(field)))
        for area, variable in self.research_advantages.items():
            variable.set(bool((config.research_advantages or {}).get(area)))
        gun_labels = {1: "1 — Good", 0: "0 — Standard", -1: "-1 — Below average",
                      -2: "-2 — Poor", 9: "9 — Unavailable"}
        for caliber, variable in self.gun_quality.items():
            variable.set(gun_labels.get((config.gun_quality or {}).get(caliber, 9),
                                        "9 — Unavailable"))

    def browse_flag(self):
        selected = filedialog.askopenfilename(
            parent=self, title="Choose normal-government flag",
            filetypes=(("Windows bitmap", "*.bmp"), ("All files", "*.*")))
        if selected:
            self.custom_flag_path.set(selected)

    def make_config(self):
        try:
            numeric = {
                "government_type": int(self.government_type.get()),
                "dock_size": int(self.dock_size.get().replace(",", "")),
                "base_resources": int(self.base_resources.get().replace(",", "")),
                "budget_modifier": int(self.budget_modifier.get().replace(",", "")),
                "treaty_tonnage_factor": int(self.treaty_tonnage_factor.get().replace(",", "")),
                "ship_names_per_class": int(self.ship_names_per_class.get().replace(",", "")),
            }
        except ValueError as exc:
            raise ValueError("Government, economy, treaty, and ship-name values must be whole numbers") from exc
        config = CustomNationConfig(
            **{key: variable.get().strip() for key, variable in self.variables.items()},
            template_name=self.template_name.get(), flag_code=self.flag_code.get().strip(),
            custom_flag_path=self.custom_flag_path.get().strip(),
            traits={field: variable.get() for field, variable in self.traits.items()},
            research_advantages={area: variable.get()
                                 for area, variable in self.research_advantages.items()},
            gun_quality={caliber: int(variable.get().split()[0])
                         for caliber, variable in self.gun_quality.items()},
            **numeric,
        )
        config.validate()
        return config

    def export(self):
        try:
            config = self.make_config()
        except ValueError as exc:
            messagebox.showerror("Cannot export nation", str(exc), parent=self)
            return
        output = filedialog.askdirectory(
            parent=self, title="Choose where to create the custom nation package",
            initialdir=str(Path.home() / "Documents"))
        if not output:
            return
        run_background(
            self, "Creating and verifying custom nation package…",
            lambda: export_custom_nation(config, self.install_directory, output),
            lambda path: messagebox.showinfo(
                "Custom nation package created",
                f"Created:\n{path}\n\nRead INSTALL.txt before copying it into Rule the Waves 3.",
                parent=self),
            lambda exc: messagebox.showerror("Cannot export nation", str(exc), parent=self),
        )

