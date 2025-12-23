import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from core import pattern_sorter, structure_sorter
from core import photo_organizer

class SortingToolsTab(ttk.Frame):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, padding=10)
        self.main_window = main_window

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        pattern_frame = self._create_pattern_sort_tab(notebook)
        structure_frame = self._create_structure_sort_tab(notebook)
        # ADDED: New internal tab
        photo_frame = self._create_photo_sort_tab(notebook)

        notebook.add(pattern_frame, text="Pattern Sorter")
        notebook.add(structure_frame, text="Structure Sorter")
        notebook.add(photo_frame, text="Photo/Date Sorter") # ADDED

    def _create_pattern_sort_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)

        # --- Pattern Sorter UI ---
        self.PATTERNS = {
            "First 2 Words (Default)": r'^([a-zA-Z0-9]+)[^a-zA-Z0-9]+([a-zA-Z0-9]+)',
            "First Word Only": r'^([a-zA-Z0-9]+)',
            "First 3 Words": r'^([a-zA-Z0-9]+)[^a-zA-Z0-9]+([a-zA-Z0-9]+)[^a-zA-Z0-9]+([a-zA-Z0-9]+)',
            "Date (YYYY-MM-DD)": r'^(\d{4}-\d{2}-\d{2})',
            "Custom Pattern": "" 
        }

        container = ttk.LabelFrame(frame, text="Regex Pattern Sort", padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="Sorts files into folders based on naming patterns.", wraplength=400).pack(anchor="w", pady=(0,10))

        ttk.Label(container, text="Target Directory:").pack(anchor="w")
        self.src_pattern = tk.StringVar()
        entry_frame = ttk.Frame(container)
        entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(entry_frame, textvariable=self.src_pattern).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(entry_frame, text="Browse", command=self._browse_pattern).pack(side=tk.LEFT, padx=5)

        config_frame = ttk.LabelFrame(container, text="Sort Configuration", padding=10)
        config_frame.pack(fill=tk.X, pady=15)

        ttk.Label(config_frame, text="Grouping Pattern:").grid(row=0, column=0, sticky="w", pady=5)
        self.pattern_var = tk.StringVar(value="First 2 Words (Default)")
        self.combo_pattern = ttk.Combobox(config_frame, textvariable=self.pattern_var, values=list(self.PATTERNS.keys()), state="readonly")
        self.combo_pattern.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.combo_pattern.bind("<<ComboboxSelected>>", self._on_pattern_change)

        self.custom_regex_var = tk.StringVar()
        self.entry_custom = ttk.Entry(config_frame, textvariable=self.custom_regex_var)
        self.lbl_custom = ttk.Label(config_frame, text="Regex:")
        
        ttk.Label(config_frame, text="Minimum Files to Create Folder:").grid(row=2, column=0, sticky="w", pady=5)
        self.threshold_var = tk.IntVar(value=2)
        spin = ttk.Spinbox(config_frame, from_=1, to=100, textvariable=self.threshold_var, width=5)
        spin.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # Grid row 3: Ignore Spaces
        self.ignore_spaces_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Ignore spaces in filenames (for matching)", variable=self.ignore_spaces_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        # Grid row 4: Character Limit
        self.char_limit_enabled_var = tk.BooleanVar(value=False)
        self.char_limit_var = tk.IntVar(value=15)
        
        char_limit_frame = ttk.Frame(config_frame)
        char_limit_frame.grid(row=4, column=0, columnspan=2, sticky="w")
        
        self.char_limit_check = ttk.Checkbutton(char_limit_frame, text="Limit match to first", variable=self.char_limit_enabled_var, command=self._toggle_char_limit)
        self.char_limit_check.pack(side=tk.LEFT)
        
        self.char_limit_spinbox = ttk.Spinbox(char_limit_frame, from_=1, to=100, textvariable=self.char_limit_var, width=5, state="disabled")
        self.char_limit_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(char_limit_frame, text="characters").pack(side=tk.LEFT)

        ttk.Button(container, text="Analyze and Sort", command=self._run_pattern).pack(fill=tk.X, pady=20)
        return frame

    def _create_structure_sort_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)

        # --- Structure Sorter UI ---
        f1 = ttk.LabelFrame(frame, text="Consolidate Single-File Folders", padding=10)
        f1.pack(fill=tk.X, pady=10)
        
        ttk.Label(f1, text="Moves files out of subfolders that contain only 1 item.", wraplength=350).pack(anchor="w")
        
        row1 = ttk.Frame(f1)
        row1.pack(fill=tk.X, pady=5)
        self.path1_structure = tk.StringVar()
        ttk.Entry(row1, textvariable=self.path1_structure).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row1, text="Browse", command=lambda: self._browse_structure(self.path1_structure)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(f1, text="Run Consolidation", command=self._run_consolidate).pack(fill=tk.X, pady=5)

        f2 = ttk.LabelFrame(frame, text="Sort by Extension", padding=10)
        f2.pack(fill=tk.X, pady=10)
        
        ttk.Label(f2, text="Organizes all files in a folder into /JPG_Files, /PDF_Files, etc.", wraplength=350).pack(anchor="w")
        
        row2 = ttk.Frame(f2)
        row2.pack(fill=tk.X, pady=5)
        self.path2_structure = tk.StringVar()
        ttk.Entry(row2, textvariable=self.path2_structure).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row2, text="Browse", command=lambda: self._browse_structure(self.path2_structure)).pack(side=tk.LEFT, padx=5)
        
        self.centralize_var = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(f2, text="Move ALL files to main directory (Flatten Subfolders)", variable=self.centralize_var)
        chk.pack(anchor="w", pady=5)
        
        self.run_ext_btn = ttk.Button(f2, text="Run Extension Sort", command=self._run_ext)
        self.run_ext_btn.pack(fill=tk.X, pady=5)

        f3 = ttk.LabelFrame(frame, text="Delete Empty Folders", padding=10)
        f3.pack(fill=tk.X, pady=10)
        
        ttk.Label(f3, text="Scans the selected directory and removes any empty subfolders.", wraplength=350).pack(anchor="w")
        
        row3 = ttk.Frame(f3)
        row3.pack(fill=tk.X, pady=5)
        self.path3_structure = tk.StringVar()
        ttk.Entry(row3, textvariable=self.path3_structure).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row3, text="Browse", command=lambda: self._browse_structure(self.path3_structure)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(f3, text="Find and Delete Empty Folders", command=self._run_delete_empty).pack(fill=tk.X, pady=5)

        return frame

    def _toggle_char_limit(self):
        state = "normal" if self.char_limit_enabled_var.get() else "disabled"
        self.char_limit_spinbox.config(state=state)

    def _create_photo_sort_tab(self, parent):
        frame = ttk.Frame(parent, padding=10)
        
        container = ttk.LabelFrame(frame, text="Sort by Metadata (EXIF)", padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Organizes images into folders based on the date they were taken.", 
                  wraplength=400).pack(anchor="w", pady=(0,10))

        ttk.Label(container, text="Target Directory:").pack(anchor="w")
        self.src_photo = tk.StringVar()
        row = ttk.Frame(container)
        row.pack(fill=tk.X, pady=5)
        ttk.Entry(row, textvariable=self.src_photo).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Browse", command=lambda: self.src_photo.set(filedialog.askdirectory())).pack(side=tk.LEFT, padx=5)

        config_frame = ttk.LabelFrame(container, text="Sort Configuration", padding=10)
        config_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(config_frame, text="Folder Structure (e.g., %Y/%m):").grid(row=0, column=0, sticky="w", pady=5)
        self.photo_fmt = tk.StringVar(value="%Y/%m-%b")
        ttk.Entry(config_frame, textvariable=self.photo_fmt).grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(config_frame, text="Rename Format (optional):").grid(row=1, column=0, sticky="w", pady=5)
        self.photo_rename_fmt = tk.StringVar(value="")
        ttk.Entry(config_frame, textvariable=self.photo_rename_fmt).grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        self.photo_recursive = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Search Recursively", variable=self.photo_recursive).grid(row=2, column=0, sticky="w", pady=5)

        self.photo_copy = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Copy Files (instead of move)", variable=self.photo_copy).grid(row=3, column=0, sticky="w", pady=5)

        self.photo_keep_filename = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Keep Original Filename on Duplicate", variable=self.photo_keep_filename).grid(row=4, column=0, sticky="w", pady=5)


        self.run_photo_sort_btn = ttk.Button(container, text="Run Photo Organizer", command=self._run_photo_sort)
        self.run_photo_sort_btn.pack(fill=tk.X, pady=20)
        
        return frame

    # --- Pattern Sorter Methods ---
    def _browse_pattern(self):
        d = filedialog.askdirectory()
        if d: self.src_pattern.set(d)

    def _on_pattern_change(self, event=None):
        selection = self.pattern_var.get()
        if selection == "Custom Pattern":
            self.lbl_custom.grid(row=1, column=0, sticky="e", padx=5)
            self.entry_custom.grid(row=1, column=1, sticky="ew", padx=10)
        else:
            self.lbl_custom.grid_remove()
            self.entry_custom.grid_remove()

    def _run_pattern(self):
        directory = self.src_pattern.get()
        if not directory: return messagebox.showerror("Error", "Select a folder.")
        
        selection = self.pattern_var.get()
        if selection == "Custom Pattern":
            regex = self.custom_regex_var.get()
            if not regex: return messagebox.showerror("Error", "Please enter a Custom Regex pattern.")
        else:
            regex = self.PATTERNS[selection]

        try:
            min_count = self.threshold_var.get()
        except:
            min_count = 1
        
        ignore_spaces = self.ignore_spaces_var.get()
        char_count = None
        if self.char_limit_enabled_var.get():
            try:
                char_count = self.char_limit_var.get()
            except tk.TclError:
                messagebox.showerror("Error", "Invalid character count value.")
                return

        if self.main_window:
            self.main_window.progress_label.config(text="Scanning file patterns...")

        success, msg = pattern_sorter.sort_by_name_pattern(directory, regex, min_count, ignore_spaces, char_count)
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")

        messagebox.showinfo("Result", msg)

    # --- Structure Sorter Methods ---
    def _browse_structure(self, var):
        d = filedialog.askdirectory()
        if d: var.set(d)

    def _run_consolidate(self):
        d = self.path1_structure.get()
        if not d: return messagebox.showerror("Error", "Select a folder.")
        
        if self.main_window:
            self.main_window.progress_label.config(text="Consolidating folders...")
            
        success, msg = structure_sorter.consolidate_single_files(d)
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            
        messagebox.showinfo("Result", msg)

    def _run_delete_empty(self):
        d = self.path3_structure.get()
        if not d: return messagebox.showerror("Error", "Select a folder.")

        if not messagebox.askyesno("Confirm", "Are you sure you want to permanently delete all empty folders in this directory? This cannot be undone."):
            return
        
        if self.main_window:
            self.main_window.progress_label.config(text="Scanning for empty folders...")
            
        success, msg = structure_sorter.delete_empty_folders(d)
        
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            
        messagebox.showinfo("Result", msg)

    def _run_ext(self):
        d = self.path2_structure.get()
        if not d: return messagebox.showerror("Error", "Select a folder.")
        
        centralize = self.centralize_var.get()
        
        self.run_ext_btn.config(state="disabled")
        
        threading.Thread(target=self._thread_ext, args=(d, centralize), daemon=True).start()

    def _thread_ext(self, d, centralize):
        def cb(curr, total, msg):
            if self.main_window:
                self.main_window.after(0, lambda: self._update_progress(curr, total, msg))

        success, msg = structure_sorter.sort_by_extension([d], centralize=centralize, progress_callback=cb)
        
        self.after(0, lambda: self._finish_ext(msg))

    def _update_progress(self, curr, total, msg):
        self.main_window.progress_label.config(text=msg)
        if total > 0:
            self.main_window.progress_bar['maximum'] = total
            self.main_window.progress_bar['value'] = curr

    def _finish_ext(self, msg):
        self.run_ext_btn.config(state="normal")
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            self.main_window.progress_bar.config(value=0)
        messagebox.showinfo("Result", msg)

    def _run_photo_sort(self):
        directory = self.src_photo.get()
        fmt = self.photo_fmt.get()
        rename_fmt = self.photo_rename_fmt.get() or None
        recursive = self.photo_recursive.get()
        copy = self.photo_copy.get()
        keep_filename = self.photo_keep_filename.get()

        if not directory: return messagebox.showerror("Error", "Select a folder.")

        def cb(curr, total, msg):
            if self.main_window:
                self.main_window.after(0, lambda: self._update_progress(curr, total, msg))

        self.run_photo_sort_btn.config(state="disabled")
        # Run in a thread so the UI doesn't freeze
        threading.Thread(target=self._thread_photo, args=(directory, fmt, rename_fmt, recursive, copy, keep_filename, cb), daemon=True).start()

    def _thread_photo(self, d, f, rename_fmt, recursive, copy, keep_filename, cb):
        success, msg = photo_organizer.organize_by_date(d, structure=f, progress_cb=cb, rename_format=rename_fmt, recursive=recursive, copy_files=copy, keep_filename=keep_filename)
        self.after(0, lambda: self._finish_photo_sort(msg))

    def _finish_photo_sort(self, msg):
        self.run_photo_sort_btn.config(state="normal")
        if self.main_window:
            self.main_window.progress_label.config(text="Ready.")
            self.main_window.progress_bar.config(value=0)
        messagebox.showinfo("Result", msg)
