import os
import math
import xml.etree.ElementTree as ET

# Configuration defaults
DEFAULT_ITEM_SIZE = 200    
DEFAULT_PADDING = 20       
DEFAULT_COLUMNS = 10       

def strip_namespace(element):
    """Clean namespace prefixes to prevent Illustrator errors."""
    if element.tag.startswith("{"):
        element.tag = element.tag.split('}', 1)[1]
    keys = list(element.attrib.keys())
    for key in keys:
        if key.startswith("{"):
            new_key = key.split('}', 1)[1]
            element.attrib[new_key] = element.attrib.pop(key)
    for child in element:
        strip_namespace(child)

def merge_svgs_to_grid(input_folder, item_size=DEFAULT_ITEM_SIZE, padding=DEFAULT_PADDING, columns=DEFAULT_COLUMNS):
    """
    Core logic to merge SVGs. 
    Returns: (success_boolean, message_string)
    """
    if not input_folder or not os.path.exists(input_folder):
        return False, "Invalid input folder."

    # Determine output filename automatically
    output_file = os.path.join(os.path.dirname(input_folder), 'master_grid_sorted.svg')
    
    files = [f for f in os.listdir(input_folder) if f.endswith('.svg')]
    files.sort()
    
    if not files:
        return False, "No SVGs found in the selected folder."

    # Calculate Canvas Size
    total_items = len(files)
    rows = math.ceil(total_items / columns)
    canvas_width = (item_size + padding) * columns
    canvas_height = (item_size + padding) * rows

    ET.register_namespace('', "http://www.w3.org/2000/svg")
    master_root = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'version': '1.1',
        'viewBox': f'0 0 {canvas_width} {canvas_height}'
    })

    processed_count = 0
    errors = []

    for index, filename in enumerate(files):
        file_path = os.path.join(input_folder, filename)
        layer_name = os.path.splitext(filename)[0]
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            strip_namespace(root)

            # Grid Math
            col = index % columns
            row = index // columns
            x_pos = col * (item_size + padding)
            y_pos = row * (item_size + padding)

            new_group = ET.Element('g', {
                'id': layer_name,
                'transform': f'translate({x_pos}, {y_pos})'
            })
            
            for child in root:
                new_group.append(child)
            
            # Insert at 0 (Reverse Layer Order fix)
            master_root.insert(0, new_group)
            processed_count += 1
            
        except Exception as e:
            errors.append(f"{filename}: {e}")

    # Write final file
    try:
        tree = ET.ElementTree(master_root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        return False, f"Failed to save file: {e}"

    result_msg = f"Success! Merged {processed_count} SVGs.\nSaved to: {output_file}"
    if errors:
        result_msg += f"\n\nSkipped {len(errors)} files due to errors."
    
    return True, result_msg