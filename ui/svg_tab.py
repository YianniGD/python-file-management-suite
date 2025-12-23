import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import svg_processor
from ui.ui_utils import DirectorySelector

class SVGToolsTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        self.grid_columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text="SVG Grid Merger", padding=10)
        frame.grid(row=0, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(frame, text="Merges all SVGs in a folder into one master grid file.").grid(row=0, column=0, sticky="w", pady=(0,10))

        self.dir_selector = DirectorySelector(frame, "Target Folder (Containing .svg files):")
        self.dir_selector.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Separator(frame, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=10)
        
        ttk.Button(frame, text="Merge SVGs to Grid", command=self._run_svg_merge).grid(row=3, column=0, sticky="ew", pady=(10, 0))

            
    def _run_svg_merge(self):
        path = self.dir_selector.get()
        if not path: return messagebox.showerror("Error", "Select a folder first.")
        
        # Optional: Update Global Status
        if self.main_window:
            self.main_window.progress_label.config(text="Merging SVGs...")
        
        success, msg = svg_processor.merge_svgs_to_grid(path)
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            
        if success: messagebox.showinfo("Success", msg)
        else: messagebox.showerror("Error", msg)
