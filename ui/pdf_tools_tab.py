import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from core import pdf_merger, pdf_extractor, pdf_processor
from ui.ui_utils import DirectorySelector
from ui.compress_tab import CompressTab
from ui.illustrator_to_pdf_tab import IllustratorToPdfTab

class PDFToolsTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window
        self.stop_event = threading.Event()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky="nsew")

        merger_frame = self._create_merger_tab(notebook)
        extractor_frame = self._create_extractor_tab(notebook)
        compiler_frame = self._create_compiler_tab(notebook)
        optimizer_frame = self._create_optimizer_tab(notebook)

        notebook.add(merger_frame, text="PDF Merger")
        notebook.add(extractor_frame, text="Image Extractor")
        notebook.add(compiler_frame, text="PDF Compiler")
        notebook.add(optimizer_frame, text="PDF Optimizer")

        compress_tab = CompressTab(notebook, main_window=self.main_window)
        notebook.add(compress_tab, text="PDF Compressor")

        illustrator_to_pdf_tab = IllustratorToPdfTab(notebook, main_window=self.main_window)
        notebook.add(illustrator_to_pdf_tab, text="AI to PDF")

    def _create_optimizer_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.grid_columnconfigure(0, weight=1)

        container = ttk.LabelFrame(frame, text="PDF Linearizer", padding=10)
        container.grid(row=0, column=0, sticky="ew")
        container.grid_columnconfigure(0, weight=1)
        
        self.linearize_files = []
        self.lbl_linearize_status = ttk.Label(container, text="No files selected")
        self.lbl_linearize_status.grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Button(container, text="Select PDFs", command=self._select_linearize_pdfs).grid(row=1, column=0, sticky="ew")

        action_frame = ttk.Frame(container)
        action_frame.grid(row=2, column=0, sticky="ew", pady=10)
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)

        self.run_btn_linearizer = ttk.Button(action_frame, text="Linearize PDFs", command=self._run_linearizer)
        self.run_btn_linearizer.grid(row=0, column=0, sticky="ew", pady=10)

        self.stop_btn_linearizer = ttk.Button(action_frame, text="Stop", command=self._stop_process)
        self.stop_btn_linearizer.grid(row=0, column=1, sticky="ew", padx=(5,0), pady=10)
        self.stop_btn_linearizer.grid_remove()
        
        return frame


    def _create_merger_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.grid_columnconfigure(0, weight=1)

        container = ttk.LabelFrame(frame, text="Combine PDFs with TOC", padding=10)
        container.grid(row=0, column=0, sticky="ew")
        container.grid_columnconfigure(0, weight=1)

        self.merger_dir_selector = DirectorySelector(container, "Folder Containing PDFs:")
        self.merger_dir_selector.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(container, text="Title Page Header:").grid(row=1, column=0, sticky="w")
        self.title_var = tk.StringVar(value="My Portfolio")
        ttk.Entry(container, textvariable=self.title_var).grid(row=2, column=0, sticky="ew", pady=(0, 5))

        info_lbl = ttk.Label(container, text="This will merge all .pdf files in the folder sorted alphabetically.\nIt generates a Title Page, visual Table of Contents, and clickable bookmarks.", foreground="gray", justify="left")
        info_lbl.grid(row=3, column=0, sticky="w", pady=10)

        self.run_btn_merger = ttk.Button(container, text="Merge PDFs", command=self._run_merger)
        self.run_btn_merger.grid(row=4, column=0, sticky="ew", pady=10)
        
        return frame

    def _create_extractor_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.grid_columnconfigure(0, weight=1)
        
        self.pdf_files = []
        container = ttk.LabelFrame(frame, text="PDF to Image Extractor", padding=10)
        container.grid(row=0, column=0, sticky="ew")
        container.grid_columnconfigure(0, weight=1)

        self.lbl_status = ttk.Label(container, text="No files selected")
        self.lbl_status.grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Button(container, text="Select PDFs", command=self._select_extractor).grid(row=1, column=0, sticky="ew")

        self.extractor_out_selector = DirectorySelector(container, "Output Directory:")
        self.extractor_out_selector.grid(row=2, column=0, sticky="ew", pady=(15, 0))

        self.run_btn_extractor = ttk.Button(container, text="Extract All Pages", command=self._run_extractor)
        self.run_btn_extractor.grid(row=3, column=0, sticky="ew", pady=20)

        return frame

    def _create_compiler_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        frame.grid_columnconfigure(0, weight=1)

        comp_frame = ttk.LabelFrame(frame, text="Dark Mode Compilation PDF", padding=10)
        comp_frame.grid(row=0, column=0, sticky="ew", pady=5)
        comp_frame.grid_columnconfigure(0, weight=1)
        
        self.compiler_dir_selector = DirectorySelector(comp_frame, "Source Folder (Images):")
        self.compiler_dir_selector.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        opts_frame = ttk.Frame(comp_frame)
        opts_frame.grid(row=1, column=0, sticky="ew", pady=5)
        ttk.Label(opts_frame, text="Orientation:").pack(side=tk.LEFT, padx=(0,5))
        self.pdf_orient_var = tk.StringVar(value="P")
        ttk.Radiobutton(opts_frame, text="Portrait", variable=self.pdf_orient_var, value="P").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(opts_frame, text="Landscape", variable=self.pdf_orient_var, value="L").pack(side=tk.LEFT, padx=5)
        
        self.pdf_native_res_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_frame, text="Native Resolution", variable=self.pdf_native_res_var).pack(side=tk.LEFT, padx=10)

        self.pdf_recursive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_frame, text="Batch Process Subfolders", variable=self.pdf_recursive_var).pack(side=tk.LEFT, padx=10)
        
        self.pdf_filename_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_frame, text="Include Filenames", variable=self.pdf_filename_var).pack(side=tk.LEFT, padx=20)

        action_frame = ttk.Frame(comp_frame)
        action_frame.grid(row=2, column=0, sticky="ew", pady=10)
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)


        self.generate_btn = ttk.Button(action_frame, text="Generate Compilation PDF", command=self._run_pdf_comp)
        self.generate_btn.grid(row=0, column=0, sticky="ew")

        self.stop_btn = ttk.Button(action_frame, text="Stop", command=self._stop_process)
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(5,0))
        self.stop_btn.grid_remove()

        sheet_frame = ttk.LabelFrame(frame, text="Contact Sheet Generator (Grid)", padding=10)
        sheet_frame.grid(row=1, column=0, sticky="ew", pady=10)
        sheet_frame.grid_columnconfigure(0, weight=1)
        
        self.sheet_dir_selector = DirectorySelector(sheet_frame, "Source Folder (Images):")
        self.sheet_dir_selector.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        col_frame = ttk.Frame(sheet_frame)
        col_frame.grid(row=1, column=0, sticky="ew", pady=5)
        ttk.Label(col_frame, text="Columns:").pack(side=tk.LEFT)
        self.pdf_sheet_cols = ttk.Entry(col_frame, width=5)
        self.pdf_sheet_cols.insert(0, "3")
        self.pdf_sheet_cols.pack(side=tk.LEFT, padx=5)

        self.sheet_btn = ttk.Button(sheet_frame, text="Generate Contact Sheet", command=self._run_pdf_sheet)
        self.sheet_btn.grid(row=2, column=0, sticky="ew", pady=10)

        return frame

    # --- Merger Methods ---
    def _run_merger(self):
        src = self.merger_dir_selector.get()
        title = self.title_var.get()

        if not src:
            messagebox.showerror("Error", "Please select a source folder.")
            return

        dest = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            initialfile=f"{title.replace(' ', '_')}_Merged.pdf"
        )
        
        if not dest: return

        self.run_btn_merger.config(state="disabled")
        
        if self.main_window:
            self.main_window.progress_label.config(text="Starting Merge...")
            self.main_window.progress_bar['value'] = 0

        threading.Thread(target=self._thread_merger, args=(src, dest, title), daemon=True).start()

    def _update_progress_gui_merger(self, value, message):
        if self.main_window:
            self.main_window.progress_label.config(text=message)
            self.main_window.progress_bar['value'] = value

    def _thread_merger(self, src, dest, title):
        success, msg = pdf_merger.merge_pdfs_with_toc(
            src, 
            dest, 
            title, 
            progress_callback=lambda v, m: self.after(0, self._update_progress_gui_merger, v, m)
        )
        
        self.after(0, lambda: self.run_btn_merger.config(state="normal"))
        
        if self.main_window:
            self.after(0, lambda: self.main_window.progress_label.config(text="Ready."))
            self.after(0, lambda: self.main_window.progress_bar.config(value=0))
        
        self.after(0, lambda: messagebox.showinfo("Result", msg) if success else messagebox.showerror("Error", msg))

    # --- Extractor Methods ---
    def _select_extractor(self):
        f = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        if f:
            self.pdf_files = f
            self.lbl_status.config(text=f"{len(f)} files selected")

    def _run_extractor(self):
        out = self.extractor_out_selector.get()
        if not self.pdf_files or not out:
            messagebox.showerror("Error", "Select files and output folder.")
            return
        
        self.run_btn_extractor.config(state="disabled")
        
        if self.main_window:
            self.main_window.progress_label.config(text="Extracting pages...")
            self.main_window.progress_bar.config(mode='indeterminate')
            self.main_window.progress_bar.start(10)

        threading.Thread(target=self._thread_extractor, args=(self.pdf_files, out), daemon=True).start()

    def _thread_extractor(self, files, out):
        count = pdf_extractor.extract_images_from_pdfs(files, out)
        
        self.after(0, lambda: self.run_btn_extractor.config(state="normal"))
        
        if self.main_window:
            self.after(0, lambda: self.main_window.progress_label.config(text="Ready."))
            self.after(0, lambda: self.main_window.progress_bar.stop())
            self.after(0, lambda: self.main_window.progress_bar.config(mode='determinate', value=0))
            
        self.after(0, lambda: messagebox.showinfo("Done", f"Processed {count} PDFs."))

    # --- Optimizer Methods ---
    def _select_linearize_pdfs(self):
        f = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        if f:
            self.linearize_files = f
            self.lbl_linearize_status.config(text=f"{len(f)} files selected")

    def _run_linearizer(self):
        if not self.linearize_files:
            messagebox.showerror("Error", "Please select PDF files to linearize.")
            return

        self.run_btn_linearizer.grid_remove()
        self.stop_btn_linearizer.grid()
        self.stop_btn_linearizer.config(state="normal")

        if self.main_window:
            self.main_window.progress_label.config(text="Linearizing PDFs...")
            self.main_window.progress_bar['value'] = 0
        
        self.stop_event.clear()
        
        threading.Thread(target=self._thread_linearizer, args=(self.linearize_files, self.stop_event), daemon=True).start()

    def _thread_linearizer(self, files, stop_event):
        cb = lambda c, t, m: self.after(0, self._update_progress, c, t, m)
        
        success, msg = pdf_processor.batch_linearize_pdfs(
            files, progress_callback=cb, stop_event=stop_event
        )

        def cleanup_ui():
            self.stop_btn_linearizer.grid_remove()
            self.run_btn_linearizer.grid()
            if self.main_window:
                self.main_window.progress_label.config(text="Ready.")
                self.main_window.progress_bar.config(value=0)
            messagebox.showinfo("Result", msg) if success else messagebox.showerror("Error", msg)

        self.after(0, cleanup_ui)

    # --- Compiler Methods ---
    def _stop_process(self):
        self.stop_event.set()
        self.stop_btn.config(state="disabled")

    def _run_pdf_comp(self):
        path = self.compiler_dir_selector.get()
        if not path: 
            return messagebox.showerror("Error", "Select a folder.")
        
        self.stop_event.clear()
        self.generate_btn.grid_remove()
        self.stop_btn.grid()
        self.stop_btn.config(state="normal")
        
        if self.main_window:
            self.main_window.progress_label.config(text="Initializing PDF Process...")
            self.main_window.progress_bar['value'] = 0
        
        orient = self.pdf_orient_var.get()
        incl = self.pdf_filename_var.get()
        native = self.pdf_native_res_var.get()
        is_recursive = self.pdf_recursive_var.get()
        
        threading.Thread(target=self._pdf_comp_thread, args=(path, orient, incl, native, is_recursive, self.stop_event), daemon=True).start()

    def _update_progress(self, current, total, message):
        if self.main_window:
            self.main_window.progress_label.config(text=message)
            if total > 0:
                self.main_window.progress_bar['maximum'] = total
                self.main_window.progress_bar['value'] = current

    def _pdf_comp_thread(self, path, orient, incl, native, is_recursive, stop_event):
        cb = lambda c, t, m: self.after(0, self._update_progress, c, t, m)

        if is_recursive:
            success, msg = pdf_processor.batch_create_pdfs(
                path, orient, incl, native, progress_callback=cb, stop_event=stop_event
            )
        else:
            success, msg = pdf_processor.create_compilation_pdf(
                path, orient, incl, progress_callback=cb, use_native_res=native, stop_event=stop_event
            )
        
        def cleanup_ui():
            self.stop_btn.grid_remove()
            self.generate_btn.grid()
            if self.main_window:
                self.main_window.progress_label.config(text="Ready.")
                self.main_window.progress_bar.config(value=0)
            messagebox.showinfo("Result", msg) if success else messagebox.showerror("Error", msg)

        self.after(0, cleanup_ui)

    def _run_pdf_sheet(self):
        path = self.sheet_dir_selector.get()
        try:
            cols = int(self.pdf_sheet_cols.get())
        except ValueError:
            return messagebox.showerror("Error", "Columns must be a number.")

        if not path: return messagebox.showerror("Error", "Select a folder.")
        
        self.sheet_btn.config(state="disabled")
        if self.main_window:
            self.main_window.progress_label.config(text="Generating Contact Sheet...")
        
        threading.Thread(target=self._pdf_sheet_thread, args=(path, cols), daemon=True).start()

    def _pdf_sheet_thread(self, path, cols):
        success, msg = pdf_processor.create_contact_sheet_pdf(path, cols)
        
        self.after(0, lambda: self.sheet_btn.config(state="normal"))
        if self.main_window:
            self.after(0, lambda: self.main_window.progress_label.config(text="Ready."))
        
        self.after(0, lambda: messagebox.showinfo("Result", msg) if success else messagebox.showerror("Error", msg))