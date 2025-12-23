import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import renamer
from ui.ui_utils import DirectorySelector

class RenamerTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        self.grid_columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text="Bulk File Renamer", padding=10)
        frame.grid(row=0, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        self.dir_selector = DirectorySelector(frame, "Target Directory")
        self.dir_selector.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(frame, text="Names List (.txt, comma separated):").grid(row=1, column=0, sticky="w")
        self.names_path = tk.StringVar()
        name_row = ttk.Frame(frame)
        name_row.grid(row=2, column=0, sticky="ew")
        name_row.grid_columnconfigure(0, weight=1)
        ttk.Entry(name_row, textvariable=self.names_path).grid(row=0, column=0, sticky="ew")
        ttk.Button(name_row, text="Browse", command=self._browse_file).grid(row=0, column=1, padx=(5, 0))

        # Action
        ttk.Button(frame, text="Rename Files", command=self._run).grid(row=3, column=0, sticky="ew", pady=(20, 0))

    def _browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if f: self.names_path.set(f)

    def _run(self):
        d = self.dir_selector.get()
        f = self.names_path.get()
        if not d or not f:
            messagebox.showerror("Error", "Please select directory and names file.")
            return
            
        if self.main_window:
            self.main_window.progress_label.config(text="Renaming files...")
            
        success, msg = renamer.rename_files_from_list(d, f)
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            
        if success: messagebox.showinfo("Success", msg)
        else: messagebox.showerror("Error", msg)
