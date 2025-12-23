import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import renamer

class RenamerTab(ttk.Frame):
    def __init__(self, parent, main_window=None): # <--- UPDATED
        super().__init__(parent, padding=10)
        self.main_window = main_window # <--- STORE REFERENCE

        frame = ttk.LabelFrame(self, text="Bulk File Renamer", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Directory
        ttk.Label(frame, text="Target Directory:").pack(anchor="w")
        self.dir_path = tk.StringVar()
        entry_row = ttk.Frame(frame)
        entry_row.pack(fill=tk.X, pady=5)
        ttk.Entry(entry_row, textvariable=self.dir_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(entry_row, text="Browse", command=self._browse_dir).pack(side=tk.LEFT, padx=5)

        # Names File
        ttk.Label(frame, text="Names List (.txt, comma separated):").pack(anchor="w", pady=(10,0))
        self.names_path = tk.StringVar()
        name_row = ttk.Frame(frame)
        name_row.pack(fill=tk.X, pady=5)
        ttk.Entry(name_row, textvariable=self.names_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(name_row, text="Browse", command=self._browse_file).pack(side=tk.LEFT, padx=5)

        # Action
        ttk.Button(frame, text="Rename Files", command=self._run).pack(fill=tk.X, pady=20)

    def _browse_dir(self):
        d = filedialog.askdirectory()
        if d: self.dir_path.set(d)

    def _browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if f: self.names_path.set(f)

    def _run(self):
        d = self.dir_path.get()
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