import os
import math
import warnings
import pikepdf
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.lib.utils import ImageReader

# Suppress Pillow warnings
warnings.simplefilter('ignore', Image.DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = 200000000

def linearize_pdf(input_path, output_path):
    """Linearizes a single PDF."""
    try:
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path, linearize=True)
        return True, f"Successfully linearized {os.path.basename(input_path)}"
    except Exception as e:
        return False, f"Error linearizing {os.path.basename(input_path)}: {e}"

def batch_linearize_pdfs(pdf_files, progress_callback=None, stop_event=None):
    """Linearizes a list of PDF files."""
    total_files = len(pdf_files)
    success_count = 0
    errors = []

    for i, file_path in enumerate(pdf_files):
        if stop_event and stop_event.is_set():
            break

        if progress_callback:
            progress_callback(i + 1, total_files, os.path.basename(file_path))

        directory, filename = os.path.split(file_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(directory, f"{name}_linearized{ext}")

        success, msg = linearize_pdf(file_path, output_path)
        if success:
            success_count += 1
        else:
            errors.append(msg)

    result_msg = f"Batch linearization complete. {success_count}/{total_files} PDFs linearized."
    if errors:
        result_msg += "\n\nErrors:\n" + "\n".join(errors)

    return True, result_msg

def create_compilation_pdf(image_directory, orientation='P', include_filename=True, progress_callback=None, use_native_res=False, stop_event=None):
    """
    Core logic for 'Dark Mode' PDF compilation.
    use_native_res (bool): If True, page size equals image size (Best for Digital/Screens).
                           If False, scales image to fit US Letter (Best for Printing).
    """
    if not image_directory or not os.path.exists(image_directory):
        return False, "Invalid directory."

    directory_name = os.path.basename(image_directory)
    output_file = os.path.join(image_directory, f"{directory_name}_Compilation.pdf")

    if use_native_res:
        c = canvas.Canvas(output_file, pagesize=letter)
    else:
        page_size = landscape(letter) if orientation == 'L' else letter
        c = canvas.Canvas(output_file, pagesize=page_size)
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff')
    image_files = sorted([f for f in os.listdir(image_directory) if f.lower().endswith(image_extensions)])
    
    if not image_files:
        return False, "No supported images found."

    text_font, text_size, margin = 'Helvetica-Bold', 14, 0.25 * inch
    stopped = False

    for i, filename_with_ext in enumerate(image_files):
        if stop_event and stop_event.is_set():
            stopped = True
            break
        
        if progress_callback:
            progress_callback(i + 1, len(image_files), filename_with_ext)
            
        file_path = os.path.join(image_directory, filename_with_ext)
        filename_base = os.path.splitext(filename_with_ext)[0]
        
        try:
            with Image.open(file_path) as img:
                original_width, original_height = img.size

                if use_native_res:
                    label_height = 50 if include_filename else 0
                    page_width, page_height = original_width, original_height + label_height
                    c.setPageSize((page_width, page_height))
                    c.setFillColor(black)
                    c.rect(0, 0, page_width, page_height, fill=1)
                    c.drawImage(ImageReader(img), 0, label_height, width=original_width, height=original_height, mask='auto')
                    if include_filename:
                        c.setFillColor(white)
                        c.setFont(text_font, text_size * 2)
                        c.drawCentredString(page_width / 2, label_height / 3, filename_base)
                else:
                    page_width, page_height = c._pagesize
                    c.setFillColor(black)
                    c.rect(0, 0, page_width, page_height, fill=1)
                    c.setFillColor(white)
                    c.setFont(text_font, text_size)

                    max_drawing_width = page_width - (2 * margin)
                    max_drawing_height = page_height - (2 * margin)
                    label_space = 0.5 * inch
                    height_adjustment = label_space if include_filename else 0
                    max_img_height = max_drawing_height - height_adjustment
                    scale = min(max_drawing_width / original_width, max_img_height / original_height)
                    final_width, final_height = original_width * scale, original_height * scale
                    img_x = (page_width - final_width) / 2
                    content_height = final_height + height_adjustment
                    top_margin = (page_height - content_height) / 2
                    img_y = top_margin + height_adjustment
                    c.drawImage(ImageReader(img), img_x, img_y, width=final_width, height=final_height, mask='auto')
                    if include_filename:
                        c.drawCentredString(page_width / 2, margin / 2, filename_base)
                c.showPage()
        except Exception as e:
            print(f"Error on {filename_with_ext}: {e}")

    if stopped:
        c.save() # Save to close the file handle
        if os.path.exists(output_file):
            os.remove(output_file) # Delete the incomplete file
        return False, "PDF generation stopped by user."
    
    c.save()
    return True, f"PDF Saved: {output_file}"

def create_contact_sheet_pdf(input_folder, cols=3):
    """
    Core logic for 'Contact Sheet' PDF.
    """
    output_filename = os.path.join(input_folder, "Contact_Sheet.pdf")
    valid_exts = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp')
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(valid_exts)]
    files.sort()

    if not files:
        return False, "No images found."

    # Scan for Max Dimensions
    max_w, max_h = 0, 0
    for f in files:
        try:
            with Image.open(os.path.join(input_folder, f)) as img:
                max_w = max(max_w, img.width)
                max_h = max(max_h, img.height)
        except: continue

    if max_w == 0: return False, "Could not read images."

    # Setup
    TEXT_HEIGHT = 60
    FONT_SIZE = 24
    cell_w, cell_h = max_w, max_h + TEXT_HEIGHT
    rows = math.ceil(len(files) / cols)
    
    c = canvas.Canvas(output_filename, pagesize=(cell_w * cols, cell_h * rows))
    c.setFont("Helvetica", FONT_SIZE)

    current_col, current_row = 0, 0
    
    for f in files:
        filepath = os.path.join(input_folder, f)
        try:
            with Image.open(filepath) as img:
                img_w, img_h = img.size
                
                x_base = current_col * cell_w
                y_base = (cell_h * rows) - ((current_row + 1) * cell_h) # PDF coords start bottom-left

                x_img = x_base + (cell_w - img_w) / 2
                y_img = y_base + TEXT_HEIGHT + (max_h - img_h) / 2
                
                # Pass the PIL image object directly and use mask='auto'
                c.drawImage(ImageReader(img), x_img, y_img, width=img_w, height=img_h, mask='auto')
                c.drawCentredString(x_base + cell_w/2, y_base + 20, os.path.splitext(f)[0])

        except Exception as e:
            print(f"Error creating contact sheet for {f}: {e}")


        current_col += 1
        if current_col >= cols:
            current_col, current_row = 0, current_row + 1

    c.save()
    return True, f"Sheet Saved: {output_filename}"

