import os

def rename_files_from_list(directory, names_file_path):
    """
    Renames all files in 'directory' based on a comma-separated list in 'names_file_path'.
    """
    try:
        # Read names from file (comma separated)
        with open(names_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Split by comma, strip whitespace, and filter empty strings
            new_names = [name.strip() for name in content.split(',') if name.strip()]

        # Get files sorted alphabetically so they match the order of the list
        files_to_rename = sorted([
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ])
        
        # Validation
        if len(files_to_rename) != len(new_names):
            return False, f"Mismatch: Found {len(files_to_rename)} files but {len(new_names)} names."

        renamed_count = 0
        for i, old_name in enumerate(files_to_rename):
            old_path = os.path.join(directory, old_name)
            _, file_extension = os.path.splitext(old_name)
            
            # Construct new name
            clean_new_name = new_names[i]
            new_filename = f"{clean_new_name}{file_extension}"
            new_path = os.path.join(directory, new_filename)

            os.rename(old_path, new_path)
            renamed_count += 1

        return True, f"Successfully renamed {renamed_count} files."

    except Exception as e:
        return False, f"Renaming Error: {str(e)}"