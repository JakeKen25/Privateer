"""Searchable possession ownership editor with staged transfers."""
import tkinter as tk
from tkinter import ttk, messagebox
from .colonies import possessions, map_document


class ColoniesWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save = save
        self.pending = {}
        self.title(f'Manage Colonies - {save.nation(nation_index).name}')
        self.geometry('1000x700')
        self.minsize(800, 550)
        self.transient(parent)
        try:
            self.records = {(p.area, p.index): p for p in possessions(save)}
            filename = map_document(save)[0]
        except ValueError as exc:
            messagebox.showerror('Colony data unavailable', str(exc), parent=parent)
            self.destroy()
            return
        body = ttk.Frame(self, padding=12)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'Possession ownership - {filename}', font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Includes colonies and home territories. Ownership changes do not settle wars or move ships.').pack(anchor='w')
        filters = ttk.Frame(body)
        filters.pack(fill='x', pady=10)
        self.search = tk.StringVar()
        self.owner_filter = tk.StringVar(value=save.nation(nation_index).name)
        owners = sorted({n.name for n in save.nations} | {'Neutral'})
        ttk.Label(filters, text='Current owner').pack(side='left')
        ttk.Combobox(filters, textvariable=self.owner_filter, values=['All owners']+sorted(set(owners)|{p.owner for p in self.records.values()}), state='readonly', width=23).pack(side='left', padx=8)
        ttk.Label(filters, text='Search').pack(side='left')
        ttk.Entry(filters, textvariable=self.search, width=28).pack(side='left', padx=8)
        self.count = tk.StringVar()
        ttk.Label(filters, textvariable=self.count).pack(side='right')
        frame = ttk.Frame(body)
        frame.pack(fill='both', expand=True)
        self.table = ttk.Treeview(frame, columns=('name','area','owner','new','value','oil','base'), show='headings', selectmode='extended')
        for key, label, width in [('name','Possession',210),('area','Map area',65),('owner','Current owner',130),('new','New owner',130),('value','Value',55),('oil','Oil',40),('base','Base',55)]:
            self.table.heading(key,text=label); self.table.column(key,width=width,minwidth=40)
        scroll=ttk.Scrollbar(frame,orient='vertical',command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y'); self.table.pack(fill='both',expand=True)
        editor=ttk.Frame(body); editor.pack(fill='x',pady=12)
        ttk.Label(editor,text='New owner for selected possessions').pack(side='left')
        self.new_owner=tk.StringVar(value=save.nation(nation_index).name)
        ttk.Combobox(editor,textvariable=self.new_owner,values=owners,state='readonly',width=23).pack(side='left',padx=8)
        ttk.Button(editor,text='Stage transfer',command=self.stage).pack(side='left')
        self.status=tk.StringVar(value='No changes')
        ttk.Label(body,textvariable=self.status).pack(anchor='w')
        ttk.Label(body,text='Apply stages ownership edits in memory. Use Save or Save As to write them.').pack(anchor='w',pady=6)
        buttons=ttk.Frame(body);buttons.pack(fill='x')
        ttk.Button(buttons,text='Reset changes',command=self.reset_changes).pack(side='left')
        ttk.Button(buttons,text='Cancel',command=self.destroy).pack(side='right')
        ttk.Button(buttons,text='Apply',command=self.apply).pack(side='right',padx=8)
        self.search.trace_add('write',lambda *_: self.render())
        self.owner_filter.trace_add('write',lambda *_: self.render())
        self.render();self.bind('<Escape>',lambda e:self.destroy());self.grab_set()

    def render(self):
        self.table.delete(*self.table.get_children())
        for pair,p in self.records.items():
            if self.owner_filter.get() not in ('All owners',p.owner):continue
            if self.search.get().strip().casefold() not in f'{p.name} {p.owner} {p.area}'.casefold():continue
            self.table.insert('','end',iid=f'{p.area}:{p.index}',values=(p.name,p.area,p.owner,self.pending.get(pair,''),p.value,p.oil,p.base))
        self.count.set(f'{len(self.table.get_children())} / {len(self.records)} possessions')
        self.status.set(f'{len(self.pending)} staged ownership change(s)')

    def stage(self):
        if not self.table.selection():
            self.status.set('Select one or more possessions first.');return
        for item in self.table.selection():
            pair=tuple(map(int,item.split(':')))
            owner=self.new_owner.get()
            if owner==self.records[pair].owner:self.pending.pop(pair,None)
            else:self.pending[pair]=owner
        self.render()

    def reset_changes(self):
        self.pending.clear();self.render()

    def apply(self):
        try:self.save.set_colony_owners(self.pending)
        except ValueError as exc:
            messagebox.showerror('Unable to apply ownership changes',str(exc),parent=self);return
        if self.pending:self.master.status.set('Unsaved changes')
        self.destroy()