def batch_create_pdfs(parent_directory, orientation='P', include_filename=True, use_native_res=False, progress_callback=None, stop_event=None):
    """
    Scans the parent_directory for subfolders and creates a PDF for each one.
    """
    if not parent_directory or not os.path.exists(parent_directory):
        return False, "Invalid directory."

    subfolders = [f.path for f in os.scandir(parent_directory) if f.is_dir()]
    
    if not subfolders:
        return False, "No subfolders found in the selected directory."

    success_count = 0
    total_folders = len(subfolders)
    errors = []
    stopped = False

    for i, folder in enumerate(subfolders):
        if stop_event and stop_event.is_set():
            stopped = True
            break
        
        folder_name = os.path.basename(folder)
        
        if progress_callback:
            progress_callback(i + 1, total_folders, f"Folder: {folder_name}")

        # Pass the stop_event down to the single PDF creation function
        success, msg = create_compilation_pdf(
            folder, orientation, include_filename, None, use_native_res, stop_event=stop_event
        )
        
        if success:
            success_count += 1
        else:
            # If the sub-process was stopped, we should also stop the batch.
            if "stopped by user" in msg:
                stopped = True
                break
            errors.append(f"{folder_name}: {msg}")

    result_msg = f"Batch Complete. Created {success_count}/{total_folders} PDFs."
    if stopped:
        result_msg = f"Batch process stopped by user. {success_count} of {total_folders} PDFs were completed."
    elif errors:
        result_msg += f"\n\nErrors:\n" + "\n".join(errors)
        
    return True, result_msg
