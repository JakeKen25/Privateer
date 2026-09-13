"""Responsive modal progress animation and background-task bridge for Tk."""

from __future__ import annotations

from queue import Empty, SimpleQueue
from threading import Thread
import tkinter as tk
from tkinter import ttk


class BusyDialog(tk.Toplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.title("Privateer")
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ttk.Frame(self, padding=18)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=message).pack(anchor="w", pady=(0, 10))
        self.progress = ttk.Progressbar(body, mode="indeterminate", length=300)
        self.progress.pack(fill="x")
        self.progress.start(10)
        self.update_idletasks()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")
        self.grab_set()

    def close(self):
        if not self.winfo_exists():
            return
        self.progress.stop()
        if self.grab_current() == self:
            self.grab_release()
        self.destroy()


def run_background(parent, message, operation, on_success, on_error):
    """Run non-Tk work off the event loop while an animated modal is visible."""
    dialog = BusyDialog(parent, message)
    result = SimpleQueue()

    def worker():
        try:
            result.put((True, operation()))
        except Exception as exc:
            result.put((False, exc))

    def poll():
        try:
            succeeded, value = result.get_nowait()
        except Empty:
            if parent.winfo_exists():
                parent.after(40, poll)
            return
        dialog.close()
        (on_success if succeeded else on_error)(value)

    Thread(target=worker, daemon=True).start()
    parent.after(40, poll)
    return dialog


def show_while_opening(parent, message, operation, on_error):
    """Paint the progress dialog before constructing a Tk window on the UI thread."""
    dialog = BusyDialog(parent, message)

    def open_window():
        try:
            operation()
        except Exception as exc:
            on_error(exc)
        finally:
            dialog.close()

    parent.after(75, open_window)
    return dialog
