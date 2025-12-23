import tkinter as tk
from tkinter import ttk, filedialog

class DirectorySelector(ttk.Frame):
    def __init__(self, parent, label_text="Directory"):
        super().__init__(parent)
        self.path = tk.StringVar()

        ttk.Label(self, text=label_text).grid(row=0, column=0, sticky="w")
        
        entry = ttk.Entry(self, textvariable=self.path)
        entry.grid(row=1, column=0, sticky="ew")
        
        button = ttk.Button(self, text="Browse", command=self._browse)
        button.grid(row=1, column=1, padx=(5, 0))

        self.grid_columnconfigure(0, weight=1)

    def _browse(self):
        d = filedialog.askdirectory()
        if d:
            self.path.set(d)

    def get(self):
        return self.path.get()

    def set(self, path):
        self.path.set(path)
