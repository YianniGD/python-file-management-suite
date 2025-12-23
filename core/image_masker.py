import os
from PIL import Image, ImageDraw

def apply_mask(image_path, output_dir, mode="normal"):
    """
    mode: 'normal' (Keep Center) or 'inverted' (Keep Outside)
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        
        # 0 = Transparent, 255 = Opaque
        if mode == "normal":
            # Start Black (Transparent), Draw White Circle (Opaque)
            mask = Image.new('L', (width, height), 0) 
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, width, height), fill=255)
            
            # Composite: Keep pixels where mask is white
            result = Image.composite(img, Image.new("RGBA", img.size, (0,0,0,0)), mask)
            
        else: # inverted
            # Start White (Opaque), Draw Black Circle (Transparent)
            mask = Image.new('L', (width, height), 255)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, width, height), fill=0)
            
            # Apply directly to alpha channel
            result = img.copy()
            result.putalpha(mask)

        # Save
        base_name = os.path.basename(image_path)
        name, _ = os.path.splitext(base_name)
        suffix = "circular" if mode == "normal" else "inverted"
        
        output_filename = f"{name}_{suffix}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        result.save(output_path)
        return True
    except Exception as e:
        print(f"Mask Error {image_path}: {e}")
        return False