import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

def create_belt_image(belt_color_name, main_color, bar_color, output_path):
    width, height = 1000, 1000
    
    # Base slate studio background #12141c with radial gradient light
    bg = Image.new('RGB', (width, height), '#12141c')
    draw_bg = ImageDraw.Draw(bg)
    
    # Create radial background glow
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    center_x, center_y = 500, 500
    for r in range(450, 0, -10):
        alpha = int(40 * (1 - r / 450))
        glow_draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            fill=(40, 45, 60, alpha)
        )
    bg = Image.alpha_composite(bg.convert('RGBA'), glow).convert('RGB')
    
    # Layer for drawing the belt
    belt_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(belt_layer)
    
    # Drop shadow layer
    shadow_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    
    # Belt geometry parameters (folded / coiled loop representation)
    belt_width = 80
    
    # Main horizontal folded belt body
    # Loop 1: Top fold
    y1 = 380
    x_start1, x_end1 = 220, 780
    
    # Loop 2: Bottom fold
    y2 = 490
    x_start2, x_end2 = 180, 820
    
    # Draw drop shadow for belts
    shadow_draw.rounded_rectangle([x_start1 - 10, y1 + 15, x_end1 + 10, y1 + belt_width + 15], radius=16, fill=(0, 0, 0, 140))
    shadow_draw.rounded_rectangle([x_start2 - 15, y2 + 20, x_end2 + 15, y2 + belt_width + 20], radius=16, fill=(0, 0, 0, 180))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(15))
    
    # Helper to draw a belt segment with stitching texture
    def draw_belt_segment(x1, y1, x2, y2, color, is_white=False):
        # Base rectangle
        segment = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(segment)
        s_draw.rounded_rectangle([x1, y1, x2, y2], radius=12, fill=color)
        
        # Add 8 parallel longitudinal stitching lines
        stitch_color = (40, 40, 40, 90) if is_white else (255, 255, 255, 40)
        h = y2 - y1
        for i in range(1, 8):
            line_y = y1 + int(h * (i / 8))
            s_draw.line([(x1 + 10, line_y), (x2 - 10, line_y)], fill=stitch_color, width=2)
            
        # Top gradient highlight for 3D depth
        highlight = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        h_draw = ImageDraw.Draw(highlight)
        h_draw.rounded_rectangle([x1, y1, x2, y1 + 12], radius=6, fill=(255, 255, 255, 35))
        
        # Bottom shading
        shading = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        sh_draw = ImageDraw.Draw(shading)
        sh_draw.rounded_rectangle([x1, y2 - 12, x2, y2], radius=6, fill=(0, 0, 0, 60))
        
        belt_layer.alpha_composite(segment)
        belt_layer.alpha_composite(highlight)
        belt_layer.alpha_composite(shading)
        
    is_white_belt = (belt_color_name == 'branca')
    
    # Draw bottom layer fold
    draw_belt_segment(x_start2, y2, x_end2, y2 + belt_width, main_color, is_white=is_white_belt)
    
    # Draw top layer fold
    draw_belt_segment(x_start1, y1, x_end1, y1 + belt_width, main_color, is_white=is_white_belt)
    
    # Draw Rank Sleeve Bar on the right end of the top fold
    bar_width = 110
    bar_x1 = x_end1 - 140
    bar_x2 = bar_x1 + bar_width
    bar_y1 = y1
    bar_y2 = y1 + belt_width
    
    bar_segment = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    bar_draw = ImageDraw.Draw(bar_segment)
    bar_draw.rectangle([bar_x1, bar_y1 + 2, bar_x2, bar_y2 - 2], fill=bar_color)
    
    # Border stitching around rank bar
    bar_draw.rectangle([bar_x1, bar_y1 + 2, bar_x2, bar_y2 - 2], outline=(255, 255, 255, 80), width=2)
    
    # Rank stripes (white athletic tape stripes on the sleeve bar)
    stripe_w = 12
    stripe_gap = 14
    start_stripe_x = bar_x1 + 18
    # Draw 2 stripes for representation
    for s_idx in range(2):
        sx = start_stripe_x + s_idx * (stripe_w + stripe_gap)
        bar_draw.rectangle([sx, bar_y1 + 6, sx + stripe_w, bar_y2 - 6], fill=(245, 245, 245, 240))
        bar_draw.rectangle([sx, bar_y1 + 6, sx + stripe_w, bar_y2 - 6], outline=(180, 180, 180, 200), width=1)
        
    belt_layer.alpha_composite(bar_segment)
    
    # Add subtle textile noise/texture over the belt
    final_img = Image.alpha_composite(bg.convert('RGBA'), shadow_layer)
    final_img = Image.alpha_composite(final_img, belt_layer)
    
    # Save image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_img.convert('RGB').save(output_path, 'JPEG', quality=95)
    print(f"Generated belt image: {output_path}")

belts = [
    {'name': 'branca', 'main': '#f4f4f6', 'bar': '#18181b'},
    {'name': 'azul', 'main': '#1d4ed8', 'bar': '#18181b'},
    {'name': 'roxa', 'main': '#7e22ce', 'bar': '#18181b'},
    {'name': 'marrom', 'main': '#5c3a21', 'bar': '#18181b'},
    {'name': 'preta', 'main': '#18181b', 'bar': '#dc2626'},
]

for b in belts:
    out = os.path.join('/home/vier/Documentos/Code/BJ Sports/static/img/store', f"faixa_{b['name']}.jpg")
    create_belt_image(b['name'], b['main'], b['bar'], out)
