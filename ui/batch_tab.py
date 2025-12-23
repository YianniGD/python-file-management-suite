import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from core import general_tools 
from ui.ui_utils import DirectorySelector

class BatchToolsTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        self.grid_columnconfigure(0, weight=1)
        
        batch_frame = ttk.LabelFrame(self, text="Image Batching", padding=(10, 5))
        batch_frame.grid(row=0, column=0, sticky="ew")
        batch_frame.grid_columnconfigure(0, weight=1)

        self.source_selector = DirectorySelector(batch_frame, "Source Dir:")
        self.source_selector.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.dest_selector = DirectorySelector(batch_frame, "Destination Dir:")
        self.dest_selector.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        options_frame = ttk.Frame(batch_frame)
        options_frame.grid(row=2, column=0, sticky="ew", pady=5)
        options_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(options_frame, text="Scale (%):").grid(row=0, column=0, sticky="w")
        self.batch_percentage_entry = ttk.Entry(options_frame, width=5)
        self.batch_percentage_entry.insert(0, "100")
        self.batch_percentage_entry.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(options_frame, text="Format:").grid(row=1, column=0, sticky="w")
        self.batch_format_var = tk.StringVar(self)
        self.batch_format_var.set("JPEG")
        self.batch_format_menu = ttk.OptionMenu(options_frame, self.batch_format_var,
                                                "JPEG", "PNG", "WebP", "BMP", "GIF", "TIFF")
        self.batch_format_menu.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(options_frame, text="Quality:").grid(row=2, column=0, sticky="w")
        self.batch_quality_scale = ttk.Scale(options_frame, from_=1, to=100, orient="horizontal", length=150)
        self.batch_quality_scale.set(85)
        self.batch_quality_scale.grid(row=2, column=1, sticky="w", padx=5)
        
        self.run_btn = ttk.Button(batch_frame, text="Start Batch Process", command=self._start_batch_process)
        self.run_btn.grid(row=3, column=0, sticky="ew", pady=(20, 0))

    def _start_batch_process(self):
        source = self.source_selector.get()
        dest = self.dest_selector.get()
        
        try:
            pct = float(self.batch_percentage_entry.get()) / 100
            fmt = self.batch_format_var.get().lower()
            qual = int(self.batch_quality_scale.get())
            
            self.run_btn.config(state="disabled")
            threading.Thread(target=self._run_thread, args=(source, dest, pct, fmt, qual), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.run_btn.config(state="normal")

    def _update_progress(self, current, total, filename):
        if self.main_window:
            self.main_window.progress_label.config(text=f"Processing: {filename}")
            if total > 0:
                self.main_window.progress_bar['maximum'] = total
                self.main_window.progress_bar['value'] = current

    def _run_thread(self, s, d, p, f, q):
        # We define a callback lambda to pass to the logic
        cb = lambda c, t, file: self.after(0, self._update_progress, c, t, file)
        
        count = general_tools.batch_process_images(s, d, p, f, q, progress_callback=cb)
        
        self.after(0, lambda: self.run_btn.config(state="normal"))
        if self.main_window:
            self.after(0, lambda: self.main_window.progress_label.config(text="Ready."))
            self.after(0, lambda: self.main_window.progress_bar.config(value=0))
            
        self.after(0, lambda: messagebox.showinfo("Done", f"Processed {count} images."))
