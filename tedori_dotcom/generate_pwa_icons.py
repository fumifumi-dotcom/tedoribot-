from PIL import Image, ImageDraw, ImageFont
import os

DIR = "/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools/images"
os.makedirs(DIR, exist_ok=True)

def create_icon(size):
    # Base circle with blue accent color
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([(0, 0), (size, size)], fill="#0ea5e9")
    
    # Text (Yen symbol)
    try:
        # Use a system font if available, or just draw something simple
        # Since we might not have reliable TTF, let's just make it visually distinct using basic drawing
        font = ImageFont.load_default()
    except:
        font = None
        
    # Draw simple Yen symbol using lines to avoid font issues
    c = size // 2
    w = size // 4
    h = size // 3
    # Y top v
    d.line([(c-w, c-h), (c, c)], fill="white", width=size//15)
    d.line([(c+w, c-h), (c, c)], fill="white", width=size//15)
    # Y vertical
    d.line([(c, c), (c, c+h)], fill="white", width=size//15)
    # horizontal bars
    d.line([(c-w//1.5, c+h//4), (c+w//1.5, c+h//4)], fill="white", width=size//15)
    d.line([(c-w//1.5, c+h//1.5), (c+w//1.5, c+h//1.5)], fill="white", width=size//15)

    img.save(os.path.join(DIR, f"icon-{size}x{size}.png"))

create_icon(192)
create_icon(512)
print("Icons generated.")
