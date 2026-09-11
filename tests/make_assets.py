"""Generates the test images used by test_site.py (one of every input format)."""
from PIL import Image, ImageDraw
import random, math, pathlib
random.seed(1)
OUT = pathlib.Path(__file__).resolve().parent / "assets"; OUT.mkdir(exist_ok=True)
W, H = 640, 420
img = Image.new("RGBA", (W, H)); px = img.load()
for y in range(H):
    for x in range(W):
        r = int(255 * x / W); g = int(255 * y / H); b = int(128 + 127 * math.sin(x / 40) * math.cos(y / 30)); n = random.randint(-6, 6)
        a = 0 if (x < 80 and y < 80) else (128 if (x > W - 80 and y < 80) else 255)
        px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), a)
d = ImageDraw.Draw(img); d.ellipse((200, 100, 440, 320), fill=(250, 240, 20, 255)); d.rectangle((300, 250, 600, 400), fill=(20, 60, 200, 255))
img.save(OUT / "photo.png"); img.convert("RGB").save(OUT / "photo.jpg", quality=92); img.convert("RGB").save(OUT / "photo.bmp")
img.save(OUT / "photo.webp", quality=90); img.convert("P", palette=Image.ADAPTIVE).save(OUT / "photo.gif")
g = Image.new("RGBA", (400, 300), (255, 255, 255, 255)); d = ImageDraw.Draw(g)
d.rectangle((20, 20, 380, 120), fill=(99, 102, 241, 255)); d.ellipse((50, 150, 250, 290), fill=(20, 180, 100, 255)); d.text((30, 40), "PixelShrink", fill=(255, 255, 255, 255))
g.save(OUT / "graphic.png")
(OUT / "vector.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><rect width="200" height="100" fill="#6366f1"/><circle cx="60" cy="50" r="30" fill="#fff"/><text x="110" y="60" font-size="28" fill="#fff">SVG</text></svg>')
(OUT / "sized.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="150"><rect width="300" height="150" fill="#f59e0b"/></svg>')
img.resize((64, 64)).save(OUT / "icon.ico", sizes=[(64, 64)])
print("assets written to", OUT)
