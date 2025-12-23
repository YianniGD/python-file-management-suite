import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import glob
from core import image_masker

class MaskToolsTab(ttk.Frame):
    def __init__(self, parent, main_window=None): # <--- UPDATED
        super().__init__(parent, padding=10)
        self.main_window = main_window # <--- STORE REFERENCE
        
        # Normal Mask
        f1 = ttk.LabelFrame(self, text="Circular Mask (Keep Center)", padding=10)
        f1.pack(fill=tk.X, pady=5)
        ttk.Button(f1, text="Process Single Image", command=lambda: self._proc("single", "normal")).pack(fill=tk.X, pady=2)
        ttk.Button(f1, text="Process Folder", command=lambda: self._proc("dir", "normal")).pack(fill=tk.X, pady=2)

        # Inverted Mask
        f2 = ttk.LabelFrame(self, text="Inverted Mask (Hollow Center)", padding=10)
        f2.pack(fill=tk.X, pady=10)
        ttk.Button(f2, text="Process Single Image", command=lambda: self._proc("single", "inverted")).pack(fill=tk.X, pady=2)
        ttk.Button(f2, text="Process Folder", command=lambda: self._proc("dir", "inverted")).pack(fill=tk.X, pady=2)

    def _proc(self, type, mode):
        out_folder = "masked_output"
        
        # Optional: Update status
        if self.main_window:
            self.main_window.progress_label.config(text="Processing masks...")
        
        if type == "single":
            path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
            if path:
                out = os.path.join(os.path.dirname(path), out_folder)
                os.makedirs(out, exist_ok=True)
                image_masker.apply_mask(path, out, mode)
                messagebox.showinfo("Done", f"Saved to {out}")
        else:
            path = filedialog.askdirectory()
            if path:
                out = os.path.join(path, out_folder)
                os.makedirs(out, exist_ok=True)
                files = glob.glob(os.path.join(path, "*.jpg")) + glob.glob(os.path.join(path, "*.png"))
                if not files: return
                
                for f in files:
                    image_masker.apply_mask(f, out, mode)
                messagebox.showinfo("Done", f"Processed {len(files)} images.")

        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")