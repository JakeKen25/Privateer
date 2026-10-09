"""Application-wide light/dark styling, including classic Tk controls."""
import tkinter as tk
from tkinter import ttk


class ThemeManager:
    def __init__(self, root, dark=False):
        self.root = root
        self.style = ttk.Style(root)
        self.light_theme = self.style.theme_use()
        self.dark = False
        self.style.theme_create('privateer-dark', parent='clam', settings={
            '.': {'configure': {'background': '#252930', 'foreground': '#e8edf2',
                               'fieldbackground': '#1b1f25', 'bordercolor': '#505866',
                               'troughcolor': '#171b20', 'selectbackground': '#315c87',
                               'selectforeground': '#ffffff'},
                  'map': {'foreground': [('disabled', '#929ba7')]}},
            'TButton': {'map': {'background': [('pressed', '#315c87'), ('active', '#3a424d')]}},
            'TCheckbutton': {'map': {'background': [('active', '#303640')]}},
            'TRadiobutton': {'map': {'background': [('active', '#303640')]}},
            'TEntry': {'map': {'fieldbackground': [('readonly', '#303640'), ('disabled', '#252930')],
                              'foreground': [('disabled', '#929ba7'), ('readonly', '#e8edf2')]}},
            'TCombobox': {'configure': {'arrowcolor': '#e8edf2'}, 'map': {
                'fieldbackground': [('readonly', '#1b1f25'), ('disabled', '#252930')],
                'foreground': [('disabled', '#929ba7'), ('readonly', '#e8edf2')],
                'selectbackground': [('readonly', '#315c87')],
                'selectforeground': [('readonly', '#ffffff')]}},
            'Treeview': {'configure': {'background': '#1b1f25', 'fieldbackground': '#1b1f25'},
                         'map': {'background': [('selected', '#315c87')],
                                 'foreground': [('selected', '#ffffff')]}},
            'Treeview.Heading': {'configure': {'background': '#343c47', 'foreground': '#e8edf2'},
                                 'map': {'background': [('active', '#445061')]}},
            'TScrollbar': {'configure': {'background': '#414b59', 'arrowcolor': '#e8edf2'}},
        })
        root.bind_all('<Map>', self._mapped, add='+')
        self.apply(dark)

    def apply(self, dark):
        self.dark = bool(dark)
        self.style.theme_use('privateer-dark' if self.dark else self.light_theme)
        # The combobox popup is a Tcl-owned listbox, outside winfo_children.
        for key, value in {'background': '#1b1f25' if dark else '#ffffff',
                           'foreground': '#e8edf2' if dark else '#000000',
                           'selectBackground': '#315c87' if dark else '#0078d7',
                           'selectForeground': '#ffffff'}.items():
            self.root.option_add('*TCombobox*Listbox.' + key, value)
        self._walk(self.root)

    def _mapped(self, event):
        if isinstance(event.widget, tk.Misc):
            self._style_widget(event.widget)

    def _walk(self, widget):
        self._style_widget(widget)
        for child in widget.winfo_children():
            self._walk(child)

    def _style_widget(self, widget):
        options = widget.keys()
        # Save the original colors once so switching back restores custom stripes.
        if not hasattr(widget, '_privateer_light_colors'):
            widget._privateer_light_colors = {
                key: widget.cget(key) for key in (
                    'background', 'foreground', 'activebackground', 'activeforeground',
                    'selectbackground', 'selectforeground', 'selectcolor', 'insertbackground',
                    'troughcolor', 'highlightbackground', 'disabledforeground') if key in options
            }
        original = widget._privateer_light_colors
        if not self.dark:
            if original:
                widget.configure(**original)
        else:
            stripes = {'#fafafa': '#252b33', '#ededed': '#2d333d',
                       '#e5e5e5': '#303843', '#d8d8d8': '#39424f', '#d2d2d2': '#414b59'}
            colors = {}
            for key, value in original.items():
                if 'foreground' in key:
                    colors[key] = '#aab3bf' if key == 'disabledforeground' else '#e8edf2'
                    if str(value).lower() == '#a00000':
                        colors[key] = '#ff9c9c'
                elif key == 'insertbackground':
                    colors[key] = '#e8edf2'
                elif key == 'selectbackground':
                    colors[key] = '#315c87'
                elif key == 'troughcolor':
                    colors[key] = '#171b20'
                else:
                    colors[key] = stripes.get(str(value).lower(), '#252930')
                    if isinstance(widget, (tk.Text, tk.Entry, tk.Listbox)):
                        colors[key] = '#1b1f25'
            if colors:
                widget.configure(**colors)
        if isinstance(widget, ttk.Treeview):
            for tag in ('home', 'blocked'):
                if tag in widget.tk.splitlist(widget.tk.call(widget._w, 'tag', 'names')):
                    widget.tag_configure(tag, foreground='#aab3bf' if self.dark else '#777777')
