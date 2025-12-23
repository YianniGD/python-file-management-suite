import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from core.pdf_converter import batch_convert_to_pdf
from ui.ui_utils import DirectorySelector

class IllustratorToPdfTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        self.grid_columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text="Illustrator to PDF Converter", padding=10)
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
            self.main_window.progress_label.config(text="Converting Illustrator files to PDF...")
            self.main_window.progress_bar.start()
        
        threading.Thread(target=self.run_conversion, args=(source_dir, output_dir, archive_dir), daemon=True).start()

    def run_conversion(self, source_dir, output_dir, archive_dir):
        try:
            count = batch_convert_to_pdf(source_dir, output_dir, archive_dir, self.update_progress)
            self.after(0, lambda: messagebox.showinfo("Success", f"Done! {count} files processed."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Script Error", f"Details: {str(e)}"))
        finally:
            self.after(0, self.reset_ui)

    def update_progress(self, value):
        if self.main_window:
            self.main_window.progress_bar['value'] = value

    def reset_ui(self):
        self.btn_run.config(state="normal", text="Start Conversion")
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            self.main_window.progress_bar.stop()
            self.main_window.progress_bar['value'] = 0