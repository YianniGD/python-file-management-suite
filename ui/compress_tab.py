import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import pikepdf
from ui.ui_utils import DirectorySelector

class CompressTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        self.grid_columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text="PDF Compressor", padding=10)
        frame.grid(row=0, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        self.dir_selector = DirectorySelector(frame, "Target Directory (Finds .pdf files):")
        self.dir_selector.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Action Button
        self.btn_run = ttk.Button(frame, text="Start Compression", command=self.start_thread)
        self.btn_run.grid(row=1, column=0, sticky="ew", pady=10)

        # Log Area
        log_frame = ttk.LabelFrame(self, text="Log", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=15, state='disabled', font=("Consolas", 9))
        self.log_area.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(1, weight=1)


    def log(self, message):
        """Updates the text area in a thread-safe way"""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def start_thread(self):
        """Runs compression in a separate thread to keep UI responsive"""
        source_dir = self.dir_selector.get()
        if not source_dir:
            messagebox.showwarning("Warning", "Please select a directory first.")
            return

        self.btn_run.config(state="disabled", text="Processing...")
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END) # Clear previous logs
        self.log_area.config(state='disabled')
        if self.main_window:
            self.main_window.progress_label.config(text="Compressing PDFs...")
            self.main_window.progress_bar.start()

        threading.Thread(target=self.run_compression, args=(source_dir,), daemon=True).start()

    def run_compression(self, source_directory):
        source_path = Path(source_directory)
        output_path = source_path / "compressed_pdfs"

        try:
            output_path.mkdir(exist_ok=True)
            self.log(f"Processing folder: {source_directory}")
            self.log("-" * 40)

            files = list(source_path.glob("*.pdf"))
            if not files:
                self.log("No PDF files found in this directory.")
                self.after(0, self.reset_ui)
                return

            total_saved = 0
            
            for i, file_path in enumerate(files):
                try:
                    if self.main_window:
                        # This progress update is a bit tricky with indeterminate mode
                        pass

                    output_filename = output_path / file_path.name
                    
                    with pikepdf.open(file_path) as pdf:
                        pdf.remove_unreferenced_resources()
                        pdf.save(output_filename, compress_streams=True, linearize=True)
                    
                    # Stats
                    original_size = file_path.stat().st_size
                    new_size = output_filename.stat().st_size
                    savings = original_size - new_size
                    savings_percent = (savings / original_size) * 100 if original_size > 0 else 0
                    total_saved += savings
                    
                    self.log(f"✔ {file_path.name}")
                    self.log(f"   Saved {savings_percent:.1f}% ({original_size/1024:.0f}KB -> {new_size/1024:.0f}KB)")
                    
                except Exception as e:
                    self.log(f"✘ Error on {file_path.name}: {e}")

            self.log("-" * 40)
            self.log(f"All done! Total space saved: {total_saved/1024/1024:.2f} MB")
            self.log(f"Files saved in: {output_path}")
            
        except Exception as e:
            self.log(f"Critical Error: {e}")
        
        self.after(0, self.reset_ui)

    def reset_ui(self):
        self.btn_run.config(state="normal", text="Start Compression")
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            self.main_window.progress_bar.stop()
            self.main_window.progress_bar['value'] = 0