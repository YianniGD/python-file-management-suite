import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import svg_processor

class SVGToolsTab(ttk.Frame):
    def __init__(self, parent, main_window=None): # <--- UPDATED
        super().__init__(parent, padding=10)
        self.main_window = main_window # <--- Store it

        frame = ttk.LabelFrame(self, text="SVG Grid Merger", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Merges all SVGs in a folder into one master grid file.").pack(anchor="w", pady=(0,10))

        ttk.Label(frame, text="Target Folder (Containing .svg files):").pack(anchor="w")
        self.svg_path_entry = ttk.Entry(frame)
        self.svg_path_entry.pack(fill=tk.X, pady=5)
        ttk.Button(frame, text="Browse", command=self._browse_svg_input).pack(fill=tk.X)
        
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=20)
        
        ttk.Button(frame, text="Merge SVGs to Grid", command=self._run_svg_merge).pack(fill=tk.X, pady=20)

    def _browse_svg_input(self):
        d = filedialog.askdirectory()
        if d: 
            self.svg_path_entry.delete(0, tk.END)
            self.svg_path_entry.insert(0, d)
            
    def _run_svg_merge(self):
        path = self.svg_path_entry.get()
        if not path: return messagebox.showerror("Error", "Select a folder first.")
        
        # Optional: Update Global Status
        if self.main_window:
            self.main_window.progress_label.config(text="Merging SVGs...")
        
        success, msg = svg_processor.merge_svgs_to_grid(path)
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            
        if success: messagebox.showinfo("Success", msg)
        else: messagebox.showerror("Error", msg)