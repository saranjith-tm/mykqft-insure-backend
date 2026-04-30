import io
from typing import List
from PIL import Image, ImageEnhance

def crop_and_enhance_region(
    page_image_bytes: bytes, 
    polygon: List[float], 
    page_width: float, 
    page_height: float,
    padding: float = 0.15
) -> bytes:
    """Crops a region from an image based on polygon coordinates and enhances it."""
    pil_img = Image.open(io.BytesIO(page_image_bytes))
    img_w, img_h = pil_img.size
    
    xs = [polygon[i] for i in range(0, len(polygon), 2)]
    ys = [polygon[i] for i in range(1, len(polygon), 2)]
    
    rel_xmin = min(xs) / page_width
    rel_xmax = max(xs) / page_width
    rel_ymin = min(ys) / page_height
    rel_ymax = max(ys) / page_height
    
    # Add padding
    pad_x = (rel_xmax - rel_xmin) * padding
    pad_y = (rel_ymax - rel_ymin) * padding
    
    left = max(0, int((rel_xmin - pad_x) * img_w))
    right = min(img_w, int((rel_xmax + pad_x) * img_w))
    top = max(0, int((rel_ymin - pad_y) * img_h))
    bottom = min(img_h, int((rel_ymax + pad_y) * img_h))
    
    cropped = pil_img.crop((left, top, right, bottom))
    
    # Enhance
    cropped = ImageEnhance.Sharpness(cropped).enhance(2.0)
    cropped = ImageEnhance.Contrast(cropped).enhance(1.5)
    cropped = ImageEnhance.Brightness(cropped).enhance(1.1)
    
    out_io = io.BytesIO()
    cropped.save(out_io, format="PNG")
    return out_io.getvalue()
