import os
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw

def get_kimono_mask(base_img):
    mask_cache = '/tmp/kimono_mask.png'
    if os.path.exists(mask_cache):
        return Image.open(mask_cache).convert('L')
    
    gray = base_img.convert('L')
    small = gray.resize((1000, 1500), Image.Resampling.BILINEAR)
    thresh = small.point(lambda p: 255 if p > 248 else 0)
    
    ImageDraw.floodfill(thresh, (0, 0), 128)
    ImageDraw.floodfill(thresh, (999, 0), 128)
    ImageDraw.floodfill(thresh, (0, 1499), 128)
    ImageDraw.floodfill(thresh, (999, 1499), 128)
    
    arr_small = np.array(thresh)
    bg_small = (arr_small == 128)
    kimono_small = Image.fromarray((~bg_small).astype(np.uint8)*255, mode='L')
    kimono_mask = kimono_small.resize(base_img.size, Image.Resampling.BILINEAR)
    kimono_mask.save(mask_cache)
    return kimono_mask

def generate_kimono_mockups():
    base_cache_path = '/tmp/psd_clean_kimono.png'
    psd_path = 'tema/loja/aquivos em PSD/kimono-mockup/b6a29b97-7b17-47a8-a007-8d5996ebb677.psd'
    
    if os.path.exists(base_cache_path):
        print(f"Loading cached clean 3D kimono base from {base_cache_path}...")
        base_img = Image.open(base_cache_path).convert('RGBA')
    else:
        print("Rendering clean 3D kimono base from PSD...")
        from psd_tools import PSDImage
        psd = PSDImage.open(psd_path)
        for layer in psd:
            if layer.name in ['DESIGN', 'BACKGROUND']:
                layer.visible = False
        base_img = psd.composite().convert('RGBA')
        base_img.save(base_cache_path)
    
    kimono_mask = get_kimono_mask(base_img)
    mask_arr = np.array(kimono_mask, dtype=np.float32) / 255.0
    
    # Load BJ Sports logos
    logo_dark_path = 'logo.png' if os.path.exists('logo.png') else 'static/img/logo_original.png'
    logo_light_path = 'static/img/logo_inverted.png' if os.path.exists('static/img/logo_inverted.png') else 'static/img/logo_transparent.png'
    
    logo_dark = Image.open(logo_dark_path).convert('RGBA') if os.path.exists(logo_dark_path) else None
    logo_light = Image.open(logo_light_path).convert('RGBA') if os.path.exists(logo_light_path) else None
    
    os.makedirs('static/img/store', exist_ok=True)
    
    def apply_patches(kimono_img, logo, chest_pos=(2150, 1680), chest_width=320, sleeve_pos=(1380, 1460), sleeve_width=200):
        if logo is None:
            return kimono_img
        res = kimono_img.copy()
        
        # 1. Left Chest Patch
        aspect = logo.height / logo.width
        chest_h = int(chest_width * aspect)
        logo_chest = logo.resize((chest_width, chest_h), Image.Resampling.LANCZOS)
        res.paste(logo_chest, chest_pos, logo_chest)
        
        # 2. Sleeve Patch
        if sleeve_pos:
            sleeve_h = int(sleeve_width * aspect)
            logo_sleeve = logo.resize((sleeve_width, sleeve_h), Image.Resampling.LANCZOS)
            res.paste(logo_sleeve, sleeve_pos, logo_sleeve)
            
        return res

    # Clean dark studio background #12141c for product cards
    crop_box = (850, 750, 3150, 5250)

    # Base luminance from unbranded kimono image
    gray_img = np.array(base_img.convert('L'), dtype=np.float32)
    norm_gray = gray_img / 255.0

    # -------------------------------------------------------------
    # 1. KIMONO BRANCO (White)
    # -------------------------------------------------------------
    print("Generating Kimono Branco...")
    white_val = gray_img
    r_w = (18 * (1 - mask_arr) + white_val * mask_arr).clip(0, 255).astype(np.uint8)
    g_w = (20 * (1 - mask_arr) + white_val * mask_arr).clip(0, 255).astype(np.uint8)
    b_w = (28 * (1 - mask_arr) + white_val * mask_arr).clip(0, 255).astype(np.uint8)
    a_channel = np.full_like(r_w, 255)
    
    white_kimono = Image.fromarray(np.stack([r_w, g_w, b_w, a_channel], axis=-1), mode='RGBA')
    if logo_dark:
        white_kimono = apply_patches(white_kimono, logo_dark, chest_pos=(2150, 1680), chest_width=320, sleeve_pos=(1380, 1460), sleeve_width=200)
    
    white_cropped = white_kimono.convert('RGB').crop(crop_box)
    white_final = ImageEnhance.Contrast(white_cropped).enhance(1.04)
    white_final.save('static/img/store/kimono_branco.jpg', quality=95)
    print("Saved static/img/store/kimono_branco.jpg")

    # -------------------------------------------------------------
    # 2. KIMONO PRETO (Black)
    # -------------------------------------------------------------
    print("Generating Kimono Preto...")
    black_val = np.power(norm_gray, 1.25) * 55.0
    r_k = (18 * (1 - mask_arr) + black_val * mask_arr).clip(0, 255).astype(np.uint8)
    g_k = (20 * (1 - mask_arr) + black_val * mask_arr).clip(0, 255).astype(np.uint8)
    b_k = (28 * (1 - mask_arr) + black_val * mask_arr).clip(0, 255).astype(np.uint8)
    
    black_kimono = Image.fromarray(np.stack([r_k, g_k, b_k, a_channel], axis=-1), mode='RGBA')
    if logo_light:
        black_kimono = apply_patches(black_kimono, logo_light, chest_pos=(2150, 1680), chest_width=320, sleeve_pos=(1380, 1460), sleeve_width=200)
    
    black_cropped = black_kimono.convert('RGB').crop(crop_box)
    black_final = ImageEnhance.Contrast(black_cropped).enhance(1.08)
    black_final.save('static/img/store/kimono_preto.jpg', quality=95)
    print("Saved static/img/store/kimono_preto.jpg")

    # -------------------------------------------------------------
    # 3. KIMONO AZUL ROYAL (Royal Blue)
    # -------------------------------------------------------------
    print("Generating Kimono Azul Royal...")
    blue_r_val = np.power(norm_gray, 1.25) * 15.0
    blue_g_val = np.power(norm_gray, 1.15) * 65.0
    blue_b_val = np.power(norm_gray, 0.90) * 215.0
    
    r_b = (18 * (1 - mask_arr) + blue_r_val * mask_arr).clip(0, 255).astype(np.uint8)
    g_b = (20 * (1 - mask_arr) + blue_g_val * mask_arr).clip(0, 255).astype(np.uint8)
    b_b = (28 * (1 - mask_arr) + blue_b_val * mask_arr).clip(0, 255).astype(np.uint8)
    
    blue_kimono = Image.fromarray(np.stack([r_b, g_b, b_b, a_channel], axis=-1), mode='RGBA')
    if logo_light:
        blue_kimono = apply_patches(blue_kimono, logo_light, chest_pos=(2150, 1680), chest_width=320, sleeve_pos=(1380, 1460), sleeve_width=200)
    
    blue_cropped = blue_kimono.convert('RGB').crop(crop_box)
    blue_final = ImageEnhance.Contrast(blue_cropped).enhance(1.05)
    blue_final.save('static/img/store/kimono_azul.jpg', quality=95)
    print("Saved static/img/store/kimono_azul.jpg")

    print("All Kimono PSD mockups regenerated successfully with studio dark background!")

if __name__ == '__main__':
    generate_kimono_mockups()
