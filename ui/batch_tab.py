import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from core import general_tools 

class BatchToolsTab(ttk.Frame):
    def __init__(self, parent, main_window=None): # <--- UPDATED
        super().__init__(parent, padding=10)
        self.main_window = main_window # <--- Store it
        
        batch_frame = ttk.LabelFrame(self, text="Image Batching", padding=(10, 5))
        batch_frame.pack(fill=tk.X, pady=5)

        ttk.Label(batch_frame, text="Source Dir:").pack(anchor="w")
        self.batch_source_dir_entry = ttk.Entry(batch_frame)
        self.batch_source_dir_entry.pack(fill=tk.X, ipady=3)
        ttk.Button(batch_frame, text="Browse Source", command=self._browse_batch_source).pack(fill=tk.X, pady=2)

        ttk.Label(batch_frame, text="Destination Dir:").pack(anchor="w")
        self.batch_dest_dir_entry = ttk.Entry(batch_frame)
        self.batch_dest_dir_entry.pack(fill=tk.X, ipady=3)
        ttk.Button(batch_frame, text="Browse Destination", command=self._browse_batch_destination).pack(fill=tk.X, pady=2)

        scale_option_frame = ttk.Frame(batch_frame)
        scale_option_frame.pack(fill=tk.X, pady=2)
        ttk.Label(scale_option_frame, text="Scale (%):").pack(side=tk.LEFT)
        self.batch_percentage_entry = ttk.Entry(scale_option_frame, width=5)
        self.batch_percentage_entry.insert(0, "100")
        self.batch_percentage_entry.pack(side=tk.LEFT, padx=(0, 10))

        format_option_frame = ttk.Frame(batch_frame)
        format_option_frame.pack(fill=tk.X, pady=2)
        ttk.Label(format_option_frame, text="Format:").pack(side=tk.LEFT)
        self.batch_format_var = tk.StringVar(self)
        self.batch_format_var.set("JPEG")
        self.batch_format_menu = ttk.OptionMenu(format_option_frame, self.batch_format_var,
                                                "JPEG", "PNG", "WebP", "BMP", "GIF", "TIFF")
        self.batch_format_menu.pack(side=tk.LEFT, padx=(0, 10))

        quality_option_frame = ttk.Frame(batch_frame)
        quality_option_frame.pack(fill=tk.X, pady=2)
        ttk.Label(quality_option_frame, text="Quality:").pack(side=tk.LEFT)
        self.batch_quality_scale = ttk.Scale(quality_option_frame, from_=1, to=100, orient="horizontal", length=100)
        self.batch_quality_scale.set(85)
        self.batch_quality_scale.pack(side=tk.LEFT)
        
        self.run_btn = ttk.Button(batch_frame, text="Start Batch Process", command=self._start_batch_process)
        self.run_btn.pack(fill=tk.X, pady=5)

    def _browse_batch_source(self):
        directory = filedialog.askdirectory(title="Select Source")
        if directory:
            self.batch_source_dir_entry.delete(0, tk.END)
            self.batch_source_dir_entry.insert(0, directory)

    def _browse_batch_destination(self):
        directory = filedialog.askdirectory(title="Select Destination")
        if directory:
            self.batch_dest_dir_entry.delete(0, tk.END)
            self.batch_dest_dir_entry.insert(0, directory)

    def _start_batch_process(self):
        source = self.batch_source_dir_entry.get()
        dest = self.batch_dest_dir_entry.get()
        
        try:
            pct = float(self.batch_percentage_entry.get()) / 100
            fmt = self.batch_format_var.get().lower()
            qual = int(self.batch_quality_scale.get())
            
            self.run_btn.config(state="disabled")
            threading.Thread(target=self._run_thread, args=(source, dest, pct, fmt, qual), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))

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