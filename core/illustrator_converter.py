import os
import shutil
import win32com.client
import pythoncom  # Required for threading

def get_illustrator():
    """Attempts to connect to Illustrator."""
    versions = [
        "Illustrator.Application",       # Version independent
        "Illustrator.Application.29",    # 2025
        "Illustrator.Application.28",    # 2024
        "Illustrator.Application.27",    # 2023
        "Illustrator.Application.26",    # 2022
        "Illustrator.Application.25"     # 2021
    ]
    for v in versions:
        try:
            return win32com.client.Dispatch(v)
        except Exception:
            continue
    return None

def batch_convert_to_svg(source_dir, output_dir, archive_dir, progress_callback=None):
    # 1. Initialize COM for this thread
    pythoncom.CoInitialize()
    
    try:
        ai_app = get_illustrator()
        if not ai_app:
            return False, "Could not connect to Adobe Illustrator. Is it installed?"
        
        # 2. Suppress Dialogs
        original_interaction_level = ai_app.UserInteractionLevel
        ai_app.UserInteractionLevel = -1 # aiDontDisplayAlerts
        
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
                # JavaScript requires forward slashes for paths even on Windows
                js_svg_path = svg_path.replace("\\", "/")
                
                archive_path = os.path.normpath(os.path.join(target_archive_folder, filename))

                # --- ILLUSTRATOR OPERATIONS ---
                # Open the file
                doc = ai_app.Open(os.path.abspath(file_path))
                
                try:
                    # STRATEGY CHANGE: Use 'saveAs' instead of 'exportFile'
                    # saveAs is safer because it doesn't require the strict ExportType Enum.
                    # It infers the type from the 'SVGSaveOptions' object.
                    
                    jsx_code = f'''
                    var doc = app.activeDocument;
                    var file = new File("{js_svg_path}");
                    
                    // Use SVGSaveOptions instead of ExportOptionsSVG
                    var opts = new SVGSaveOptions();
                    opts.embedRasterImages = true;
                    opts.fontSubsetting = SVGFontSubsetting.GLYPHSUSED;
                    
                    // saveAs(file, options) - No integer constant required!
                    doc.saveAs(file, opts);
                    '''
                    
                    ai_app.DoJavaScript(jsx_code)
                    
                finally:
                    doc.Close(2) # 2 = aiDoNotSaveChanges

                # Move to Archive
                if os.path.exists(archive_path):
                    os.remove(archive_path)
                shutil.move(file_path, archive_path)
                
                success_count += 1

            except Exception as e:
                # Log detailed error
                error_msg = str(e)
                if hasattr(e, 'excepinfo') and e.excepinfo:
                    error_msg = f"{e.excepinfo[2]}" 
                
                print(f"Error on {filename}: {error_msg}")
                errors.append(f"{filename}: {error_msg}")

        # 3. Restore Interaction Level
        ai_app.UserInteractionLevel = original_interaction_level
        
        msg = f"Processed {success_count}/{total_files} files."
        if errors:
            msg += f"\n\nErrors ({len(errors)}):\n" + "\n".join(errors[:5])
            
        return True, msg

    except Exception as e:
        return False, f"Critical Error: {str(e)}"