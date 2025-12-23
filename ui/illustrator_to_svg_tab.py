import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from core import illustrator_to_svg as illustrator_converter
from ui.ui_utils import DirectorySelector

class IllustratorToSvgTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        self.grid_columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text="Illustrator to SVG Converter", padding=10)
        frame.grid(row=0, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        self.source_selector = DirectorySelector(frame, "Source Directory:")
        self.source_selector.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.dest_selector = DirectorySelector(frame, "Destination Directory:")
        self.dest_selector.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.archive_selector = DirectorySelector(frame, "Archive Directory:")
        self.archive_selector.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Action Button
        self.btn_run = ttk.Button(frame, text="Start Conversion", command=self.start_thread)
        self.btn_run.grid(row=3, column=0, sticky="ew", pady=(20, 0))

    def start_thread(self):
        source_dir = self.source_selector.get()
        output_dir = self.dest_selector.get()
        archive_dir = self.archive_selector.get()

        if not all([source_dir, output_dir, archive_dir]):
            messagebox.showwarning("Warning", "Please select all three directories.")
            return

        self.btn_run.config(state="disabled", text="Processing...")
        if self.main_window:
            self.main_window.progress_label.config(text="Initializing Illustrator...")
            self.main_window.progress_bar['value'] = 0
        
        threading.Thread(target=self.run_conversion, args=(source_dir, output_dir, archive_dir), daemon=True).start()

    def run_conversion(self, source_dir, output_dir, archive_dir):
        def cb(c, t, m):
            self.after(0, lambda: self.update_progress(c, t, m))

        try:
            success, msg = illustrator_converter.batch_convert_to_svg(
                source_dir, output_dir, archive_dir, progress_callback=cb
            )
            self.after(0, lambda: self._finish(success, msg))
            
        except Exception as e:
            self.after(0, lambda: self._finish(False, str(e)))

    def update_progress(self, curr, total, msg):
        if self.main_window:
            self.main_window.progress_label.config(text=msg)
            if total > 0:
                self.main_window.progress_bar['maximum'] = total
                self.main_window.progress_bar['value'] = curr

    def _finish(self, success, msg):
        self.btn_run.config(state="normal", text="Start Conversion")
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            self.main_window.progress_bar['value'] = 0
            
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
