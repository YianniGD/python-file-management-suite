import tkinter as tk
from tkinter import ttk
import os

# --- IMPORT MODULES ---
from ui.pdf_tools_tab import PDFToolsTab
from ui.sorting_tools_tab import SortingToolsTab
from ui.batch_tab import BatchToolsTab
from ui.renamer_tab import RenamerTab
from ui.mask_tab import MaskToolsTab
from ui.svg_tab import SVGToolsTab
from core.theme import COLORS, FONTS # Import your new theme

class FileManagementSuite(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Management Suite")
        self.geometry("900x650")

        # --- THEME SETUP ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam') # 'clam' allows for easier custom coloring
        
        # Apply Main Window Background
        self.configure(background=COLORS["bg_main"])
        
        # Configure Generic TTK Widgets
        self.style.configure('TFrame', background=COLORS["bg_main"])
        self.style.configure('TLabel', background=COLORS["bg_main"], foreground=COLORS["fg_text"], font=FONTS["body"])
        
        # Configure LabelFrames (The boxes around sections)
        self.style.configure('TLabelFrame', 
                             background=COLORS["bg_main"], 
                             foreground=COLORS["accent"], 
                             relief="flat",
                             font=FONTS["h1"])
        self.style.configure('TLabelFrame.Label', background=COLORS["bg_main"], foreground=COLORS["accent"])

        # Configure Buttons
        self.style.configure('TButton', 
                             font=FONTS["h1"], 
                             background=COLORS["btn_normal"], 
                             foreground=COLORS["fg_text"],
                             borderwidth=0,
                             focuscolor=COLORS["bg_main"]) # Removes ugly dashed line
        
        self.style.map('TButton',
            background=[('active', COLORS["btn_active"])], 
            foreground=[('active', COLORS["fg_text"])]
        )

        # Configure Inputs (Entry fields)
        self.style.configure('TEntry', 
                             fieldbackground=COLORS["bg_secondary"],
                             foreground="black", # Keep text black for readability inside white/light boxes
                             insertcolor=COLORS["fg_text"]) # Cursor color

        # Configure Notebook (Tabs)
        self.style.configure('TNotebook', background=COLORS["bg_main"], borderwidth=0)
        self.style.configure('TNotebook.Tab', 
                             background=COLORS["bg_secondary"], 
                             foreground=COLORS["fg_text"],
                             padding=[10, 5],
                             font=FONTS["body"])
        self.style.map('TNotebook.Tab',
            background=[('selected', COLORS["accent"])],
            foreground=[('selected', 'white')]
        )
        # --- MAIN NOTEBOOK ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- LOAD TABS ---
        
        # 1. Batch Processing
        batch_notebook = ttk.Notebook(self.notebook)
        self.batch_tab = BatchToolsTab(batch_notebook, main_window=self)
        self.renamer_tab = RenamerTab(batch_notebook, main_window=self)
        self.mask_tab = MaskToolsTab(batch_notebook, main_window=self)
        self.svg_tab = SVGToolsTab(batch_notebook, main_window=self)
        batch_notebook.add(self.batch_tab, text="Batch Images")
        batch_notebook.add(self.renamer_tab, text="Renamer")
        batch_notebook.add(self.mask_tab, text="Crop/Mask")
        batch_notebook.add(self.svg_tab, text="SVG Merger")
        self.notebook.add(batch_notebook, text="Batch Processing")

        # 2. PDF Tools
        self.pdf_tools_tab = PDFToolsTab(self.notebook, main_window=self)
        self.notebook.add(self.pdf_tools_tab, text="PDF Tools")

        # 3. Sorting Tools
        self.sorting_tools_tab = SortingToolsTab(self.notebook, main_window=self)
        self.notebook.add(self.sorting_tools_tab, text="Sorting Tools")

        # --- GLOBAL STATUS BAR ---
        self.progress_frame = ttk.Frame(self, padding=10)
        self.progress_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.progress_label = ttk.Label(self.progress_frame, text="Ready.")
        self.progress_label.pack(fill=tk.X, pady=2)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=2)

if __name__ == "__main__":
    app = FileManagementSuite()
    app.mainloop()