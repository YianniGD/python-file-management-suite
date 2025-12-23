import os
import shutil
import hashlib
from PIL import Image

# --- IMAGE BATCHING LOGIC ---
def batch_process_images(source_dir, dest_dir, percentage, output_format, quality, progress_callback=None):
    supported_formats = ["jpeg", "png", "webp", "bmp", "gif", "tiff"]
    image_files = [f for f in os.listdir(source_dir) if f.lower().endswith(tuple(f".{fmt}" for fmt in supported_formats))]
    total_files = len(image_files)

    for i, filename in enumerate(image_files):
        if progress_callback:
            progress_callback(i + 1, total_files, filename)

        try:
            img_path = os.path.join(source_dir, filename)
            img = Image.open(img_path)

            new_size = (int(img.width * percentage), int(img.height * percentage))
            img = img.resize(new_size, Image.LANCZOS)

            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}.{output_format.lower()}"
            output_path = os.path.join(dest_dir, output_filename)

            counter = 0
            while os.path.exists(output_path):
                counter += 1
                output_filename = f"{base_name}({counter}).{output_format.lower()}"
                output_path = os.path.join(dest_dir, output_filename)

            if output_format.lower() in ['jpeg', 'webp']:
                img.save(output_path, quality=quality, optimize=True)
            else:
                img.save(output_path)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    return total_files

# --- SPLITTER LOGIC ---
def get_image_files_in_directory(dir_path):
    supported_formats = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
    image_files = []
    for root, _, files in os.walk(dir_path):
        for filename in files:
            if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                image_files.append(os.path.join(root, filename))
    return image_files

def split_image_into_grid(image_path, tile_size=None, grid_size=None):
    try:
        with Image.open(image_path).convert("RGBA") as img:
            img_width, img_height = img.size

            if grid_size:
                rows, cols = grid_size
                tile_width = img_width // cols
                tile_height = img_height // rows
            elif tile_size:
                tile_width, tile_height = tile_size
            else:
                raise ValueError("Must provide either tile_size or grid_size.")

            if tile_width <= 0 or tile_height <= 0:
                raise ValueError("Calculated tile size is not valid.")

            image_name = os.path.splitext(os.path.basename(image_path))[0]
            output_dir = os.path.join(os.path.dirname(image_path), f"output_tiles_{image_name}")
            os.makedirs(output_dir, exist_ok=True)
            
            for y in range(0, img_height, tile_height):
                for x in range(0, img_width, tile_width):
                    left, upper = x, y
                    right, lower = x + tile_width, y + tile_height
                    tile = img.crop((left, upper, right, lower))

                    if tile.getbbox():
                        tile_name = f"tile_{x}_{y}.png"
                        tile.save(os.path.join(output_dir, tile_name))
            return True
    except Exception as e:
        print(f"Error splitting '{os.path.basename(image_path)}': {e}")
        return False

# --- GIF LOGIC ---
def extract_gif_frames(input_path, output_dir, is_single_file, progress_callback=None):
    extracted_frames_count = 0
    gif_paths = []

    if is_single_file:
        gif_paths = [input_path]
    else:
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith('.gif'):
                    gif_paths.append(os.path.join(root, f))
    
    total_gifs = len(gif_paths)
    for idx, gif_path in enumerate(gif_paths):
        try:
            gif_filename = os.path.basename(gif_path)
            with Image.open(gif_path) as im:
                total_frames_in_gif = im.n_frames
                for i in range(total_frames_in_gif):
                    im.seek(i)
                    frame_filename = f"{os.path.splitext(gif_filename)[0]}_frame_{i:04d}.png"
                    frame_path = os.path.join(output_dir, frame_filename)
                    im.save(frame_path)
                    extracted_frames_count += 1
                    if progress_callback:
                        progress_callback(idx + 1, total_gifs, gif_filename, i + 1, total_frames_in_gif)
        except Exception as e:
            print(f"Error extracting frames from {gif_path}: {e}")

    return extracted_frames_count

# --- SORTER LOGIC ---
def scan_extensions(source_dir):
    unique_extensions = set()
    for root, _, files in os.walk(source_dir):
        for file_name in files:
            _, file_extension = os.path.splitext(file_name)
            file_extension = file_extension.lstrip('.').lower()
            if not file_extension:
                unique_extensions.add("no_extension")
            else:
                unique_extensions.add(file_extension)
    return sorted(list(unique_extensions))

def sort_files(source_dir, selected_ext, progress_callback=None):
    if selected_ext == "no_extension":
        destination_folder_name = "no_extension"
    else:
        destination_folder_name = f"{selected_ext}_files"
    destination_folder = os.path.join(source_dir, destination_folder_name)

    os.makedirs(destination_folder, exist_ok=True)

    files_to_move_info = []
    for root, _, files in os.walk(source_dir):
        if os.path.abspath(root) == os.path.abspath(destination_folder):
            continue
        for file_name in files:
            full_original_path = os.path.join(root, file_name)
            _, file_extension = os.path.splitext(file_name)
            file_extension = file_extension.lstrip('.').lower()

            if (selected_ext == "no_extension" and not file_extension) or \
               (selected_ext != "no_extension" and file_extension == selected_ext):
                files_to_move_info.append((full_original_path, file_name))
    
    total_files = len(files_to_move_info)
    moved_count = 0
    skipped_count = 0
    
    for i, (original_full_path, file_name_only) in enumerate(files_to_move_info):
        if progress_callback:
            progress_callback(i + 1, total_files, file_name_only)
        
        try:
            unique_filename = _get_unique_filename(destination_folder, file_name_only)
            destination_path = os.path.join(destination_folder, unique_filename)
            shutil.move(original_full_path, destination_path)
            moved_count += 1
        except Exception:
            skipped_count += 1
    
    return moved_count, skipped_count

def _get_unique_filename(destination_folder, original_filename):
    base_name, extension = os.path.splitext(original_filename)
    counter = 0
    new_filename = original_filename
    while os.path.exists(os.path.join(destination_folder, new_filename)):
        counter += 1
        new_filename = f"{base_name}({counter}){extension}"
    return new_filename