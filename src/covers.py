"""Blog cover images (1200x630 JPEG), drawn with Pillow at build time.

Every cover has the same layout: brand gradient background, a small tag, the article title on the left and a
simple illustration on the right. The illustration is picked per article in MOTIFS below. Everything is
original artwork drawn from shapes, so there are no image licences to worry about.
"""
from pathlib import Path

W, H, S = 1200, 630, 2           # output size and supersampling factor
FONT_DIR = Path("/usr/share/fonts/opentype/inter")

# slug -> (illustration, tag shown on the cover). Anything not listed gets ("chart", "Guide").
MOTIFS = {
    "are-online-image-converters-safe": ("lock", "Privacy"),
    "best-image-format-for-web": ("formats", "Guide"),
    "what-is-a-webp-file": ("formats", "Explainer"),
    "convert-images-to-pdf": ("pdf", "How-to"),
    "image-to-pdf-file-size": ("pdf", "Measured"),
    "favicon-size-guide": ("favicon", "Guide"),
    "image-converter-accuracy-test": ("check", "Measured"),
    "jpg-vs-webp-quality-settings": ("chart", "Measured"),
    "png-vs-jpg-vs-webp-tested": ("chart", "Measured"),
    "resize-vs-compress-image-file-size": ("resize", "Measured"),
    "png-compressor-vanilla-javascript": ("code", "Under the hood"),
    "reduce-image-file-size": ("shrink", "How-to"),
    "compress-image-to-specific-size-kb": ("shrink", "How-to"),
    "webp-vs-png": ("formats", "Measured"),
    "how-to-fix-grainy-photos": ("shrink", "How-to"),
}

BG_A, BG_B = (30, 27, 75), (99, 102, 241)       # deep indigo -> brand indigo
ACCENT = (167, 139, 250)
WHITE = (255, 255, 255)


def _font(size, weight="Bold"):
    from PIL import ImageFont
    for name in (f"Inter-{weight}.otf", "Inter-Bold.otf"):
        try: return ImageFont.truetype(str(FONT_DIR / name), size * S)
        except Exception: pass
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf"):
        try: return ImageFont.truetype(p, size * S)
        except Exception: pass
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w, max_lines=4):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines[:max_lines]


def _rr(d, box, r, **kw):
    x0, y0, x1, y1 = [v * S for v in box]
    d.rounded_rectangle((x0, y0, x1, y1), radius=r * S, **kw)


def _poly(d, pts, **kw): d.polygon([(x * S, y * S) for x, y in pts], **kw)
def _line(d, pts, w, fill): d.line([(x * S, y * S) for x, y in pts], width=w * S, fill=fill, joint="curve")


# ---------- illustrations: each is drawn inside the box x 700..1130, y 120..520 ----------
def m_chart(d, T):
    base, xs = 500, [730, 810, 890, 970, 1050]
    hs = [150, 230, 190, 300, 250]
    for x, h, c in zip(xs, hs, [(129, 140, 248), (167, 139, 250), (129, 140, 248), (196, 181, 253), (129, 140, 248)]):
        _rr(d, (x, base - h, x + 56, base), 10, fill=c)
    _line(d, [(758, 330), (838, 270), (918, 300), (998, 190), (1078, 220)], 6, WHITE)
    for p in [(758, 330), (838, 270), (918, 300), (998, 190), (1078, 220)]:
        d.ellipse(((p[0] - 9) * S, (p[1] - 9) * S, (p[0] + 9) * S, (p[1] + 9) * S), fill=WHITE)
    _line(d, [(710, 500), (1120, 500)], 4, (255, 255, 255, 120))


def m_formats(d, T):
    for i, (label, c, dx, dy) in enumerate([("PNG", (99, 102, 241), 0, 0), ("JPG", (168, 85, 247), 70, 70), ("WebP", (236, 72, 153), 140, 140)]):
        x, y = 720 + dx, 150 + dy
        _rr(d, (x, y, x + 240, y + 190), 22, fill=c, outline=WHITE, width=4 * S)
        d.text(((x + 120) * S, (y + 95) * S), label, font=_font(54), fill=WHITE, anchor="mm")


