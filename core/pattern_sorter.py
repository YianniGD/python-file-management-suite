import os
import re
import shutil

def sort_by_name_pattern(directory, pattern_regex, min_files=2):
    """
    Sorts files based on a regex pattern.
    Uses re.search() to find the pattern ANYWHERE in the filename.
    """
    if not directory or not os.path.isdir(directory):
        return False, "Invalid directory."

    try:
        # We compile the regex provided by the UI
        pattern = re.compile(pattern_regex)
    except re.error:
        return False, "Invalid Regular Expression pattern."

    # --- PASS 1: SCAN AND GROUP ---
    groups = {}
    potential_folders = set()

    for root, dirs, files in os.walk(directory):
        # Prevent recursing into folders we just created
        dirs[:] = [d for d in dirs if d not in potential_folders]

        for filename in files:
            if filename.startswith('.'): continue
            
            # CHANGE: .search() looks anywhere in the string. 
            # .match() only looked at the beginning.
            match = pattern.search(filename)
            
            if match:
                # Combine capture groups to make the folder name
                # If your regex is "(BW)", it captures "BW" -> Folder "bw"
                parts = [g for g in match.groups() if g]
                
                if not parts: 
                    continue # Pattern matched but no capturing group () defined
                
                # Create a clean folder name
                folder_name = "_".join(parts).lower().strip()
                
                if folder_name not in groups:
                    groups[folder_name] = []
                    potential_folders.add(folder_name)
                
                full_path = os.path.join(root, filename)
                groups[folder_name].append(full_path)

    # --- PASS 2: FILTER AND MOVE ---
    moved_count = 0
    folders_created = 0
    
    for folder_name, file_paths in groups.items():
        # THRESHOLD CHECK
        if len(file_paths) < min_files:
            continue 

        dest_dir = os.path.join(directory, folder_name)
        
        try:
            os.makedirs(dest_dir, exist_ok=True)
            folders_created += 1
            
            for src in file_paths:
                filename = os.path.basename(src)
                dest = os.path.join(dest_dir, filename)
                
                # Handle duplicates
                if os.path.exists(dest):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(os.path.join(dest_dir, f"{base}_{counter}{ext}")):
                        counter += 1
                    dest = os.path.join(dest_dir, f"{base}_{counter}{ext}")

                shutil.move(src, dest)
                moved_count += 1
                
        except Exception as e:
            print(f"Error processing group {folder_name}: {e}")

    if moved_count == 0:
        return True, "Scan complete. No files matched the pattern (or met the threshold)."
        
    return True, f"Sorted {moved_count} files into {folders_created} folders."