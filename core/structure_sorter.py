import os
import shutil

def consolidate_single_files(directory):
    """
    Moves files from subfolders that contain EXACTLY ONE item 
    into a 'Singles_Consolidated' folder, then deletes the empty subfolder.
    """
    if not os.path.exists(directory): return False, "Invalid Path"
    
    target_dir = os.path.join(directory, "Singles_Consolidated")
    os.makedirs(target_dir, exist_ok=True)
    
    moved = 0
    deleted_folders = 0
    
    for item in os.listdir(directory):
        sub_path = os.path.join(directory, item)
        
        if os.path.isdir(sub_path) and sub_path != target_dir:
            contents = os.listdir(sub_path)
            
            if len(contents) == 1:
                file_name = contents[0]
                src = os.path.join(sub_path, file_name)
                
                if os.path.isfile(src):
                    try:
                        shutil.move(src, os.path.join(target_dir, file_name))
                        os.rmdir(sub_path)
                        moved += 1
                        deleted_folders += 1
                    except Exception as e:
                        print(f"Error processing {sub_path}: {e}")

    return True, f"Consolidated {moved} files.\nRemoved {deleted_folders} empty folders."

def sort_by_extension(source_dirs, centralize=False, progress_callback=None):
    """
    Scans folders and moves files into subfolders by extension.
    centralize (bool): 
        If True: Moves ALL files to the main source directory (source_dirs[0]).
        If False: Sorts files into subfolders relative to where they were found.
    """
    moved_count = 0
    
    # 1. Scan for files
    files_to_move = []
    for d in source_dirs:
        for root, _, files in os.walk(d):
            # Avoid processing folders we just created
            if "_Files" in os.path.basename(root): 
                continue
                
            for f in files:
                files_to_move.append((root, f))
    
    total_files = len(files_to_move)
    main_root = source_dirs[0] # The main folder selected by the user
    
    # 2. Process Moves
    for i, (current_root, filename) in enumerate(files_to_move):
        if progress_callback:
            progress_callback(i+1, total_files, f"Sorting {filename}")
            
        ext = os.path.splitext(filename)[1].strip('.').upper()
        if not ext: ext = "NO_EXT"
        
        folder_name = f"{ext}_Files"
        
        # LOGIC SWITCH
        if centralize:
            # Move to Main Root/JPG_Files
            dest_dir = os.path.join(main_root, folder_name)
        else:
            # Move to Current Root/JPG_Files
            dest_dir = os.path.join(current_root, folder_name)
        
        try:
            os.makedirs(dest_dir, exist_ok=True)
            
            # Handle duplicate filenames if centralizing
            dest_path = os.path.join(dest_dir, filename)
            if os.path.exists(dest_path):
                base, extension = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(dest_dir, f"{base}_{counter}{extension}")):
                    counter += 1
                dest_path = os.path.join(dest_dir, f"{base}_{counter}{extension}")

            shutil.move(os.path.join(current_root, filename), dest_path)
            moved_count += 1
        except Exception as e: 
            print(f"Error moving {filename}: {e}")

    return True, f"Sorted {moved_count} files by file type."