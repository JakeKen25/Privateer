"""Technology editor; pending changes remain local until Apply."""
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from .technology import DEFAULT_DATABASE, load_database, AreaTechnologyEdits


class TechnologyWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save = save
        self.nation_index = nation_index
        self.pending = {}
        self.variables = {}
        nation = save.nation(nation_index)
        self.original = nation.section.fields()
        self.title(f'Technology Manager — {nation.name}')
        self.geometry('1180x760')
        self.minsize(1000, 640)
        self.transient(parent)
        install_directory = getattr(getattr(parent, 'settings', None),
                                    'rtw3_install_directory', '')
        configured_database = (Path(install_directory) / 'Data' / 'ResearchAreas3.dat'
                               if install_directory else None)
        path = configured_database if configured_database and configured_database.is_file() else DEFAULT_DATABASE
        if not path.is_file():
            path = filedialog.askopenfilename(parent=self, title='Locate ResearchAreas3.dat',
                                             filetypes=[('RTW3 research data', '*.dat')])
            if not path:
                self.destroy()
                return
        try:
            self.database = load_database(path)
        except (OSError, ValueError) as exc:
            messagebox.showerror('Technology database unavailable', str(exc), parent=self)
            self.destroy()
            return
        self.edits = AreaTechnologyEdits(self.database, self.original)
        self.pending = self.edits.pending
        body = ttk.Frame(self, padding=12)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'{nation.name} (Nation{nation.index}) — Technology',
                  font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(body, text='One slider per research area: level 5 unlocks levels 1–5. 0 = None.').pack(anchor='w')
        ttk.Label(body, text='Select an area, then uncheck individual technologies to skip them. Moving its slider replaces those exceptions.').pack(anchor='w')
        filters = ttk.Frame(body)
        filters.pack(fill='x', pady=8)
        self.search = tk.StringVar()
        ttk.Label(filters, text='Search').pack(side='left')
        ttk.Entry(filters, textvariable=self.search, width=30).pack(side='left', padx=8)
        self.area = tk.StringVar(value='All research areas')
        self.areas = {'All research areas': None}
        self.areas.update({t.area_name: t.area for t in self.database})
        ttk.Combobox(filters, textvariable=self.area, values=list(self.areas),
                     state='readonly', width=35).pack(side='left')
        self.count = tk.StringVar()
        ttk.Label(filters, textvariable=self.count).pack(side='right')
        frame = ttk.Frame(body)
        frame.pack(fill='both', expand=True)
        choices = ttk.LabelFrame(frame, text='Individual technologies', padding=6)
        choices.pack(side='right', fill='both', padx=(10, 0))
        self.choice_canvas = tk.Canvas(choices, width=360, highlightthickness=0)
        choice_scroll = ttk.Scrollbar(choices, command=self.choice_canvas.yview)
        choice_scroll.pack(side='right', fill='y')
        self.choice_canvas.configure(yscrollcommand=choice_scroll.set)
        self.choice_canvas.pack(fill='both', expand=True)
        self.choice_rows = ttk.Frame(self.choice_canvas)
        self.choice_id = self.choice_canvas.create_window((0, 0), window=self.choice_rows, anchor='nw')
        self.choice_rows.bind('<Configure>', lambda e: self.choice_canvas.configure(scrollregion=self.choice_canvas.bbox('all')))
        self.choice_canvas.bind('<Configure>', lambda e: self.choice_canvas.itemconfigure(self.choice_id, width=e.width))
        self.choice_variables = []
        sliders = ttk.Frame(frame)
        sliders.pack(side='left', fill='both', expand=True)
        self.canvas = tk.Canvas(sliders, highlightthickness=0)
        scroll = ttk.Scrollbar(sliders, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.rows = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.rows, anchor='nw')
        self.rows.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(self.window_id, width=e.width))
        self.bind('<MouseWheel>', self.scroll_wheel)
        ttk.Label(body, text='Selected technology', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 4))
        self.details = tk.Text(body, height=6, wrap='word', state='disabled')
        self.details.pack(fill='x')
        ttk.Label(body, text='Unlocks may require refits or other game conditions. Naval gun quality is a separate system.').pack(anchor='w', pady=5)
        buttons = ttk.Frame(body)
        buttons.pack(fill='x')
        self.change_count = tk.StringVar(value='No changes')
        ttk.Label(buttons, textvariable=self.change_count).pack(side='left')
        ttk.Button(buttons, text='Reset changes', command=self.reset_changes).pack(side='left', padx=8)
        ttk.Button(buttons, text='Cancel', command=self.destroy).pack(side='right')
        ttk.Button(buttons, text='Apply', command=self.apply).pack(side='right', padx=8)
        self.search.trace_add('write', lambda *_: self.render_rows())
        self.area.trace_add('write', lambda *_: self.render_rows())
        self.bind('<Escape>', lambda e: self.destroy())
        self.render_rows()
        self.show_details(self.database[0].area)
        self.grab_set()

    def scroll_wheel(self, event):
        canvas = self.choice_canvas if str(event.widget).startswith(str(self.choice_rows)) or event.widget == self.choice_canvas else self.canvas
        canvas.yview_scroll(-int(event.delta / 120), 'units')

    def show_choices(self, area):
        for widget in self.choice_rows.winfo_children():
            widget.destroy()
        self.choice_variables.clear()
        technologies = self.edits.areas[area]
        ttk.Label(self.choice_rows, text=technologies[0].area_name, wraplength=335).pack(anchor='w', pady=5)
        for index, tech in enumerate(technologies):
            value = tk.BooleanVar(value=self.edits.enabled(tech))
            self.choice_variables.append(value)
            row = ttk.Frame(self.choice_rows)
            row.pack(fill='x', pady=4)
            ttk.Checkbutton(row, variable=value,
                            state='normal' if self.edits.editable(area) else 'disabled',
                            command=lambda a=area, i=index, v=value: self.toggle(a, i, v.get())).pack(side='left')
            label = ttk.Label(row, text=f'{index + 1}. {tech.name} ({tech.year or "year unknown"})', wraplength=300, cursor='hand2')
            label.pack(side='left', fill='x', expand=True)
            label.bind('<Button-1>', lambda e, a=area, i=index: self.show_details(a, i, refresh=False))

    def toggle(self, area, index, enabled):
        self.edits.set_enabled(area, index, enabled)
        self.change_count.set(f'{len(self.pending)} unlock flag change(s)')
        position = self.canvas.yview()[0]
        self.render_rows()
        self.canvas.yview_moveto(position)
        self.show_details(area, index, refresh=False)

    def show_details(self, area, index=None, refresh=True):
        if refresh:
            self.show_choices(area)
        technologies = self.edits.areas[area]
        level = self.edits.current(area)
        text = f'{technologies[0].area_name} — Level {level} of {len(technologies)}\n'
        if level or index is not None:
            tech = technologies[level - 1 if index is None else index]
            text += (f'{tech.name} | Typical unlock year: '
                     f'{tech.year if tech.year is not None else "Not available"}\n\n'
                     f'{tech.description or "No effect description available."}')
            text += '\nEnabled' if self.edits.enabled(tech) else '\nDisabled'
        else:
            text += 'None unlocked. No technology effect or unlock year at this setting.'
        if not self.edits.editable(area):
            text += '\nThis area cannot be edited: missing or invalid save fields.'
        elif self.edits.mixed(area):
            text += '\nSome individual levels are disabled. Moving the slider replaces these exceptions.'
        elif area in self.edits.selected:
            text += f'\nLevels 1–{level} enabled; higher levels disabled.' if level else '\nAll defined levels disabled.'
        self.details.configure(state='normal')
        self.details.delete('1.0', 'end')
        self.details.insert('1.0', text)
        self.details.configure(state='disabled')

    def level_label(self, area):
        if not self.edits.editable(area):
            return 'Missing/invalid field'
        level = self.edits.current(area)
        suffix = ' (gaps)' if self.edits.mixed(area) else ''
        return (f'Level {level} / {len(self.edits.areas[area])}' if level else 'None') + suffix

    def changed(self, area, variable, label):
        self.edits.set_level(area, variable.get())
        label.configure(text=self.level_label(area))
        self.change_count.set(f'{len(self.pending)} unlock flag change(s)')
        self.show_details(area)

    def reset_changes(self):
        self.edits.reset()
        self.change_count.set('No changes')
        self.render_rows()
        self.show_details(self.database[0].area)

    def render_rows(self):
        for widget in self.rows.winfo_children():
            widget.destroy()
        self.variables.clear()
        query = self.search.get().strip().casefold()
        area_filter = self.areas[self.area.get()]
        visible = [(area, techs) for area, techs in self.edits.areas.items()
                   if (area_filter is None or area == area_filter) and
                   any(query in f'{t.area_name} {t.name} {t.description} {t.year}'.casefold()
                       for t in techs)]
        self.count.set(f'{len(visible)} / {len(self.edits.areas)} areas')
        self.rows.columnconfigure(1, weight=1)
        for row, (area, technologies) in enumerate(visible):
            name = ttk.Label(self.rows, text=technologies[0].area_name, wraplength=250)
            name.grid(row=row, column=0, sticky='w', padx=6, pady=12)
            name.bind('<Button-1>', lambda e, a=area: self.show_details(a))
            variable = tk.IntVar(value=self.edits.current(area))
            self.variables[area] = variable
            label = ttk.Label(self.rows, width=23, text=self.level_label(area))
            label.grid(row=row, column=2, padx=8)
            slider = tk.Scale(self.rows, from_=0, to=len(technologies), resolution=1,
                              orient='horizontal', variable=variable, length=320,
                              showvalue=True, state='normal' if self.edits.editable(area) else 'disabled',
                              takefocus=True)
            slider.grid(row=row, column=1, sticky='ew', padx=6)
            variable.trace_add('write', lambda *_, a=area, v=variable, l=label: self.changed(a, v, l))
            slider.bind('<FocusIn>', lambda e, a=area: self.show_details(a))
            slider.bind('<Button-1>', lambda e, a=area: self.show_details(a))
        self.canvas.yview_moveto(0)

    def apply(self):
        try:
            self.save.set_technology_flags(self.nation_index, self.database, self.pending)
        except ValueError as exc:
            messagebox.showerror('Unable to apply technology changes', str(exc), parent=self)
            return
        if self.pending:
            self.master.status.set('Unsaved changes')
        self.destroy()
