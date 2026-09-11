"""WIP technology editor; pending changes remain local until Apply."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .technology import DEFAULT_DATABASE, load_database


class TechnologyWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save = save
        self.nation_index = nation_index
        self.pending = {}
        self.variables = {}
        nation = save.nation(nation_index)
        self.original = nation.section.fields()
        self.title(f'Manage Technology (WIP) — {nation.name}')
        self.geometry('1000x720')
        self.minsize(760, 520)
        self.transient(parent)
        path = DEFAULT_DATABASE
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
        body = ttk.Frame(self, padding=12)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'{nation.name} (Nation{nation.index}) — Technology (WIP)',
                  font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Each technology is an independent unlock: 0 = Not unlocked, 1 = Unlocked.').pack(anchor='w')
        ttk.Label(body, text='Select or move a slider to see its effect and typical unlock year below.').pack(anchor='w')
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
        self.canvas = tk.Canvas(frame, highlightthickness=0)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.rows = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.rows, anchor='nw')
        self.rows.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(self.window_id, width=e.width))
        self.bind('<MouseWheel>', lambda e: self.canvas.yview_scroll(-int(e.delta / 120), 'units'))
        ttk.Label(body, text='Selected technology', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 4))
        self.details = tk.Text(body, height=6, wrap='word', state='disabled')
        self.details.pack(fill='x')
        ttk.Label(body, text='WIP: Unlocks may require refits or other game conditions. Naval gun quality is a separate system.').pack(anchor='w', pady=5)
        buttons = ttk.Frame(body)
        buttons.pack(fill='x')
        self.change_count = tk.StringVar(value='No changes')
        ttk.Label(buttons, textvariable=self.change_count).pack(side='left')
        ttk.Button(buttons, text='Cancel', command=self.destroy).pack(side='right')
        ttk.Button(buttons, text='Apply', command=self.apply).pack(side='right', padx=8)
        self.search.trace_add('write', lambda *_: self.render_rows())
        self.area.trace_add('write', lambda *_: self.render_rows())
        self.bind('<Escape>', lambda e: self.destroy())
        self.render_rows()
        self.show_details(self.database[0])
        self.grab_set()

    def show_details(self, tech):
        value = self.pending.get(tech.key, self.original.get(tech.key))
        state = {'0': 'Not unlocked', '1': 'Unlocked'}.get(str(value), 'Unavailable in this save')
        text = (f'{tech.area_name} — Level {tech.level}: {tech.name}\n'
                f'Typical unlock year: {tech.year if tech.year is not None else "Not available"} | {state}\n\n'
                f'{tech.description or "No effect description available."}')
        self.details.configure(state='normal')
        self.details.delete('1.0', 'end')
        self.details.insert('1.0', text)
        self.details.configure(state='disabled')

    def changed(self, tech, variable, label):
        value = variable.get()
        if str(value) == self.original.get(tech.key):
            self.pending.pop(tech.key, None)
        else:
            self.pending[tech.key] = value
        label.configure(text='Unlocked' if value else 'Not unlocked')
        self.change_count.set(f'{len(self.pending)} pending change(s)')
        self.show_details(tech)

    def render_rows(self):
        for widget in self.rows.winfo_children():
            widget.destroy()
        self.variables.clear()
        query = self.search.get().strip().casefold()
        area = self.areas[self.area.get()]
        visible = [t for t in self.database if (area is None or t.area == area) and
                   query in f'{t.area_name} {t.name} {t.description} {t.year}'.casefold()]
        self.count.set(f'{len(visible)} / {len(self.database)} technologies')
        self.rows.columnconfigure(0, weight=1)
        for row, tech in enumerate(visible):
            name = ttk.Label(self.rows, text=f'{tech.area_name} · Level {tech.level}\n{tech.name}', wraplength=500)
            name.grid(row=row, column=0, sticky='w', padx=6, pady=6)
            name.bind('<Button-1>', lambda e, t=tech: self.show_details(t))
            valid = self.original.get(tech.key) in ('0', '1')
            variable = tk.IntVar(value=int(self.pending.get(tech.key, self.original.get(tech.key, '0'))) if valid else 0)
            self.variables[tech.key] = variable
            label = ttk.Label(self.rows, width=20, text=('Unlocked' if variable.get() else 'Not unlocked') if valid else 'Missing/invalid field')
            label.grid(row=row, column=2, padx=8)
            slider = tk.Scale(self.rows, from_=0, to=1, resolution=1, orient='horizontal',
                              variable=variable, length=115, showvalue=True,
                              state='normal' if valid else 'disabled', takefocus=True)
            slider.grid(row=row, column=1, padx=6)
            variable.trace_add('write', lambda *_, t=tech, v=variable, l=label: self.changed(t, v, l))
            slider.bind('<FocusIn>', lambda e, t=tech: self.show_details(t))
            slider.bind('<Button-1>', lambda e, t=tech: self.show_details(t))
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
