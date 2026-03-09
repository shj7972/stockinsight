import os
import io
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "static")

def generate_stock_og_image(ticker: str, name: str, current_price: str, change_pct: str, trend: str):
    """
    Generate a dynamic Open Graph image for a specific stock.
    Current size: 1200x630 (Standard OG image size)
    """
    width, height = 1200, 630
    
    # 1. Create a background gradient or solid color
    # Using a dark theme gradient-like solid color for now
    img = Image.new('RGB', (width, height), color=(15, 23, 42))  # slate-900
    draw = ImageDraw.Draw(img)
    
    # Draw simple gradient/pattern
    for y in range(height):
        r = int(15 + (30 - 15) * (y / height))
        g = int(23 + (40 - 23) * (y / height))
        b = int(42 + (60 - 42) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Draw a subtle grid
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=(255, 255, 255, 10))
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255, 10))

    try:
        # Load fonts
        title_font = ImageFont.truetype(os.path.join(FONTS_DIR, "NanumGothic-Bold.ttf"), 90)
        subtitle_font = ImageFont.truetype(os.path.join(FONTS_DIR, "NanumGothic-Bold.ttf"), 50)
        price_font = ImageFont.truetype(os.path.join(FONTS_DIR, "NanumGothic-Bold.ttf"), 120)
        change_font = ImageFont.truetype(os.path.join(FONTS_DIR, "NanumGothic-Bold.ttf"), 70)
        brand_font = ImageFont.truetype(os.path.join(FONTS_DIR, "NanumGothic-Bold.ttf"), 40)
    except IOError:
        # Fallback to default if font is missing
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
        change_font = ImageFont.load_default()
        brand_font = ImageFont.load_default()

    # Layout and padding
    pad_x = 80
    
    # 2. Draw Ticker & Name
    draw.text((pad_x, 80), f"{name}", font=title_font, fill=(248, 250, 252))  # slate-50
    draw.text((pad_x, 190), f"{ticker}", font=subtitle_font, fill=(148, 163, 184))  # slate-400

    # 3. Draw Price
    draw.text((pad_x, 320), f"{current_price}", font=price_font, fill=(255, 255, 255))
    
    # 4. Draw Change Percentage with color
    # Determine color based on trend
    if trend == 'up' or float(change_pct.replace('%', '').replace('+', '').replace('-', '')) > 0:
        if '-' not in change_pct:
            color = (52, 211, 153) # emerald-400
            change_str = change_pct if '+' in change_pct else f"+{change_pct}"
            if "▲" not in change_str:
                change_str = f"▲ {change_str}"
        else:
            color = (248, 113, 113) # red-400
            change_str = change_pct
            if "▼" not in change_str:
                change_str = f"▼ {change_str.replace('-','')}"
    else:
        color = (248, 113, 113) # red-400
        change_str = change_pct
        if trend == 'down':
             if "▼" not in change_str and "-" not in change_str:
                 change_str = f"▼ {change_str}"
        
    if change_pct == "0.00%":
        color = (148, 163, 184)
        change_str = "0.00%"

    # Hacky way to measure text
    try:
        price_bbox = draw.textbbox((pad_x, 320), f"{current_price}", font=price_font)
        price_width = price_bbox[2] - price_bbox[0]
    except:
        price_width = len(f"{current_price}") * 70
        
    draw.text((pad_x + price_width + 40, 360), change_str, font=change_font, fill=color)

    # 5. Draw AI Insight badge (simulate a badge)
    badge_color = (56, 189, 248) if trend == 'up' else ((248, 113, 113) if trend == 'down' else (148, 163, 184))
    badge_text = "AI 매수 신호 포착" if trend == 'up' else ("AI 리스크 주의" if trend == 'down' else "AI 중립/관망")
    
    # Draw badge background
    try:
        badge_bbox = draw.textbbox((0, 0), badge_text, font=subtitle_font)
        badge_w = badge_bbox[2] - badge_bbox[0] + 60
        badge_h = badge_bbox[3] - badge_bbox[1] + 40
    except:
        badge_w, badge_h = 400, 80
        
    badge_x = width - badge_w - pad_x
    badge_y = 80
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=15, fill=badge_color)
    draw.text((badge_x + 30, badge_y + 10), badge_text, font=subtitle_font, fill=(255, 255, 255))

    # 6. Build Brand/Logo at bottom
    draw.line([(pad_x, height - 100), (width - pad_x, height - 100)], fill=(51, 65, 85), width=2)
    draw.text((pad_x, height - 70), "📈 Stock Insight AI", font=brand_font, fill=(148, 163, 184))
    draw.text((width - pad_x - 300, height - 70), "실시간 AI 주식 펀더멘털 분석", font=brand_font, fill=(148, 163, 184))

    # 7. Convert to byte array
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr
