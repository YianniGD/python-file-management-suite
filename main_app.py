import tkinter as tk
from tkinter import ttk
import os

# --- IMPORT MODULES ---
from ui.pdf_tools_tab import PDFToolsTab
from ui.sorting_tools_tab import SortingToolsTab
from ui.svg_tab import SVGToolsTab
from ui.batch_tab import BatchToolsTab
from ui.renamer_tab import RenamerTab
from ui.mask_tab import MaskToolsTab
from ui.compress_tab import CompressTab
from ui.illustrator_to_pdf_tab import IllustratorToPdfTab
from ui.illustrator_to_svg_tab import IllustratorToSvgTab
from core.theme import COLORS, FONTS # Import your new theme

class ImageEditorTools(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Graphic Design Suite")
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
        
        # 1. Image Tools
        self.batch_tab = BatchToolsTab(self.notebook, main_window=self)
        self.notebook.add(self.batch_tab, text="Batch Images")

        self.mask_tab = MaskToolsTab(self.notebook, main_window=self)
        self.notebook.add(self.mask_tab, text="Crop/Mask")  

        # 2. PDF Tools
        self.pdf_tools_tab = PDFToolsTab(self.notebook, main_window=self)
        self.notebook.add(self.pdf_tools_tab, text="PDF Tools")

        self.compress_tab = CompressTab(self.notebook, main_window=self)
        self.notebook.add(self.compress_tab, text="PDF Compressor")

        # 3. Sorting Tools
        self.sorting_tools_tab = SortingToolsTab(self.notebook, main_window=self)
        self.notebook.add(self.sorting_tools_tab, text="Sorting Tools")

        # 4. Converters
        self.illustrator_to_pdf_tab = IllustratorToPdfTab(self.notebook, main_window=self)
        self.notebook.add(self.illustrator_to_pdf_tab, text="AI to PDF")

        self.illustrator_to_svg_tab = IllustratorToSvgTab(self.notebook, main_window=self)
        self.notebook.add(self.illustrator_to_svg_tab, text="AI to SVG")

        # 5. Utilities
        self.svg_tab = SVGToolsTab(self.notebook, main_window=self)
        self.notebook.add(self.svg_tab, text="SVG Merger")
        
        self.renamer_tab = RenamerTab(self.notebook, main_window=self)
        self.notebook.add(self.renamer_tab, text="Renamer") 

        # --- GLOBAL STATUS BAR ---
        self.progress_frame = ttk.Frame(self, padding=10)
        self.progress_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.progress_label = ttk.Label(self.progress_frame, text="Ready.")
        self.progress_label.pack(fill=tk.X, pady=2)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=2)

if __name__ == "__main__":
    app = ImageEditorTools()
    app.mainloop()