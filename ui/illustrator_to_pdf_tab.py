import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from core.pdf_converter import batch_convert_to_pdf

class IllustratorToPdfTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        frame = ttk.LabelFrame(self, text="Illustrator to PDF Converter", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Source Directory
        ttk.Label(frame, text="Source Directory:").pack(anchor="w")
        self.source_dir = tk.StringVar()
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Entry(row1, textvariable=self.source_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row1, text="Browse", command=lambda: self._browse(self.source_dir)).pack(side=tk.LEFT, padx=5)

        # Destination Directory
        ttk.Label(frame, text="Destination Directory:").pack(anchor="w")
        self.dest_dir = tk.StringVar()
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Entry(row2, textvariable=self.dest_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row2, text="Browse", command=lambda: self._browse(self.dest_dir)).pack(side=tk.LEFT, padx=5)

        # Archive Directory
        ttk.Label(frame, text="Archive Directory:").pack(anchor="w")
        self.archive_dir = tk.StringVar()
        row3 = ttk.Frame(frame)
        row3.pack(fill=tk.X, pady=5)
        ttk.Entry(row3, textvariable=self.archive_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row3, text="Browse", command=lambda: self._browse(self.archive_dir)).pack(side=tk.LEFT, padx=5)

        # Action Button
        self.btn_run = ttk.Button(frame, text="Start Conversion", command=self.start_thread)
        self.btn_run.pack(fill=tk.X, pady=20)

    def _browse(self, var):
        d = filedialog.askdirectory()
        if d: var.set(d)

    def start_thread(self):
        source_dir = self.source_dir.get()
        output_dir = self.dest_dir.get()
        archive_dir = self.archive_dir.get()

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
            messagebox.showinfo("Success", f"Done! {count} files processed.")
        except Exception as e:
            messagebox.showerror("Script Error", f"Details: {str(e)}")
        finally:
            self.reset_ui()

    def update_progress(self, value):
        if self.main_window:
            self.main_window.progress_bar['value'] = value

    def reset_ui(self):
        self.btn_run.config(state="normal", text="Start Conversion")
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            self.main_window.progress_bar.stop()
            self.main_window.progress_bar['value'] = 0
