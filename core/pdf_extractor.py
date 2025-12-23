import os
import fitz  # PyMuPDF

def extract_pages_as_images(pdf_paths, output_root, zoom=2):
    processed_count = 0
    for pdf_path in pdf_paths:
        try:
            pdf_filename_base = os.path.splitext(os.path.basename(pdf_path))[0]
            output_folder = os.path.join(output_root, pdf_filename_base)
            os.makedirs(output_folder, exist_ok=True)

            doc = fitz.open(pdf_path)
            matrix = fitz.Matrix(zoom, zoom)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=matrix)
                output_filename = f"{pdf_filename_base}_page_{page_num + 1:02d}.png"
                pix.save(os.path.join(output_folder, output_filename))
            
            doc.close()
            processed_count += 1
        except Exception as e:
            print(f"Error extracting {pdf_path}: {e}")
            
    return processed_count