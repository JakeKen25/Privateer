"""Per-caliber radio buttons with staged Apply/Cancel editing."""
import tkinter as tk
from tkinter import ttk, messagebox
from .guns import GUN_CALIBERS, GUN_QUALITIES, gun_quality


class GunCalibersWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save = save
        self.nation_index = nation_index
        self.original = save.nation(nation_index).section.fields()
        self.pending = {}
        self.variables = {}
        self.title(f'Manage Gun Calibers - {save.nation(nation_index).name}')
        self.geometry('790x750')
        self.minsize(710, 480)
        self.transient(parent)
        body = ttk.Frame(self, padding=12)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'{save.nation(nation_index).name} - Naval gun quality',
                  font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Choose one quality per caliber. Higher values mean better quality.').pack(anchor='w')
        ttk.Label(body, text='Unavailable disables that caliber; choosing a quality makes it available.').pack(anchor='w')
        frame = ttk.Frame(body)
        frame.pack(fill='both', expand=True, pady=10)
        self.canvas = tk.Canvas(frame, highlightthickness=0)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.canvas.yview)
        scroll.pack(side='right', fill='y')
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        rows = ttk.Frame(self.canvas)
        window_id = self.canvas.create_window((0, 0), window=rows, anchor='nw')
        rows.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(window_id, width=e.width))
        self.bind('<MouseWheel>', lambda e: self.canvas.yview_scroll(-int(e.delta / 120), 'units'))
        ttk.Label(rows, text='Caliber').grid(row=0, column=0, padx=8, pady=8)
        for column, quality in enumerate(GUN_QUALITIES, 1):
            text = 'Unavailable' if quality == 9 else f'{quality:+d}' if quality > 0 else str(quality)
            ttk.Label(rows, text=text).grid(row=0, column=column, padx=8)
            rows.columnconfigure(column, weight=1)
        ttk.Label(rows, text='Current').grid(row=0, column=8, padx=8)
        for row, caliber in enumerate(GUN_CALIBERS, 1):
            current = gun_quality(self.original, caliber)
            variable = tk.IntVar(value=current if current is not None else -99)
            self.variables[caliber] = variable
            ttk.Label(rows, text=f'{caliber}"').grid(row=row, column=0, padx=8, pady=7)
            for column, quality in enumerate(GUN_QUALITIES, 1):
                ttk.Radiobutton(rows, variable=variable, value=quality,
                                state='normal' if current is not None else 'disabled',
                                command=lambda c=caliber: self.changed(c)).grid(row=row, column=column, padx=8)
            label = ('Unavailable' if current == 9 else str(current)) if current is not None else 'Missing/invalid'
            ttk.Label(rows, text=label).grid(row=row, column=8, padx=8)
        ttk.Label(body, text='Apply stages edits. Use Save or Save As in the main window to write them.').pack(anchor='w')
        buttons = ttk.Frame(body)
        buttons.pack(fill='x', pady=(10, 0))
        self.status = tk.StringVar(value='No changes')
        ttk.Label(buttons, textvariable=self.status).pack(side='left')
        ttk.Button(buttons, text='Reset changes', command=self.reset_changes).pack(side='left', padx=8)
        ttk.Button(buttons, text='Cancel', command=self.destroy).pack(side='right')
        ttk.Button(buttons, text='Apply', command=self.apply).pack(side='right', padx=8)
        self.bind('<Escape>', lambda e: self.destroy())
        self.grab_set()

    def changed(self, caliber):
        value = self.variables[caliber].get()
        if value == gun_quality(self.original, caliber):
            self.pending.pop(caliber, None)
        else:
            self.pending[caliber] = value
        self.status.set(f'{len(self.pending)} caliber change(s)')

    def reset_changes(self):
        self.pending.clear()
        for caliber, variable in self.variables.items():
            value = gun_quality(self.original, caliber)
            variable.set(value if value is not None else -99)
        self.status.set('No changes')

    def apply(self):
        try:
            self.save.set_gun_qualities(self.nation_index, self.pending)
        except ValueError as exc:
            messagebox.showerror('Unable to apply gun qualities', str(exc), parent=self)
            return
        if self.pending:
            self.master.status.set('Unsaved changes')
        self.destroy()
