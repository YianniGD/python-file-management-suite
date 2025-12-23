import os
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def merge_pdfs_with_toc(source_folder, output_path, title_text="Compilation", progress_callback=None):
    """
    Merges all PDFs, generates a Title Page + TOC, and adds CLICKABLE bookmarks.
    progress_callback: function(percentage_int, status_string)
    """
    if not source_folder or not os.path.exists(source_folder):
        return False, "Invalid directory."

    # 1. Gather PDF files
    pdf_files = sorted([
        f for f in os.listdir(source_folder) 
        if f.lower().endswith('.pdf')
    ])
    
    if not pdf_files:
        return False, "No PDF files found in directory."

    total_files = len(pdf_files)

    # 2. Pass 1: Analyze Page Counts (Weights 0-10% of progress)
    file_info = [] 
    
    for i, f in enumerate(pdf_files):
        if progress_callback:
            # Scale 0-10%
            pct = int((i / total_files) * 10)
            progress_callback(pct, f"Analyzing page counts: {f}")

        path = os.path.join(source_folder, f)
        try:
            doc = fitz.open(path)
            count = doc.page_count
            doc.close()
            file_info.append({
                "name": os.path.splitext(f)[0],
                "pages": count,
                "path": path
            })
        except Exception as e:
            print(f"Skipping {f}: {e}")

    if not file_info:
        return False, "Could not read any PDF files."

    # 3. Calculate Layout
    if progress_callback: progress_callback(10, "Generating Table of Contents...")
    
    lines_per_page = 35
    toc_pages = (len(file_info) // lines_per_page) + 1
    front_matter_length = 1 + toc_pages
    
    # 4. Generate Front Matter (Title + TOC)
    temp_front_matter = os.path.join(source_folder, "temp_front_matter.pdf")
    c = canvas.Canvas(temp_front_matter, pagesize=letter)
    width, height = letter

    # --- Draw Title Page ---
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width / 2, height / 2, title_text)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, (height / 2) - 50, f"Generated from {len(file_info)} files")
    c.showPage() 

    # --- Draw Table of Contents ---
    c.setFont("Helvetica-Bold", 24)
    c.drawString(inch, height - inch, "Table of Contents")
    c.setFont("Helvetica", 12)
    
    current_y = height - (1.5 * inch)
    current_page_number = front_matter_length + 1 
    
    searchable_names = []

    for item in file_info:
        if current_y < inch:
            c.showPage()
            current_y = height - inch
            c.setFont("Helvetica", 12)

        name = item['name'][:60] 
        searchable_names.append(name)
        
        c.drawString(inch, current_y, name)
        c.drawRightString(width - inch, current_y, str(current_page_number))
        
        dot_start = inch + c.stringWidth(name, "Helvetica", 12) + 5
        dot_end = width - inch - 30
        if dot_end > dot_start:
            c.drawString(dot_start, current_y, "." * int((dot_end - dot_start) / 4))

        current_y -= 20
        current_page_number += item['pages']

    c.save() 

    # 5. Merge Everything (Weights 10-60% of progress)
    try:
        final_doc = fitz.open()
        
        # A. Insert Front Matter
        front_doc = fitz.open(temp_front_matter)
        final_doc.insert_pdf(front_doc)
        front_doc.close()

        # B. Insert All Content PDFs
        toc_data = [] 
        toc_data.append([1, title_text, 1]) 
        toc_data.append([1, "Table of Contents", 2]) 
        
        current_page_cursor = front_matter_length + 1

        for i, item in enumerate(file_info):
            if progress_callback:
                # Scale 10-60%
                pct = 10 + int((i / len(file_info)) * 50)
                progress_callback(pct, f"Merging file: {item['name']}")

            doc = fitz.open(item['path'])
            final_doc.insert_pdf(doc)
            doc.close()
            
            toc_data.append([1, item['name'], current_page_cursor])
            current_page_cursor += item['pages']

        final_doc.set_toc(toc_data)

        # 6. Pass 3: Create Clickable Links (Weights 60-95% of progress)
        link_cursor = front_matter_length + 1
        
        for i, name_text in enumerate(searchable_names):
            if progress_callback:
                # Scale 60-95%
                pct = 60 + int((i / len(searchable_names)) * 35)
                progress_callback(pct, f"Creating link for: {name_text}")

            target_page_index = link_cursor - 1
            
            for p_idx in range(1, front_matter_length + 1):
                page = final_doc[p_idx]
                rects = page.search_for(name_text)
                
                if rects:
                    click_rect = rects[0]
                    click_rect.x1 = width - inch
                    
                    page.insert_link({
                        "kind": fitz.LINK_GOTO,
                        "page": target_page_index,
                        "from": click_rect
                    })
                    break 
            
            link_cursor += file_info[i]['pages']

        # Save (Final 5%)
        if progress_callback: progress_callback(95, "Saving final document...")
        final_doc.save(output_path)
        final_doc.close()

        if os.path.exists(temp_front_matter):
            os.remove(temp_front_matter)
        
        if progress_callback: progress_callback(100, "Done!")
        return True, f"Merged PDF saved to:\n{output_path}"

    except Exception as e:
        return False, f"Merge Error: {e}"