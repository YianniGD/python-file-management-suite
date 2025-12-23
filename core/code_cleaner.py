import os
import glob

def remove_lines_from_files(directory, num_lines, extension="html"):
    """
    Removes the first 'num_lines' from every file with 'extension' in 'directory'.
    """
    if not os.path.exists(directory):
        return False, "Invalid directory."

    search_pattern = os.path.join(directory, f"*.{extension.strip('.')}")
    target_files = glob.glob(search_pattern)

    if not target_files:
        return False, f"No .{extension} files found in directory."

    processed_count = 0
    errors = []

    for filepath in target_files:
        try:
            # Read all lines
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()

            if len(lines) > num_lines:
                # Keep lines after the cut
                remaining = lines[num_lines:]
                
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.writelines(remaining)
                processed_count += 1
            else:
                errors.append(f"Skipped {os.path.basename(filepath)} (Too short)")

        except Exception as e:
            errors.append(f"Error on {os.path.basename(filepath)}: {e}")

    result_msg = f"Processed {processed_count} files."
    if errors:
        result_msg += f"\n\nWarnings:\n" + "\n".join(errors[:5]) # Show first 5 errors
        if len(errors) > 5: result_msg += "\n..."

    return True, result_msg