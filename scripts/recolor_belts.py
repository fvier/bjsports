import os
import numpy as np
from PIL import Image, ImageEnhance

def generate_all_belts():
    src_path = '/home/vier/.gemini/antigravity/brain/cd538e99-d1aa-4478-ad6a-9d15b3ad888f/.user_uploaded/media_1789355761102.png'
    src = Image.open(src_path).convert('RGBA')
    
    # Scale up using high quality Lanczos filter for crispness
    target_w, target_h = 800, 706
    src_scaled = src.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    arr = np.array(src_scaled, dtype=np.float32)
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    
    # Calculate luminance / brightness map (0 to 1)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    
    # Mask for background (very bright white pixels around the belt)
    # Background in reference image is > 240
    bg_mask = (r > 240) & (g > 240) & (b > 240)
    
    # Black sleeve bar mask in the scaled image (x from ~500 to ~700, y from ~370 to ~520)
    # Let's detect sleeve bar pixels: dark pixels (lum < 0.35) inside the belt
    bar_mask = (lum < 0.35) & (~bg_mask)
    
    # Belt fabric mask (belt body): not background and not black bar
    belt_mask = (~bg_mask) & (~bar_mask)
    
    def make_belt_image(belt_name, main_hex, bar_hex=None):
        # Convert hex to RGB float 0-1
        m_r = int(main_hex[1:3], 16) / 255.0
        m_g = int(main_hex[3:5], 16) / 255.0
        m_b = int(main_hex[5:7], 16) / 255.0
        
        out_arr = arr.copy()
        
        if belt_name == 'branca':
            # For white belt, use original image directly
            pass
        elif belt_name == 'preta':
            # For black belt: belt body is dark charcoal/black with highlights, bar is red
            # Belt body recolor
            for y in range(target_h):
                for x in range(target_w):
                    if belt_mask[y, x]:
                        l = lum[y, x]
                        # Map luminance to dark charcoal black (0.08 to 0.45)
                        v = 0.08 + l * 0.35
                        out_arr[y, x, 0] = v * 255.0
                        out_arr[y, x, 1] = v * 255.0
                        out_arr[y, x, 2] = (v + 0.02) * 255.0
            # Red rank bar recolor
            b_r, b_g, b_b = 0.86, 0.12, 0.12 # #dc2626
            for y in range(target_h):
                for x in range(target_w):
                    if bar_mask[y, x]:
                        l = lum[y, x]
                        out_arr[y, x, 0] = b_r * (0.6 + l * 0.8) * 255.0
                        out_arr[y, x, 1] = b_g * (0.6 + l * 0.8) * 255.0
                        out_arr[y, x, 2] = b_b * (0.6 + l * 0.8) * 255.0
        else:
            # For Blue, Purple, Brown belts
            for y in range(target_h):
                for x in range(target_w):
                    if belt_mask[y, x]:
                        l = lum[y, x]
                        # Preserve fabric highlights and shadows multiplying by luminance
                        factor = 0.35 + l * 0.85
                        out_arr[y, x, 0] = min(255.0, m_r * factor * 255.0)
                        out_arr[y, x, 1] = min(255.0, m_g * factor * 255.0)
                        out_arr[y, x, 2] = min(255.0, m_b * factor * 255.0)
                        
        # Create 1000x1000 canvas with clean white background
        canvas_size = 1000
        canvas = Image.new('RGB', (canvas_size, canvas_size), (255, 255, 255))
        
        belt_img = Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8), 'RGBA')
        
        # Center belt on white canvas
        pos_x = (canvas_size - target_w) // 2
        pos_y = (canvas_size - target_h) // 2
        canvas.paste(belt_img, (pos_x, pos_y), belt_img)
        
        out_file = f"/home/vier/Documentos/Code/BJ Sports/static/img/store/faixa_{belt_name}.jpg"
        canvas.save(out_file, 'JPEG', quality=95)
        print(f"Generated belt: {out_file}")

    belts_config = [
        ('branca', '#f4f4f6'),
        ('azul', '#1d4ed8'),
        ('roxa', '#7e22ce'),
        ('marrom', '#5c3a21'),
        ('preta', '#18181b')
    ]
    
    for b_name, b_hex in belts_config:
        make_belt_image(b_name, b_hex)

if __name__ == '__main__':
    generate_all_belts()
