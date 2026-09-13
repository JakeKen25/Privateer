"""Small hover descriptions for settings controls."""

import tkinter as tk


class Tooltip:
    def __init__(self, widget, text, delay=400):
        self.widget, self.text, self.delay = widget, text, delay
        self.after_id = None
        self.tip = None
        widget.bind("<Enter>", self.schedule, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def schedule(self, _event=None):
        self.hide()
        self.after_id = self.widget.after(self.delay, self.show)

    def show(self):
        self.after_id = None
        if not self.widget.winfo_exists():
            return
        self.tip = tk.Toplevel(self.widget)
        self.tip.overrideredirect(True)
        self.tip.attributes("-topmost", True)
        x, y = self.widget.winfo_pointerx() + 12, self.widget.winfo_pointery() + 18
        self.tip.geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, justify="left", background="#fffbd6",
                 relief="solid", borderwidth=1, padx=7, pady=5,
                 wraplength=340).pack()

    def hide(self, _event=None):
        if self.after_id is not None:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None
