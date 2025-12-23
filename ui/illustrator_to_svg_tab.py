import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from core import illustrator_to_svg as illustrator_converter

class IllustratorToSvgTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        frame = ttk.LabelFrame(self, text="Illustrator to SVG Converter", padding=10)
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
            self.main_window.progress_label.config(text="Initializing Illustrator...")
            self.main_window.progress_bar['value'] = 0
        
        threading.Thread(target=self.run_conversion, args=(source_dir, output_dir, archive_dir), daemon=True).start()

    def run_conversion(self, source_dir, output_dir, archive_dir):
        # FIX 2: Thread Safety - Use callback wrapper
        def cb(c, t, m):
            self.after(0, lambda: self.update_progress(c, t, m))

        try:
            # Call the logic
            success, msg = illustrator_converter.batch_convert_to_svg(
                source_dir, output_dir, archive_dir, progress_callback=cb
            )
            # FIX 3: Schedule UI updates on main thread
            self.after(0, lambda: self._finish(success, msg))
            
        except Exception as e:
            self.after(0, lambda: self._finish(False, str(e)))

    def update_progress(self, curr, total, msg):
        # FIX 4: Callback now accepts 3 arguments (curr, total, msg)
        if self.main_window:
            self.main_window.progress_label.config(text=msg)
            if total > 0:
                self.main_window.progress_bar['maximum'] = total
                self.main_window.progress_bar['value'] = curr

    def _finish(self, success, msg):
        # Reset UI on main thread
        self.btn_run.config(state="normal", text="Start Conversion")
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            self.main_window.progress_bar['value'] = 0
            
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)