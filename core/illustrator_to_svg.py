import os
import shutil
try:
    import win32com.client
    import pythoncom  # Required for threading
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

def get_illustrator():
    """Attempts to connect to Illustrator."""
    if not HAS_WIN32:
        return None

    versions = [
        "Illustrator.Application",       # Version independent
        "Illustrator.Application.29",    # 2025
        "Illustrator.Application.28",    # 2024
        "Illustrator.Application.27"     # 2023
    ]
    for v in versions:
        try:
            return win32com.client.Dispatch(v)
        except Exception:
            continue
    return None

def batch_convert_to_svg(source_dir, output_dir, archive_dir, progress_callback=None):
    if not HAS_WIN32:
        return False, "pywin32 is not installed or supported on this system."

    # 1. Initialize COM for this thread (Crucial for GUI apps)
    pythoncom.CoInitialize()
    
    try:
        ai_app = get_illustrator()
        if not ai_app:
            return False, "Could not connect to Adobe Illustrator. Is it installed?"
        
        # 2. Suppress Dialogs (Prevent script hanging on 'Missing Fonts')
        # -1 = aiDontDisplayAlerts
        original_interaction_level = ai_app.UserInteractionLevel
        ai_app.UserInteractionLevel = -1 

        # Setup Export Options
        svg_options = win32com.client.Dispatch("Illustrator.ExportOptionsSVG")
        svg_options.EmbedRasterImages = True
        svg_options.FontSubsetting = 2 # 2 = aiAllGlyphs (Complete font embedding)
        
        # Collect Files
        ai_files = []
        for root, _, files in os.walk(source_dir):
            for f in files:
                if f.lower().endswith('.ai'):
                    ai_files.append(os.path.join(root, f))
        
        total_files = len(ai_files)
        if total_files == 0:
            return False, "No .ai files found in source directory."

        success_count = 0
        errors = []

        for i, file_path in enumerate(ai_files):
            filename = os.path.basename(file_path)
            
            # Report Progress
            if progress_callback:
                progress_callback(i + 1, total_files, f"Processing: {filename}")

            try:
                # Calculate Paths
                relative_path = os.path.relpath(os.path.dirname(file_path), source_dir)
                
                target_svg_folder = os.path.join(output_dir, relative_path)
                target_archive_folder = os.path.join(archive_dir, relative_path)
                
                os.makedirs(target_svg_folder, exist_ok=True)
                os.makedirs(target_archive_folder, exist_ok=True)

                svg_path = os.path.normpath(os.path.join(target_svg_folder, filename.replace(".ai", ".svg")))
                archive_path = os.path.normpath(os.path.join(target_archive_folder, filename))

                # --- ILLUSTRATOR OPERATIONS ---
                # Open
                doc = ai_app.Open(os.path.abspath(file_path))
                
                try:
                    # Export (5 = aiSVG)
                    doc.Export(os.path.abspath(svg_path), 5, svg_options)
                finally:
                    # Close (2 = aiDoNotSaveChanges)
                    # Use 'finally' to ensure close happens even if export fails
                    doc.Close(2)

                # Move to Archive
                # Handle overwrite if file exists in archive
                if os.path.exists(archive_path):
                    os.remove(archive_path)
                shutil.move(file_path, archive_path)
                
                success_count += 1

            except Exception as e:
                print(f"Error on {filename}: {e}")
                errors.append(f"{filename}: {str(e)}")

        # 3. Restore Interaction Level
        ai_app.UserInteractionLevel = original_interaction_level
        
        msg = f"Processed {success_count}/{total_files} files."
        if errors:
            msg += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors[:5])
            
        return True, msg

    except Exception as e:
        return False, f"Critical Error: {str(e)}"