def m_pdf(d, T):
    for k, (dx, dy) in enumerate([(60, 40), (30, 20), (0, 0)]):
        x, y = 770 + dx, 130 + dy
        _poly(d, [(x, y), (x + 190, y), (x + 250, y + 60), (x + 250, y + 340), (x, y + 340)], fill=(255, 255, 255) if k == 2 else (209, 213, 255), outline=(79, 70, 229), width=3 * S)
    x, y = 770, 130
    _poly(d, [(x + 190, y), (x + 190, y + 60), (x + 250, y + 60)], fill=(199, 210, 254))
    d.text(((x + 125) * S, (y + 190) * S), "PDF", font=_font(70), fill=(79, 70, 229), anchor="mm")
    for i in range(3): _rr(d, (x + 30, y + 250 + i * 24, x + 220 - i * 30, y + 258 + i * 24), 4, fill=(165, 180, 252))


def m_lock(d, T):
    cx = 915
    d.arc(((cx - 80) * S, 150 * S, (cx + 80) * S, 330 * S), 180, 360, fill=WHITE, width=26 * S)
    _line(d, [(cx - 80, 240), (cx - 80, 300)], 26, WHITE); _line(d, [(cx + 80, 240), (cx + 80, 300)], 26, WHITE)
    _rr(d, (cx - 130, 290, cx + 130, 470), 28, fill=(255, 255, 255))
    d.ellipse(((cx - 24) * S, 345 * S, (cx + 24) * S, 393 * S), fill=(79, 70, 229))
    _rr(d, (cx - 10, 380, cx + 10, 430), 6, fill=(79, 70, 229))


