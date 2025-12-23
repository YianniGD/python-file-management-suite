import os
import shutil

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

def get_illustrator():
    """Attempts to connect to Illustrator regardless of version."""
    if not HAS_WIN32:
        return None

    versions = ["Illustrator.Application.29", "Illustrator.Application.28",
                "Illustrator.Application.27", "Illustrator.Application"]
    for v in versions:
        try:
            return win32com.client.Dispatch(v)
        except:
            continue
    return None

def batch_convert_to_pdf(source_dir, output_dir, archive_dir, progress_callback=None):
    if not HAS_WIN32:
        raise ImportError("pywin32 is not installed or supported on this system.")

    ai_app = get_illustrator()
    if not ai_app:
        raise ConnectionError("Could not connect to Adobe Illustrator. Is it installed?")

    pdf_options = win32com.client.Dispatch("Illustrator.PDFSaveOptions")
    pdf_options.PDFPreset = "[Smallest File Size]"

    count = 0
    ai_files = [os.path.join(root, f) for root, _, files in os.walk(source_dir) for f in files if f.lower().endswith('.ai')]
    total_files = len(ai_files)

    for i, file_path in enumerate(ai_files):
        if progress_callback:
            progress_callback((i + 1) / total_files * 100)
        
        filename = os.path.basename(file_path)
        relative_path = os.path.relpath(os.path.dirname(file_path), source_dir)

        # Create matching subfolders
        for base_path in [output_dir, archive_dir]:
            target_path = os.path.join(base_path, relative_path)
            if not os.path.exists(target_path):
                os.makedirs(target_path)

        pdf_path = os.path.normpath(os.path.join(output_dir, relative_path, filename.replace(".ai", ".pdf")))
        archive_path = os.path.normpath(os.path.join(archive_dir, relative_path, filename))

        doc = ai_app.Open(file_path)
        doc.SaveAs(pdf_path, pdf_options)
        doc.Close(1) # 1 = aiDoNotSaveChanges

        try:
            shutil.move(file_path, archive_path)
            count += 1
        except Exception as e:
            print(f"Error moving file {file_path}: {e}")
            continue
            
    return count
