import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import code_cleaner

class CleanerTab(ttk.Frame):
    def __init__(self, parent, main_window=None): # <--- UPDATED
        super().__init__(parent, padding=10)
        self.main_window = main_window # <--- STORE REFERENCE
        
        frame = ttk.LabelFrame(self, text="HTML Code Cleaner", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Directory
        ttk.Label(frame, text="Target Directory (Finds .html files):").pack(anchor="w")
        self.dir_path = tk.StringVar()
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=5)
        ttk.Entry(row, textvariable=self.dir_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Browse", command=self._browse).pack(side=tk.LEFT, padx=5)

        # Lines to Remove
        ttk.Label(frame, text="Lines to remove from top:").pack(anchor="w", pady=(15,0))
        self.lines_var = tk.IntVar(value=1)
        ttk.Entry(frame, textvariable=self.lines_var, width=10).pack(anchor="w", pady=5)

        # Action
        ttk.Button(frame, text="Clean Files", command=self._run).pack(fill=tk.X, pady=20)

    def _browse(self):
        d = filedialog.askdirectory()
        if d: self.dir_path.set(d)

    def _run(self):
        d = self.dir_path.get()
        n = self.lines_var.get()
        if not d:
            messagebox.showerror("Error", "Select a directory.")
            return
            
        if self.main_window:
            self.main_window.progress_label.config(text="Cleaning files...")
            
        success, msg = code_cleaner.remove_lines_from_files(d, n, "html")
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            
        messagebox.showinfo("Result", msg)