def m_favicon(d, T):
    _rr(d, (720, 140, 1120, 480), 22, fill=(255, 255, 255))
    _rr(d, (720, 140, 1120, 210), 22, fill=(224, 231, 255))
    _rr(d, (740, 160, 900, 210), 14, fill=(255, 255, 255))
    _rr(d, (752, 172, 778, 198), 6, fill=(99, 102, 241))
    for i, (s, x) in enumerate([(48, 760), (96, 840), (144, 970)]):
        _rr(d, (x, 440 - s - 20, x + s, 440 - 20), max(6, s // 6), fill=(99, 102, 241) if i != 1 else (168, 85, 247))
    for i, (x, w) in enumerate([(760, 80), (860, 110), (990, 90)]):
        d.text(((x + 30) * S, 452 * S), ["16", "32", "48"][i], font=_font(22, "SemiBold"), fill=(79, 70, 229), anchor="ma")


def m_check(d, T):
    cx, cy = 915, 320
    d.ellipse(((cx - 150) * S, (cy - 150) * S, (cx + 150) * S, (cy + 150) * S), fill=(255, 255, 255))
    _line(d, [(cx - 70, cy + 5), (cx - 15, cy + 60), (cx + 80, cy - 55)], 30, (79, 70, 229))
    for i, (x, y) in enumerate([(740, 160), (1060, 190), (1080, 440), (740, 470)]):
        _rr(d, (x - 30, y - 30, x + 30, y + 30), 10, fill=(129, 140, 248) if i % 2 == 0 else (196, 181, 253))


def m_resize(d, T):
    _rr(d, (720, 150, 1030, 410), 18, fill=(255, 255, 255))
    _rr(d, (790, 230, 960, 350), 14, fill=(129, 140, 248))
    _rr(d, (950, 330, 1110, 480), 18, fill=(196, 181, 253), outline=WHITE, width=4 * S)
    _line(d, [(1000, 195), (1090, 195)], 8, WHITE); _poly(d, [(1090, 175), (1125, 195), (1090, 215)], fill=WHITE)
    for hx, hy in [(790, 230), (960, 230), (790, 350), (960, 350)]:
        d.ellipse(((hx - 9) * S, (hy - 9) * S, (hx + 9) * S, (hy + 9) * S), fill=WHITE, outline=(79, 70, 229), width=3 * S)


def m_code(d, T):
    _rr(d, (720, 150, 1120, 470), 22, fill=(17, 24, 39))
    for i, c in enumerate([(248, 113, 113), (251, 191, 36), (74, 222, 128)]):
        d.ellipse(((748 + i * 34) * S, 176 * S, (768 + i * 34) * S, 196 * S), fill=c)
    d.text((760 * S, 330 * S), "</>", font=_font(120), fill=(165, 180, 252), anchor="lm")
    for i, w in enumerate([260, 200, 300]): _rr(d, (760, 400 + i * 22, 760 + w, 410 + i * 22), 4, fill=(75, 85, 120))


def m_shrink(d, T):
    _rr(d, (720, 150, 960, 390), 22, fill=(255, 255, 255))
    d.text((840 * S, 270 * S), "5 MB", font=_font(54), fill=(79, 70, 229), anchor="mm")
    _line(d, [(975, 270), (1030, 270)], 8, WHITE); _poly(d, [(1030, 245), (1070, 270), (1030, 295)], fill=WHITE)
    _rr(d, (1010, 330, 1130, 450), 16, fill=(196, 181, 253), outline=WHITE, width=4 * S)
    d.text((1070 * S, 390 * S), "50 KB", font=_font(30), fill=(49, 46, 129), anchor="mm")
    _line(d, [(740, 470), (960, 470)], 6, (255, 255, 255, 140))


MOTIF_FN = {"chart": m_chart, "formats": m_formats, "pdf": m_pdf, "lock": m_lock, "favicon": m_favicon,
            "check": m_check, "resize": m_resize, "code": m_code, "shrink": m_shrink}


def make_cover(slug, title, out_dir, brand="ConvertPicto", logo=None):
    """Draw one cover and save it as <out_dir>/<slug>.jpg. Returns the path."""
    from PIL import Image, ImageDraw
    motif, tag = MOTIFS.get(slug, ("chart", "Guide"))
    img = Image.new("RGB", (W * S, H * S), BG_A)
    px = img.load()
    # diagonal gradient (drawn at low resolution then scaled up, which is smoother and much faster)
    g = Image.new("RGB", (W // 4, H // 4))
    gp = g.load()
    for y in range(H // 4):
        for x in range(W // 4):
            t = min(1.0, max(0.0, (x / (W / 4)) * 0.7 + (y / (H / 4)) * 0.3)) ** 1.4
            gp[x, y] = tuple(int(BG_A[i] + (BG_B[i] - BG_A[i]) * t) for i in range(3))
    img = g.resize((W * S, H * S), Image.BICUBIC)
    d = ImageDraw.Draw(img, "RGBA")
    # soft decorative circles
    d.ellipse((820 * S, -200 * S, 1400 * S, 380 * S), fill=(255, 255, 255, 14))
    d.ellipse((-160 * S, 420 * S, 340 * S, 920 * S), fill=(255, 255, 255, 10))
    MOTIF_FN.get(motif, m_chart)(d, None)
    # tag chip
    f_tag = _font(26, "SemiBold")
    tw = d.textlength(tag.upper(), font=f_tag) / S
    _rr(d, (70, 78, 70 + tw + 44, 126), 24, fill=(255, 255, 255, 40), outline=(255, 255, 255, 110), width=2 * S)
    d.text((92 * S, 102 * S), tag.upper(), font=f_tag, fill=WHITE, anchor="lm")
    # title, shrunk until it fits in 4 lines on the left 60% of the image
    for size in (66, 60, 54, 48, 44):
        f = _font(size)
        lines = _wrap(d, title, f, 590 * S, max_lines=5)
        if len(lines) <= 4 and all(d.textlength(l, font=f) <= 590 * S for l in lines): break
    y = 165
    for l in lines:
        d.text((70 * S, y * S), l, font=f, fill=WHITE, anchor="la")
        y += int(size * 1.18)
    # footer: brand
    d.text((70 * S, 556 * S), brand, font=_font(30), fill=(224, 231, 255), anchor="lm")
    if logo is not None:
        lg = logo.resize((44 * S, 44 * S))
        img.paste(lg, (int(70 * S + d.textlength(brand, font=_font(30)) + 18 * S), 534 * S), lg)
    img = img.resize((W, H), Image.LANCZOS)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}.jpg"
    img.save(path, quality=86, optimize=True, progressive=True)
    return path
