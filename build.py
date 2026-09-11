#!/usr/bin/env python3
"""
PixelShrink site generator.

    python3 build.py        -> regenerates everything in dist/

Edit the SITE / ADS / ANALYTICS blocks below, then rebuild. Every page in
dist/ is a fully self-contained HTML file (CSS + JS inlined) so nothing can
fail to load, wherever you open or host it. Deploy the dist/ folder.
"""
import json, html, shutil, datetime, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
import blog as blogmod

ROOT = Path(__file__).parent
SRC, DIST = ROOT / "src", ROOT / "dist"

# =====================================================================
# 1. CONFIG — the only block most people need to touch
# =====================================================================
SITE = {
    "name": "ConvertPicto",
    "domain": "https://convertpicto.com",     # your real domain, no trailing slash
    "tagline": "Free image tools that run entirely in your browser",
    "contact_email": "contact@ihtishamkhalil.com",
    "year": datetime.date.today().year,

    # Logo text is split into a normal part + a gradient part, e.g. ("Pixel", "Shrink").
    # Rename the site by changing "name" above AND this pair.
    "logo": ("Convert", "Picto"),

    # Logo image (optional). Path relative to this file — SVG or PNG. Leave "" to use the
    # generated letter-mark instead. It's inlined into every page (no extra request) and
    # also becomes the favicon and the icon on the social-share image.
    "logo_file": "src/logo.svg",
    "logo_show_text": True,     # False if your logo file is a full wordmark with the name in it

    # "Designed & developed by …" credit in the footer (a followed link to your own site).
    # Set both to "" to remove the credit line.
    "designer": {"name": "Ihtisham Khalil", "url": "https://ihtishamkhalil.com/"},

    # Contact page + footer. Leave any value "" to hide it.
    "contact": {
        "phone": "",                 # e.g. "+92 300 1234567"
        "whatsapp": "",              # e.g. "923001234567" (digits only, with country code)
        "location": "",              # e.g. "Karachi, Pakistan"
        "hours": "",                 # e.g. "Replies within 1–2 business days"
    },
    "social": {                      # full URLs; leave "" to hide
        "x": "", "facebook": "", "instagram": "", "linkedin": "", "github": "", "youtube": "",
    },
}

ADS = {
    # Set enabled=True and paste your AdSense publisher ID + slot IDs once approved.
    # Until then, dashed placeholders show you exactly where the ads will render.
    "enabled": False,
    # While enabled=False: show dashed placeholder boxes where ads will go?  False = nothing
    # rendered at all (recommended while you wait for AdSense approval).
    "placeholders": False,
    "client": "ca-pub-XXXXXXXXXXXXXXXX",
    "slots": {"top": "1111111111", "mid": "2222222222", "side": "3333333333", "bottom": "4444444444"},
}

ANALYTICS = {"ga4": ""}   # e.g. "G-XXXXXXXXXX" — leave empty to disable

# Clean URLs: links become /png-to-jpg instead of png-to-jpg.html. Turn ON for real hosting
# (Hostinger/cPanel via the generated .htaccess; Netlify/Vercel handle it natively).
# Leave OFF only while previewing dist/ by double-clicking files on your computer.
CLEAN_URLS = True

# =====================================================================
# 2. FORMAT KNOWLEDGE — used to write unique copy for every page
# =====================================================================
F = {
    "png":  dict(label="PNG",  full="Portable Network Graphics", out=True,  lossy=False, alpha=True,
                 blurb="lossless and supports transparency — ideal for logos, icons, screenshots and anything you'll keep editing",
                 weakness="PNG files are lossless but often large, especially photos or detailed screenshots"),
    "jpg":  dict(label="JPG",  full="JPEG", out=True, lossy=True, alpha=False,
                 blurb="the most universally supported photo format — small files that open in every app, email client and printer",
                 weakness="JPG can't hold transparency, and every re-save loses a little quality"),
    "webp": dict(label="WebP", full="WebP", out=True, lossy=True, alpha=True,
                 blurb="25–35% smaller than JPG or PNG at the same visual quality, with transparency — the go-to for fast websites",
                 weakness="WebP is compact and modern, but some older software, email clients and design tools still won't open it"),
    "bmp":  dict(label="BMP",  full="Windows Bitmap", out=True, lossy=False, alpha=False,
                 blurb="an uncompressed Windows bitmap — large, but still required by some legacy software, embedded systems and print workflows",
                 weakness="BMP files are uncompressed, so they're huge — a converted version is usually a fraction of the size"),
    "ico":  dict(label="ICO",  full="Windows Icon", out=True, lossy=False, alpha=True,
                 blurb="the favicon format — browsers and Windows read it natively, and one file can bundle several sizes",
                 weakness="ICO files are meant for favicons and Windows icons; converting them makes the artwork usable anywhere"),
    "gif":  dict(label="GIF",  full="Graphics Interchange Format", out=False, lossy=True, alpha=True,
                 blurb="a 256-colour format mostly used for simple animations",
                 weakness="GIF is limited to 256 colours. Only the first frame of an animated GIF is converted"),
    "avif": dict(label="AVIF", full="AV1 Image File Format", out=False, lossy=True, alpha=True,
                 blurb="the newest and most efficient image format",
                 weakness="AVIF is extremely efficient, but support outside modern browsers is still patchy"),
    "svg":  dict(label="SVG",  full="Scalable Vector Graphics", out=False, lossy=False, alpha=True,
                 blurb="a vector format that scales to any size",
                 weakness="SVG is a vector format — many apps and platforms need a normal pixel image instead"),
}

CONVERSIONS = [
    ("png", "jpg"), ("png", "webp"), ("png", "bmp"), ("png", "ico"),
    ("jpg", "png"), ("jpg", "webp"), ("jpg", "bmp"), ("jpg", "ico"),
    ("webp", "png"), ("webp", "jpg"), ("webp", "bmp"), ("webp", "ico"),
    ("gif", "png"), ("gif", "jpg"), ("gif", "webp"), ("gif", "bmp"),
    ("bmp", "png"), ("bmp", "jpg"), ("bmp", "webp"), ("bmp", "ico"),
    ("avif", "png"), ("avif", "jpg"), ("avif", "webp"),
    ("svg", "png"), ("svg", "jpg"), ("svg", "webp"), ("svg", "ico"),
    ("ico", "png"),
]
PDF_SOURCES = ["jpg", "png", "webp"]

# =====================================================================
# 3. TOOL DEFINITIONS
# =====================================================================
TOOLS = {}   # slug -> dict

def add(slug, **kw):
    kw["slug"] = slug
    TOOLS[slug] = kw
    return kw

COMMON_FAQ = [
    ("Is this tool free?", "Yes — every tool on {site} is completely free, with no account, no watermark and no file limits. The site is supported by ads."),
    ("Are my images uploaded to a server?", "No. {site} runs entirely inside your browser using the Canvas API. Your files are read locally, processed on your device and never sent anywhere — we don't even have a server that could receive them."),
    ("Does it work on my phone?", "Yes. The site is fully responsive and works in any modern mobile browser (Chrome, Safari, Firefox, Edge). Processing large images is naturally slower on a phone than on a laptop."),
]

def conv_tool(src, dst):
    S, D = F[src], F[dst]
    slug = f"{src}-to-{dst}"
    title = f"Convert {S['label']} to {D['label']}"
    lossy_note = ""
    if D["lossy"]:
        lossy_note = f" Use the quality slider to balance file size against sharpness — 80–90% is visually identical to the original for most images."
    elif S["lossy"] and not D["lossy"]:
        lossy_note = f" {D['label']} is lossless, so nothing is lost beyond what was already baked into the {S['label']}."
    alpha_note = ""
    if S["alpha"] and not D["alpha"]:
        alpha_note = f" {D['label']} has no transparency, so transparent areas are filled with a colour of your choice (white by default)."
    why = [
        (f"Why {D['label']}?", f"{D['label']} ({D['full']}) is {D['blurb']}."),
        (f"What's wrong with {S['label']}?", f"{S['weakness']}."),
    ]
    faq = [
        (f"Will I lose quality converting {S['label']} to {D['label']}?",
         (f"{D['label']} is a lossy format, so a small amount of detail is discarded. At 85%+ quality the difference is invisible to the eye, and you can always raise the slider to 100% for maximum fidelity."
          if D["lossy"] else f"No. {D['label']} is lossless — the converted image is pixel-for-pixel identical to what your browser decoded from the {S['label']} file.") + alpha_note),
        (f"Can I convert several {S['label']} files at once?", "Yes. Drop as many files as you like — each one is converted individually and you can grab them one by one or all together as a ZIP."),
    ]
    if src == "gif": faq.append(("Does it work with animated GIFs?", f"Only the first frame is converted — {D['label']} is a still-image format. If you need the animation kept, a video format (MP4/WebM) is the usual choice."))
    if src == "svg": faq.append(("What size will the output be?", "If your SVG declares a width and height, that size is used. If it only has a viewBox, it's rendered 1024 px wide at the correct aspect ratio. Use the Resize tool afterwards if you need a specific size."))
    if src == "avif": faq.append(("My AVIF file won't open — why?", "AVIF decoding is handled by your browser. Chrome 85+, Firefox 93+ and Safari 16+ all support it; if you're on something older, updating your browser fixes it."))
    if dst == "ico": faq.append(("Which icon sizes should I pick?", "16×16, 32×32 and 48×48 (the defaults) cover browser tabs, bookmarks and Windows shortcuts. Add 64–256 px if you also need high-DPI or app-icon use."))
    if dst == "bmp": faq.append(("Why is the BMP so much bigger?", "BMP stores every pixel uncompressed — a 1920×1080 image is always about 6 MB. That's normal; only use BMP when a specific program requires it."))
    return add(slug,
        category="convert", src=src, dst=dst,
        h1=f"{S['label']} to {D['label']} Converter", howto=f"How to convert {S['label']} to {D['label']}",
        page_title=f"{S['label']} to {D['label']} Converter — Free & Private | {SITE['name']}",
        meta=f"Convert {S['label']} to {D['label']} online for free. Fast, private, no upload — everything runs in your browser. Batch convert multiple files and download as ZIP.",
        card=f"{S['label']} → {D['label']}", card_desc=f"Convert {S['full']} to {D['label']}",
        lead=f"Drop a {S['label']} file below and get a {D['label']} back in seconds.{lossy_note} No upload, no sign-up, no watermark.",
        config={"mode": "convert", "from": src, "to": dst, "dropTitle": f"Drop your {S['label']} file here or click to upload", "dropSub": f"Also accepts any other image format — the output will be {D['label']}"},
        why=why,
        steps=[("Upload", f"drag your {S['label']} file(s) onto the box, click to browse, or paste from the clipboard."),
               ("Adjust", "pick the output format if you change your mind, and set the quality or icon sizes." if D["lossy"] or dst == "ico" else "the output format is already set — optionally pick a background colour for transparent areas." if not D["alpha"] else "the output format is already set to " + D["label"] + " — nothing else to do."),
               ("Download", f"grab each {D['label']} individually, or all of them at once as a ZIP.")],
        faq=faq,
        keywords=[f"{src} to {dst}", f"convert {src} to {dst}", f"{src} to {dst} converter online"],
    )

for s, d in CONVERSIONS:
    conv_tool(s, d)

def compress_tool(fmt):
    X = F[fmt]
    if fmt == "png":
        lead = "Shrink PNG files by 50–80% with smart palette compression — the same technique TinyPNG uses — right in your browser. Transparency is preserved."
        why = [("How PNG compression works", "A normal PNG stores 16 million possible colours per pixel. Most images only use a few hundred distinct ones, so we build an optimised palette of up to 256 colours and re-encode the image against it. Dithering smooths gradients so the result is visually identical at a fraction of the size."),
               ("When to use it", "Screenshots, UI graphics, logos, illustrations and any image with transparency. For photographs, converting to WebP or JPG usually gives even smaller files.")]
        faq = [("Will I lose quality?", "Technically a small amount — the image is reduced to at most 256 colours. For graphics and screenshots the result is indistinguishable; for photos with subtle gradients, keep dithering on and use the full 256-colour palette."),
               ("Is transparency kept?", "Yes. Fully transparent and semi-transparent pixels both survive compression."),
               ("Why is my file not much smaller?", "If the PNG was already 8-bit (indexed) or very small, there's little left to squeeze. Try lowering the palette size, or convert to WebP for a bigger win.")]
        cfg = {"mode": "compress", "format": "png", "dropTitle": "Drop PNG files here or click to upload", "dropSub": "Any image format works — the output is an optimised PNG"}
    else:
        lead = f"Reduce {X['label']} file size online. Drag the quality slider, watch the size drop, download. Everything happens in your browser — nothing is uploaded."
        why = [("Pick the right quality", "60–75% is the sweet spot for most photos — the file often shrinks by half or more with no visible difference. Go lower (30–50%) for thumbnails or background images where sharpness matters less."),
               ("Want it even smaller?", "Converting to WebP instead usually cuts another 25–35% at the same visual quality." if fmt == "jpg" else "WebP is already one of the most efficient formats — pairing compression with the Resize tool is the next lever if you need to go smaller.")]
        faq = [("Does compression reduce quality?", f"{X['label']} is a lossy format, so yes — but at 70%+ the difference is invisible for most photos. You can always re-run with a different setting; the original file on your device is never modified."),
               ("What's a good target size?", "For web images, under 200 KB is a good goal for a large hero photo and under 50 KB for thumbnails.")]
        cfg = {"mode": "compress", "format": fmt, "dropTitle": f"Drop {X['label']} files here or click to upload", "dropSub": f"Any image format works — the output is a compressed {X['label']}"}
    return add(f"compress-{fmt}", category="compress", fmt=fmt,
        h1=f"Compress {X['label']} Online", howto=f"How to compress a {X['label']}",
        page_title=f"Compress {X['label']} Online — Free, No Upload | {SITE['name']}",
        meta=f"Compress {X['label']} images online for free. Reduce {X['label']} file size in your browser with no upload and no quality surprises. Batch supported.",
        card=f"Compress {X['label']}", card_desc=f"Reduce {X['label']} file size",
        lead=lead, config=cfg, why=why,
        steps=[("Upload", f"drop your {X['label']} file(s) onto the box or click to browse."),
               ("Tune", "adjust the palette size and dithering" if fmt == "png" else "drag the quality slider — the result updates for the next file you add"),
               ("Download", "each compressed file shows its before/after size and savings.")],
        faq=faq, keywords=[f"compress {fmt}", f"{fmt} compressor", f"reduce {fmt} file size"])

for f_ in ["jpg", "png", "webp"]:
    compress_tool(f_)

add("resize-image", category="edit",
    h1="Resize Image Online", howto="How to resize an image", page_title=f"Resize Image Online — Free, Fast, No Upload | {SITE['name']}",
    meta="Resize images online for free by exact pixel size or percentage. Keeps aspect ratio, batch supported, runs entirely in your browser.",
    card="Resize Image", card_desc="Scale to exact pixels or percent",
    lead="Set a width, a height, or a percentage and get a resized copy in any format. Leave one dimension blank and it's calculated for you.",
    config={"mode": "resize", "to": "png", "dropTitle": "Drop images here or click to upload", "dropSub": "Set the size below first, then drop your files"},
    why=[("Exact or proportional", "Enter just a width to keep the aspect ratio, both to fit inside a box, or untick 'Keep aspect ratio' to force exact dimensions. Leaving the height blank is the safest option — the correct height is worked out for you, so nothing is ever squashed or stretched."),
         ("Quality resampling", "Images are downscaled with high-quality interpolation, so shrinking a photo stays sharp rather than jagged. Browsers do this in a single step, which is why a 4000&nbsp;px photo reduced to 800&nbsp;px still looks clean rather than pixelated."),
         ("Resize before you compress", "File size scales with area, not width. Halving both dimensions removes 75% of the pixels, which usually saves more than any quality slider will. Resize first, then compress — doing it the other way round throws the work away."),
         ("Nothing is uploaded", "The resize happens on your own device using the Canvas API. Your images are never sent anywhere, so screenshots of private dashboards, client work and photographs of documents are all safe to drop here.")],
    steps=[("Set the size", "type a width and/or height in pixels, or click 25% / 50% / 75%."), ("Upload", "drop your image(s) — the size applies to each one."), ("Download", "pick PNG, JPG or WebP output and grab the result.")],
    faq=[("Can I enlarge an image?", "Yes, but upscaling can't invent detail — a small image made larger will look softer. It works fine for modest increases of 20–50%; beyond about 2× the softness becomes obvious."),
         ("Does it resize multiple images at once?", "Yes. The same size settings apply to every file you drop; each is resized independently, and you can download them individually or all together as a ZIP."),
         ("What size should I resize to?", "For a full-width hero image, 1920–2400&nbsp;px wide. For an image inside an article, 1200–1600&nbsp;px. For a thumbnail or card, 400–600&nbsp;px. Those figures already include a 2× allowance for high-DPI screens, so an image displayed at 600&nbsp;px on the page should be exported at around 1200&nbsp;px."),
         ("Will resizing reduce the file size?", "Almost always, and usually by a lot. A 12-megapixel phone photo of about 4&nbsp;MB typically drops to under 400&nbsp;KB when resized to 1600&nbsp;px wide, before any compression is applied at all."),
         ("Does it keep transparency?", "Yes, if you export as PNG or WebP. Exporting to JPG flattens transparent areas onto a background colour, because JPG has no alpha channel."),
         ("Can I resize by percentage instead of pixels?", "Yes — the 25%, 50% and 75% buttons scale each image relative to its own dimensions, which is useful when you're resizing a batch of images that aren't all the same size.")],
    keywords=["resize image", "image resizer", "resize png", "resize jpg"])

add("rotate-image", category="edit",
    h1="Rotate Image Online", howto="How to rotate an image", page_title=f"Rotate Image Online — 90°, 180°, 270° | {SITE['name']}",
    meta="Rotate images online for free — 90, 180 or 270 degrees, plus flip. No upload, no quality loss for PNG. Works on phone and desktop.",
    card="Rotate Image", card_desc="Turn 90°, 180° or 270°",
    lead="Fix sideways photos in one click. Rotate by 90°, 180° or 270°, optionally flip, and download in PNG, JPG or WebP.",
    config={"mode": "rotate", "to": "jpg", "rotate": 90, "dropTitle": "Drop images here or click to upload", "dropSub": "Choose the rotation first, then drop your files"},
    why=[("No quality loss (for PNG/WebP lossless use)", "Rotation by right angles doesn't resample pixels, so PNG output is lossless. JPG output re-encodes at the quality you choose."),
         ("Phones are the usual culprit", "Photos taken in portrait often carry an orientation flag that some apps ignore. Rotating and re-saving bakes the correct orientation in permanently.")],
    steps=[("Pick the angle", "90° turns clockwise, 270° counter-clockwise, 180° upside down."), ("Upload", "drop your image(s)."), ("Download", "choose the output format and save.")],
    faq=[("Can I rotate by an arbitrary angle like 15°?", "Not with this tool — it's built for the right-angle fixes that cover 99% of cases. Arbitrary angles need cropping decisions that are better made in an image editor."),
         ("Does it keep EXIF data?", "No — output files are clean re-encodes without metadata, which is usually what you want for privacy when sharing photos.")],
    keywords=["rotate image", "rotate photo online", "rotate jpg"])

add("flip-image", category="edit",
    h1="Flip Image Online", howto="How to flip an image", page_title=f"Flip Image Online — Mirror Horizontally | {SITE['name']}",
    meta="Flip or mirror an image horizontally or vertically online for free. No upload — runs in your browser. Download as PNG, JPG or WebP.",
    card="Flip / Mirror Image", card_desc="Mirror horizontally or vertically",
    lead="Mirror an image left-to-right or top-to-bottom. Handy for selfies that came out backwards, print transfers, and symmetrical design work.",
    config={"mode": "flip", "to": "png", "flipH": True, "dropTitle": "Drop images here or click to upload", "dropSub": "Choose the flip direction first, then drop your files"},
    why=[("Horizontal vs vertical", "Horizontal flips swap left and right (a mirror). Vertical flips turn the image upside-down without rotating it — text ends up reversed top-to-bottom."),
         ("Combine with rotation", "You can rotate and flip in the same pass — the rotation buttons are right there.")],
    steps=[("Choose", "tick horizontal, vertical, or both."), ("Upload", "drop your image(s)."), ("Download", "pick a format and save.")],
    faq=[("Is flipping lossless?", "Yes for PNG and BMP output. JPG and WebP re-encode at your chosen quality."),
         ("Why do front-camera selfies look mirrored?", "Phones show you a mirror image while shooting but often save the un-mirrored version. A horizontal flip gives you back what you saw on screen.")],
    keywords=["flip image", "mirror image online", "flip photo"])

add("grayscale-image", category="edit",
    h1="Convert Image to Black and White", howto="How to make an image black and white", page_title=f"Black and White Image Converter — Free | {SITE['name']}",
    meta="Turn any image black and white (grayscale) online for free. No upload, instant preview, download as PNG, JPG or WebP.",
    card="Black & White", card_desc="Convert to grayscale",
    lead="Strip the colour from any photo or graphic in one step. Output as PNG, JPG or WebP — nothing leaves your browser.",
    config={"mode": "grayscale", "to": "jpg", "dropTitle": "Drop images here or click to upload", "dropSub": "Any image format — the output will be grayscale"},
    why=[("True luminance conversion", "Colours are weighted the way the human eye perceives brightness (green counts more than blue), so skin tones and skies keep their natural contrast."),
         ("Smaller files, too", "Grayscale JPGs compress noticeably better than colour ones, so you often get a size reduction for free.")],
    steps=[("Upload", "drop your image(s)."), ("Pick a format", "PNG keeps transparency; JPG is smallest for photos."), ("Download", "save the black-and-white version.")],
    faq=[("Is this the same as 'desaturate'?", "Very close — both remove colour. This uses a perceptual luminance formula, which generally looks more natural than a plain desaturation."),
         ("Can I get a sepia or tinted version?", "Not from this tool — it's grayscale only. Any image editor can tint the result afterwards.")],
    keywords=["black and white image", "grayscale image online", "convert photo to black and white"])

for src in PDF_SOURCES:
    S = F[src]
    add(f"{src}-to-pdf", category="pdf", src=src,
        h1=f"{S['label']} to PDF Converter", howto=f"How to convert {S['label']} to PDF", page_title=f"{S['label']} to PDF Converter — Free, No Upload | {SITE['name']}",
        meta=f"Convert {S['label']} to PDF online for free. Combine multiple {S['label']} images into one PDF, choose A4/Letter/fit-to-image, no upload — runs in your browser.",
        card=f"{S['label']} → PDF", card_desc=f"Turn {S['label']} images into a PDF",
        lead=f"Turn one or many {S['label']} images into a PDF document. Choose A4, US Letter or fit-to-image pages, set margins, and download — all inside your browser.",
        config={"mode": "pdf", "from": src, "dropTitle": f"Drop {S['label']} files here or click to upload", "dropSub": "Drop several at once to combine them into one multi-page PDF"},
        why=[("Combine or separate", "By default every image you drop becomes one page of a single PDF, in the order you added them. Untick 'Combine' to get one PDF per image instead."),
             ("Print-ready sizing", "Pick A4 or Letter with a margin for documents you'll print, or 'Fit to image' for a PDF that's exactly the image's size — perfect for scans and receipts.")],
        steps=[("Set the page", "A4, Letter or fit-to-image; auto orientation picks portrait or landscape per image."), ("Upload", f"drop your {S['label']} file(s) in the order you want them."), ("Download", "one PDF, ready to send or print.")],
        faq=[("Does it keep the image quality?", "Images are embedded as JPEG at the quality you choose (90% by default — visually lossless for photos). Raise it to 100% for maximum fidelity or lower it for a smaller PDF."),
             ("Can I reorder pages?", "Pages follow the order the files are added. Drop them in the order you want, or use the file picker where you can select in sequence."),
             ("Is there a page limit?", "No hard limit — it's only bounded by your device's memory. Hundreds of typical photos are fine.")] +
            ([("What happens to transparency?", "PDF pages have a background, so transparent areas are filled with the colour you pick (white by default).")] if S["alpha"] else []),
        keywords=[f"{src} to pdf", f"convert {src} to pdf", "image to pdf"])

add("image-to-pdf", category="pdf",
    h1="Image to PDF Converter", howto="How to convert images to PDF", page_title=f"Image to PDF Converter — Free, No Upload | {SITE['name']}",
    meta="Convert any image (JPG, PNG, WebP, GIF, BMP, SVG) to PDF online for free. Combine multiple images into one PDF. No upload — runs in your browser.",
    card="Image → PDF", card_desc="Any image format to PDF",
    lead="Drop JPG, PNG, WebP, GIF, BMP or SVG files and get a PDF back. Mix formats freely — they all end up as pages of one document.",
    config={"mode": "pdf", "dropTitle": "Drop images here or click to upload", "dropSub": "Any mix of formats — drop several to combine into one PDF"},
    why=[("Every format, one PDF", "Because conversion happens in the browser, any image your browser can display can become a PDF page — including SVG and AVIF."),
         ("Nothing is uploaded", "Receipts, IDs, contracts — the sort of thing people turn into PDFs is often sensitive. Here it never leaves your device.")],
    steps=[("Set the page", "A4, Letter or fit-to-image."), ("Upload", "drop files in the order you want them."), ("Download", "one PDF, ready to go.")],
    faq=[("Can I add more pages later?", "Not to an existing PDF — but you can re-run with the full set of images any time. Merging PDFs is a different job than this tool does."),
         ("Why JPEG inside the PDF?", "JPEG keeps PDF sizes small while staying visually lossless at 90%+. Line art and text screenshots look fine at 100%.")],
    keywords=["image to pdf", "picture to pdf", "photo to pdf converter"])

add("favicon-generator", category="other",
    h1="Favicon Generator", howto="How to make a favicon", page_title=f"Favicon Generator — PNG to ICO, Multi-Size | {SITE['name']}",
    meta="Generate a favicon.ico from any image online for free. Bundles 16×16, 32×32, 48×48 (and larger) into one .ico file. Transparency preserved, no upload.",
    card="Favicon Generator", card_desc="Any image → multi-size .ico",
    lead="Turn a logo or image into a proper multi-size favicon.ico. Tick the sizes you need, drop your file, done — transparency preserved.",
    config={"mode": "convert", "to": "ico", "dropTitle": "Drop your logo here or click to upload", "dropSub": "Works best with a square PNG or SVG, 256×256 or larger"},
    why=[("One file, several sizes", "Browsers pick the best-fitting size automatically from the ones bundled in the .ico — 16 px for tabs, 32 px for bookmarks, 48 px for Windows shortcuts."),
         ("Add it to your site", "Save the file as <code>favicon.ico</code> in your site's root folder and add <code>&lt;link rel=\"icon\" href=\"/favicon.ico\"&gt;</code> inside <code>&lt;head&gt;</code>.")],
    steps=[("Pick sizes", "16, 32 and 48 are pre-selected and cover nearly every case."), ("Upload", "drop a square logo — non-square images are centred with transparent padding."), ("Download", "rename to favicon.ico if needed and upload to your site.")],
    faq=[("Do I also need PNG favicons?", "Modern browsers accept a PNG via <code>&lt;link rel=\"icon\" type=\"image/png\"&gt;</code>, and iOS wants a 180×180 'apple-touch-icon' PNG. Use the Resize tool for those; the .ico covers legacy browsers and Windows."),
         ("Why does my icon look blurry?", "Start from a large, square source (256 px or more). Tiny sources upscaled into a favicon will look soft.")],
    keywords=["favicon generator", "png to ico", "create favicon"])

add("image-to-base64", category="other",
    h1="Image to Base64 Converter", howto="How to convert an image to Base64", page_title=f"Image to Base64 — Free Data URI Converter | {SITE['name']}",
    meta="Convert an image to a Base64 data URI online for free. Copy as raw Base64, <img> tag or CSS background. No upload — runs in your browser.",
    card="Image → Base64", card_desc="Data URI for HTML/CSS",
    lead="Get a Base64 data URI for any image, with one-click copies as a raw string, an <code>&lt;img&gt;</code> tag or a CSS <code>background-image</code>.",
    config={"mode": "base64", "dropTitle": "Drop an image here or click to upload", "dropSub": "Any format — the file is encoded as-is, without re-compression"},
    why=[("When Base64 makes sense", "Inlining tiny images (icons, 1×1 pixels, small logos) saves an HTTP request. For anything over ~10 KB a normal file is faster, because Base64 is ~33% bigger and can't be cached separately."),
         ("Exactly your bytes", "The image isn't re-encoded — the data URI contains your original file byte-for-byte, so quality is untouched.")],
    steps=[("Upload", "drop or pick an image."), ("Copy", "choose raw Base64, data URI, HTML tag or CSS."), ("Paste", "into your HTML, CSS, JSON or code.")],
    faq=[("Why is the output bigger than my file?", "Base64 represents every 3 bytes as 4 characters, so it's always about 33% larger. That's inherent to the encoding."),
         ("Is there a size limit?", "No hard limit, but very large images produce very large strings that are awkward to paste. Keep inlined images small.")],
    keywords=["image to base64", "base64 image encoder", "data uri generator"])

CATEGORIES = [
    ("convert", "Convert", "Change one image format into another — 28 conversions, every one in your browser."),
    ("compress", "Compress", "Shrink file sizes with real, tunable compression — including true palette-based PNG optimisation."),
    ("edit", "Edit", "Resize, rotate, flip and recolour without opening an editor."),
    ("pdf", "Image to PDF", "Turn one or many images into a print-ready PDF."),
    ("other", "Developer tools", "Favicons and Base64 for people building websites."),
]
POPULAR = ["png-to-jpg", "jpg-to-png", "webp-to-png", "png-to-webp", "compress-jpg", "compress-png", "jpg-to-pdf", "resize-image", "favicon-generator"]

# =====================================================================
# 4. RELATED-TOOL LINKS (the interlinking that matters for SEO)
# =====================================================================
def related_for(t):
    out = []
    def push(slug):
        if slug in TOOLS and slug != t["slug"] and slug not in out: out.append(slug)
    if t["category"] == "convert":
        for s, d in CONVERSIONS:
            if s == t["src"] and d != t["dst"]: push(f"{s}-to-{d}")
        for s, d in CONVERSIONS:
            if d == t["dst"] and s != t["src"]: push(f"{s}-to-{d}")
        push(f"compress-{t['dst']}"); push(f"{t['src']}-to-pdf"); push("resize-image")
        if t["dst"] == "ico": push("favicon-generator")
    elif t["category"] == "compress":
        f_ = t["fmt"]
        push(f"{f_}-to-webp"); push(f"{f_}-to-jpg"); push("resize-image")
        for x in ["jpg", "png", "webp"]: push(f"compress-{x}")
        push(f"{f_}-to-pdf")
    elif t["category"] == "edit":
        for x in ["resize-image", "rotate-image", "flip-image", "grayscale-image"]: push(x)
        push("compress-jpg"); push("png-to-jpg"); push("jpg-to-png"); push("image-to-pdf")
    elif t["category"] == "pdf":
        for x in ["jpg-to-pdf", "png-to-pdf", "webp-to-pdf", "image-to-pdf"]: push(x)
        push("compress-jpg"); push("resize-image"); push("png-to-jpg")
    else:
        push("png-to-ico"); push("svg-to-ico"); push("resize-image"); push("png-to-webp"); push("image-to-base64"); push("favicon-generator"); push("compress-png")
    return out[:9]

# =====================================================================
# 5. HTML BUILDING BLOCKS
# =====================================================================
CSS = (SRC / "styles.css").read_text(encoding="utf-8")
ENGINE = (SRC / "engine.js").read_text(encoding="utf-8")
esc = html.escape

def ad(slot, extra_class=""):
    if ADS["enabled"]:
        return (f'<div class="ad"><ins class="adsbygoogle" style="display:block" data-ad-client="{ADS["client"]}" '
                f'data-ad-slot="{ADS["slots"][slot]}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
                f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>')
    if not ADS.get("placeholders"): return ""
    labels = {"top": "Ad — responsive leaderboard (top)", "mid": "Ad — responsive rectangle (after tool)", "side": "Ad — 300×600 sidebar (desktop only)", "bottom": "Ad — responsive (bottom)"}
    return f'<div class="ad"><div class="ad-placeholder {extra_class}">{labels[slot]}<br><small>Set ADS.enabled = True in build.py once approved</small></div></div>'

def head_scripts():
    s = ""
    if ADS["enabled"]:
        s += f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS["client"]}" crossorigin="anonymous"></script>\n'
    if ANALYTICS["ga4"]:
        s += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS["ga4"]}"></script>\n'
              f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{ANALYTICS["ga4"]}");</script>\n')
    return s

THEME_BOOT = """<script>(function(){try{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>"""

SITE_JS = """<script>
(function(){
  if(location.protocol==='file:'){var up=/\\/blog\\/[^\\/]*$/.test(location.pathname)?'../':'';[].forEach.call(document.querySelectorAll('a[href^="/"]'),function(a){var h=a.getAttribute('href');if(h.indexOf('//')===0)return;var m=h.match(/^\\/([a-z0-9\\-\\/]*)(#.*)?$/);if(m){var t=m[1]||'index';if(t===''||t.slice(-1)==='/')t+='index';a.setAttribute('href',up+t+'.html'+(m[2]||''));}});}
  var b=document.getElementById('themeBtn');if(b){b.addEventListener('click',function(){var h=document.documentElement;var dark=h.getAttribute('data-theme')==='dark'||(!h.getAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);var n=dark?'light':'dark';h.setAttribute('data-theme',n);try{localStorage.setItem('theme',n);}catch(e){}});}
  var m=document.getElementById('menuBtn'),l=document.getElementById('navLinks');if(m&&l){m.addEventListener('click',function(){l.classList.toggle('open');m.setAttribute('aria-expanded',l.classList.contains('open'));});}
  var s=document.getElementById('toolSearch');if(s){var cards=[].slice.call(document.querySelectorAll('.tool-card')),cats=[].slice.call(document.querySelectorAll('.cat')),none=document.getElementById('noResults');
    s.addEventListener('input',function(){var q=s.value.trim().toLowerCase();var any=false;cards.forEach(function(c){var hit=!q||c.textContent.toLowerCase().indexOf(q)>-1||(c.getAttribute('data-k')||'').indexOf(q)>-1;c.style.display=hit?'':'none';if(hit)any=true;});
    cats.forEach(function(c){c.style.display=[].some.call(c.querySelectorAll('.tool-card'),function(x){return x.style.display!=='none';})?'':'none';});if(none)none.style.display=any?'none':'block';});}
})();
</script>"""

import base64 as _b64, mimetypes as _mt
def logo_data_uri():
    f = SITE.get("logo_file")
    if not f: return ""
    path = ROOT / f
    if not path.exists():
        print(f"warning: logo_file {f} not found — using letter-mark"); return ""
    mime = _mt.guess_type(str(path))[0] or "image/png"
    if mime == "image/svg+xml": mime = "image/svg+xml"
    return "data:" + mime + ";base64," + _b64.b64encode(path.read_bytes()).decode()

def logo_html():
    a, b = SITE.get("logo") or (SITE["name"], "")
    uri = logo_data_uri()
    text = f'<span>{esc(a)}<span class="grad">{esc(b)}</span></span>' if (SITE.get("logo_show_text", True) or not uri) else ""
    mark = f'<img class="logo-img" src="{uri}" alt="{esc(SITE["name"])} logo" width="28" height="28">' if uri else f'<span class="logo-mark">{esc(a[:1] or SITE["name"][:1])}</span>'
    return mark + text

def favicon_html():
    uri = logo_data_uri()
    if uri: return f'<link rel="icon" href="{uri}"><link rel="apple-touch-icon" href="/apple-touch-icon.png">'
    letter = esc((SITE.get("logo") or [SITE["name"]])[0][:1])
    return ('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\'%3E%3Crect width=\'32\' height=\'32\' rx=\'8\' fill=\'%236366f1\'/%3E%3Ctext x=\'16\' y=\'22\' font-size=\'18\' font-weight=\'900\' font-family=\'sans-serif\' text-anchor=\'middle\' fill=\'white\'%3E' + letter + '%3C/text%3E%3C/svg%3E">')

SOCIAL_ICONS = {
    "x": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 2H22l-7.4 8.5L23 22h-6.8l-5.3-6.9L4.8 22H1.7l7.9-9L1 2h7l4.8 6.3L18.9 2zm-1.2 18h1.9L7.4 3.9H5.4L17.7 20z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.6 1.6-1.6h1.7V4.3c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.4H7.4V14h2.8v8h3.3z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.9 8.5H3.5V21h3.4V8.5zM5.2 3a2 2 0 100 4 2 2 0 000-4zM21 13.3c0-3.6-1.9-5.2-4.5-5.2-2 0-2.9 1.1-3.4 1.9V8.5H9.7V21h3.4v-6.6c0-1.7.3-3.4 2.5-3.4 2.1 0 2.1 2 2.1 3.5V21H21v-7.7z"/></svg>',
    "github": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 00-3.2 19.5c.5.1.7-.2.7-.5v-1.9c-2.8.6-3.4-1.2-3.4-1.2-.4-1.1-1.1-1.4-1.1-1.4-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.5 9.5 0 015 0c1.9-1.3 2.8-1 2.8-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9v2.8c0 .3.2.6.7.5A10 10 0 0012 2z"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 7.2c-.3-1-1-1.8-2-2C19.2 4.7 12 4.7 12 4.7s-7.2 0-9 .5c-1 .3-1.7 1-2 2C.5 9 .5 12 .5 12s0 3 .5 4.8c.3 1 1 1.8 2 2 1.8.5 9 .5 9 .5s7.2 0 9-.5c1-.3 1.7-1 2-2 .5-1.8.5-4.8.5-4.8s0-3-.5-4.8zM9.8 15.1V8.9l6 3.1-6 3.1z"/></svg>',
}
def social_links(cls="social"):
    items = [(k, v) for k, v in SITE.get("social", {}).items() if v]
    if not items: return ""
    return f'<div class="{cls}">' + "".join(f'<a href="{esc(v)}" target="_blank" rel="noopener" aria-label="{k}" title="{k}">{SOCIAL_ICONS.get(k, k)}</a>' for k, v in items) + "</div>"

ICON = {
    "convert": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h11l-3-3M20 17H9l3 3"/><rect x="3" y="11" width="7" height="6" rx="1.5"/><rect x="14" y="7" width="7" height="6" rx="1.5"/></svg>',
    "compress": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14h5v5M20 10h-5V5M14 10l6-6M4 20l6-6"/></svg>',
    "resize": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M14 10l5-5M15 5h4v4M10 14l-5 5M9 19H5v-4"/></svg>',
    "rotate": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v5h-5"/></svg>',
    "flip": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M8 7H4v10h4M16 7h4v10h-4" /></svg>',
    "bw": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>',
    "pdf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>',
    "favicon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></svg>',
    "code": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
    "bolt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg>',
    "layers": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5M3 17l9 5 9-5"/></svg>',
    "gift": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="4" rx="1"/><path d="M5 12v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-8M12 8v13M12 8c-2-3-6-3-6-1s4 1 6 1zm0 0c2-3 6-3 6-1s-4 1-6 1z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 7"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "upload": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 8l5-5 5 5M5 21h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-2-2h-1.26a8 8 0 1 0-15.48 0H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2Z"/></svg>',
}
def tool_icon(t):
    m = {"compress": "compress", "pdf": "pdf"}
    if t["category"] in m: return ICON[m[t["category"]]]
    return ICON.get({"resize-image": "resize", "rotate-image": "rotate", "flip-image": "flip", "grayscale-image": "bw", "favicon-generator": "favicon", "image-to-base64": "code"}.get(t["slug"], "convert"))

FONT_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">'

def header(current=""):
    links = [("index.html#convert", "Convert"), ("index.html#compress", "Compress"), ("index.html#edit", "Edit"), ("index.html#pdf", "PDF"), ("blog/index.html", "Blog"), ("index.html", "All tools")]
    cur = ' aria-current="page"'
    a = "".join(f'<a href="{h}"{cur if h == current else ""}>{t}</a>' for h, t in links)
    return f'''<header class="site"><div class="nav">
  <a class="logo" href="index.html">{logo_html()}</a>
  <nav class="links" id="navLinks" aria-label="Main">{a}<a class="mobile-cta" href="png-to-jpg.html">Convert an image →</a></nav>
  <a class="btn btn-primary nav-cta" href="png-to-jpg.html">Convert an image {ICON["arrow"]}</a>
  <button class="theme-btn" id="themeBtn" aria-label="Toggle dark mode" title="Toggle dark mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 3a9 9 0 1 0 9 9c0-.5 0-1-.1-1.4A7 7 0 0 1 12 3z"/></svg></button>
  <button class="theme-btn menu-btn" id="menuBtn" aria-label="Menu" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
</div></header>'''

def footer():
    def col(title, slugs):
        items = "".join(f'<li><a href="{s}.html">{esc(TOOLS[s]["card"])}</a></li>' for s in slugs if s in TOOLS)
        return f"<div><h3>{title}</h3><ul>{items}</ul></div>"
    convert = ["png-to-jpg", "jpg-to-png", "webp-to-png", "png-to-webp", "jpg-to-webp", "webp-to-jpg", "gif-to-png", "svg-to-png", "avif-to-jpg", "bmp-to-png"]
    compress = ["compress-jpg", "compress-png", "compress-webp", "resize-image", "rotate-image", "flip-image", "grayscale-image"]
    pdf = ["jpg-to-pdf", "png-to-pdf", "webp-to-pdf", "image-to-pdf", "favicon-generator", "image-to-base64"]
    return f'''<footer class="site"><div class="foot">
  <div class="about"><a class="logo" href="index.html">{logo_html()}</a><p>{esc(SITE["tagline"])}. Nothing you drop here is ever uploaded — every tool runs on your own device.</p>{social_links()}</div>
  {col("Convert", convert)}{col("Compress &amp; edit", compress)}{col("PDF &amp; developer", pdf)}
  <div><h3>Company</h3><ul><li><a href="blog/index.html">Blog</a></li><li><a href="about.html">About</a></li><li><a href="contact.html">Contact</a></li><li><a href="privacy-policy.html">Privacy policy</a></li><li><a href="terms.html">Terms</a></li><li><a href="/sitemap.xml">Sitemap</a></li></ul></div>
</div><div class="foot-bottom"><div class="container"><span>© {SITE["year"]} {esc(SITE["name"])} · All processing happens in your browser.</span>{credit()}</div></div></footer>'''

def credit():
    d = SITE.get("designer") or {}
    if not d.get("name"): return ""
    if d.get("url"): return f'<span>Designed &amp; developed by <a href="{esc(d["url"])}" target="_blank" rel="noopener">{esc(d["name"])}</a></span>'
    return f'<span>Designed &amp; developed by {esc(d["name"])}</span>'

import re as _re
def clean(html_text):
    """Rewrite X.html links to /X when CLEAN_URLS is on (canonical, og:url, JSON-LD and sitemap included)."""
    if not CLEAN_URLS: return html_text
    def _strip_index(name):
        if name == "index": return ""
        if name.endswith("/index"): return name[:-5]   # blog/index -> blog/
        return name
    def link(m):
        name, frag = m.group(1), m.group(2) or ""
        return 'href="/' + _strip_index(name) + frag + '"'
    html_text = _re.sub(r'href="([a-z0-9\-/]+)\.html(#[^"]*)?"', link, html_text)
    dom = _re.escape(SITE["domain"])
    html_text = _re.sub(dom + r'/([a-z0-9\-/]+)\.html', lambda m: SITE["domain"] + "/" + _strip_index(m.group(1)), html_text)
    return html_text

def page_shell(*, title, meta, path, body, jsonld=None, current="", noindex=False, engine=False):
    canonical = f'{SITE["domain"]}/{path}' if path != "index.html" else SITE["domain"] + "/"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (jsonld or []))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{esc(SITE["name"])}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(meta)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE["domain"]}/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(meta)}"><meta name="twitter:image" content="{SITE["domain"]}/og-image.png">
<meta name="robots" content="{"noindex" if noindex else "index,follow,max-image-preview:large"}">
<meta name="theme-color" content="#6366f1">
{FONT_LINK}
{favicon_html()}
{THEME_BOOT}
{head_scripts()}<style>{CSS}</style>
{ld}
</head>
<body>
{header(current)}
{body}
{footer()}
{SITE_JS}
{"<script>" + ENGINE + "</script>" if engine else ""}
</body>
</html>'''

def _shell_clean(fn):
    def wrapped(*a, **k): return clean(fn(*a, **k))
    return wrapped
page_shell = _shell_clean(page_shell)

def breadcrumb(items):
    lis = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' if h else f"<li>{esc(t)}</li>" for t, h in items)
    return f'<ol class="crumbs">{lis}</ol>'

def tool_page(t):
    cat_name = dict((c[0], c[1]) for c in CATEGORIES)[t["category"]]
    faq = [(q, a.format(site=SITE["name"])) for q, a in t["faq"] + COMMON_FAQ]
    ht = t.get("howto", "")
    why_title = t.get("why_title") or (
        "Why " + ht[7:].rstrip(".") + "?" if ht.startswith("How to ") else "Why use " + t["h1"])
    why = "".join(f'<div class="card"><h3>{h}</h3><p>{p}</p></div>' for h, p in t["why"])
    steps = "".join(f'<li><strong>{esc(s)}</strong> — {esc(r)}</li>' for s, r in t["steps"])
    faq_html = "".join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in faq)
    related = "".join(f'<a href="{s}.html">{esc(TOOLS[s]["card"])}</a>' for s in related_for(t))
    body = f'''<main><div class="layout{'' if ad("side") else ' single'}"><div>
  {breadcrumb([("Home", "index.html"), (cat_name, f"index.html#{t['category']}"), (t["card"], None)])}
  <div class="eyebrow">{esc(cat_name)}</div>
  <h1>{esc(t["h1"])}</h1>
  <p class="lead">{t["lead"]}</p>
  {ad("top")}
  <div class="tool-shell"><div id="tool" data-config='{esc(json.dumps(t["config"]))}'></div></div>
  <div class="privacy-note">{ICON["lock"].replace('viewBox', 'width="15" height="15" viewBox')} 100% private — files never leave your device.</div>
  {ad("mid", "rect")}
  <section class="section"><h2>{esc(why_title)}</h2><div class="cards">{why}</div></section>
  <section class="section"><h2>{esc(t.get("howto", "How it works"))}</h2><ol class="steps">{steps}</ol></section>
  <section class="section faq"><h2>Frequently asked questions</h2>{faq_html}</section>
  <section class="section"><h2>Related tools</h2><div class="chips">{related}</div></section>
  {ad("bottom")}
</div>
{('<aside class="sidebar"><div class="sticky">' + ad("side", "tall") + '</div></aside>') if ad("side") else ''}
</div></main>'''
    jsonld = [
        {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": t["h1"], "applicationCategory": "MultimediaApplication",
         "operatingSystem": "Any (web browser)", "url": f'{SITE["domain"]}/{t["slug"]}.html', "description": t["meta"],
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "browserRequirements": "Requires JavaScript"},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faq]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["domain"] + "/"},
            {"@type": "ListItem", "position": 2, "name": cat_name, "item": f'{SITE["domain"]}/index.html#{t["category"]}'},
            {"@type": "ListItem", "position": 3, "name": t["card"], "item": f'{SITE["domain"]}/{t["slug"]}.html'}]},
    ]
    return page_shell(title=t["page_title"], meta=t["meta"], path=f'{t["slug"]}.html', body=body, jsonld=jsonld, engine=True)

def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)

def home_page():
    POP = ' <span class="tag">POPULAR</span>'
    cat_name = dict((c[0], c[1]) for c in CATEGORIES)

    def card(t, compact=False):
        k = esc(" ".join(t["keywords"]))
        if compact:
            return (f'<a class="tool-card compact" href="{t["slug"]}.html" data-k="{k}"><div class="row"><div class="ico">{tool_icon(t)}</div>'
                    f'<div><div class="t">{esc(t["card"])}</div><div class="d">{esc(t["card_desc"])}</div></div></div></a>')
        return (f'<a class="tool-card" href="{t["slug"]}.html" data-k="{k}"><div class="ico">{tool_icon(t)}</div>'
                f'<div class="t">{esc(t["card"])}{POP if t["slug"] in POPULAR else ""}</div><div class="d">{esc(t["card_desc"])}</div><span class="arrow">{ICON["arrow"]}</span></a>')

    featured = ["png-to-jpg", "compress-png", "jpg-to-pdf", "webp-to-png", "resize-image", "favicon-generator"]
    featured_html = "".join(card(TOOLS[x]) for x in featured)

    # conversion matrix: rows = source, cols = target
    sources = ["png", "jpg", "webp", "gif", "bmp", "avif", "svg", "ico"]; targets = ["png", "jpg", "webp", "bmp", "ico"]
    pairs = {(a, b) for a, b in CONVERSIONS}
    head = "".join(f"<th>{F[t]['label']}</th>" for t in targets)
    rows = ""
    for src in sources:
        cells = ""
        for dst in targets:
            if (src, dst) in pairs: cells += f'<td><a href="{src}-to-{dst}.html" title="{F[src]["label"]} to {F[dst]["label"]}" aria-label="{F[src]["label"]} to {F[dst]["label"]}">{ICON["arrow"]}</a></td>'
            else: cells += '<td><span class="na">—</span></td>'
        rows += f'<tr><th>{F[src]["label"]}<small>{esc(F[src]["full"])}</small></th>{cells}</tr>'
    matrix = f'<div class="matrix-wrap"><table class="matrix"><thead><tr><th>From ↓ &nbsp; To →</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'

    # category blocks (searchable): convert list is compact, others compact too
    blocks = ""
    for cid, cname, cdesc in CATEGORIES:
        items = [t for t in TOOLS.values() if t["category"] == cid]
        grid = "".join(card(t, compact=True) for t in items)
        blocks += f'<section class="block cat" id="{cid}"><div class="block-head"><div><div class="eyebrow">{esc(cname)}</div><h2>{esc(cname if cname.lower().endswith("tools") else cname + " tools")}</h2><p class="sub">{esc(cdesc)}</p></div></div><div class="compact-grid">{grid}</div></section>'

    faq = [("Are my images really not uploaded?", "Correct. Every tool here is JavaScript running in your browser — there is no server-side processing at all. You can even load a page, disconnect from the internet, and it keeps working."),
           ("Which formats are supported?", "Input: PNG, JPG, WebP, GIF, BMP, AVIF, SVG and ICO — anything your browser can display. Output: PNG, JPG, WebP, BMP, ICO and PDF. HEIC isn't supported because browsers can't decode it."),
           ("Is there a file size or count limit?", "No. Batch as many files as you like; the only limit is your device's memory."),
           ("How is this free?", "The site is supported by unobtrusive ads. There's no premium tier, no watermark and no sign-up.")]
    faq_html = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq)
    fmts = "".join(f"<span>{F[k]['label']}</span>" for k in ["png", "jpg", "webp", "gif", "bmp", "avif", "svg", "ico"]) + "<span>PDF</span>"
    hero_cfg = esc(json.dumps({"mode": "convert", "to": "webp", "dropTitle": "Drop an image to try it", "dropSub": "Pick a format below, get the file back instantly"}))
    ck = ICON["check"]

    body = f'''<main style="padding-top:0">
  <section class="hero"><div class="container"><div class="hero-grid">
    <div>
      <div class="pill-badge"><span class="dot">{ck}</span>{len(TOOLS)} free tools · no upload · no sign-up</div>
      <h1>Every image tool you need.<br><span class="grad">Private by design.</span></h1>
      <p class="sub">Convert, compress, resize and turn images into PDFs — instantly, in your browser. Your files never leave your device, because there is no server to send them to.</p>
      <div class="hero-actions"><a class="btn btn-primary btn-lg" href="#convert">Browse all tools {ICON["arrow"]}</a><a class="btn btn-secondary btn-lg" href="compress-png.html">Compress a PNG</a></div>
      <div class="hero-proof"><span>{ck} No file limits</span><span>{ck} Batch + ZIP download</span><span>{ck} Works offline</span><span>{ck} Free forever</span></div>
    </div>
    <div class="hero-tool"><span class="tool-label">Live demo</span><div class="tool-shell"><div id="tool" data-config='{hero_cfg}'></div></div></div>
  </div></div></section>

  <div class="strip"><div class="container">
    <div class="formats"><span class="lbl">Supports</span>{fmts}</div>
    <div class="stats"><div class="stat"><b>{len(TOOLS)}</b><small>tools</small></div><div class="stat"><b>0</b><small>uploads, ever</small></div><div class="stat"><b>100%</b><small>free</small></div><div class="stat"><b>∞</b><small>files per batch</small></div></div>
  </div></div>

  <div class="container">
    {ad("top")}
    <section class="block"><div class="block-head"><div><div class="eyebrow">Start here</div><h2>Most-used tools</h2><p class="sub">The six things people come here for most often.</p></div><a class="more" href="#convert">See all {len(TOOLS)} tools →</a></div>
      <div class="feature-grid">{featured_html}</div></section>

    <section class="block"><div class="block-head"><div><div class="eyebrow">Convert anything</div><h2>Every conversion, one grid</h2><p class="sub">Pick your source format on the left and the format you need across the top. {len(CONVERSIONS)} conversions, all in your browser.</p></div></div>
      {matrix}</section>

    <section class="block" style="padding-top:56px"><div class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="toolSearch" type="search" placeholder="Search all tools — “webp to png”, “compress”, “pdf”…" aria-label="Search tools"></div></section>
    {blocks}
    <p class="no-results" id="noResults">No tool matches that search.</p>

    <section class="block"><div class="block-head"><div><div class="eyebrow">How it works</div><h2>Three steps. No account.</h2></div></div>
      <div class="how">
        <div class="how-step"><div class="n">1</div><h3>Drop your file</h3><p>Drag it onto the box, click to browse, or paste from your clipboard. Drop several at once for batch processing.</p></div>
        <div class="how-step"><div class="n">2</div><h3>Pick the settings</h3><p>Choose a format, drag the quality slider, set a size — every option has a sensible default so you can skip this.</p></div>
        <div class="how-step"><div class="n">3</div><h3>Download</h3><p>Grab each file, or everything at once as a ZIP. Nothing was uploaded, so there is nothing to delete afterwards.</p></div>
      </div></section>

    <section class="block"><div class="block-head"><div><div class="eyebrow">Why {esc(SITE["name"])}</div><h2>Built the way image tools should be</h2></div></div>
      <div class="why">
        <div class="why-card"><div class="ico">{ICON["lock"]}</div><h3>Private by design</h3><p>Processing happens on your device with the browser's own Canvas API. No server ever sees your files — turn off Wi-Fi and it still works.</p></div>
        <div class="why-card"><div class="ico">{ICON["bolt"]}</div><h3>Instant</h3><p>No upload queue, no waiting for a download link. Conversion starts the moment you drop a file.</p></div>
        <div class="why-card"><div class="ico">{ICON["layers"]}</div><h3>Real compression</h3><p>True palette-based PNG optimisation, tunable JPG and WebP quality, and honest before/after sizes on every file.</p></div>
        <div class="why-card"><div class="ico">{ICON["gift"]}</div><h3>Free, no catch</h3><p>No account, no watermark, no file limits, no premium tier. Supported by unobtrusive ads.</p></div>
      </div></section>

    {ad("bottom")}
    <section class="block faq" style="max-width:820px"><div class="block-head"><div><div class="eyebrow">FAQ</div><h2>Questions, answered</h2></div></div>{faq_html}</section>

    <section class="cta-band"><h2>Ready when you are.</h2><p>Pick a tool, drop a file, and you're done — no sign-up, no upload, no waiting.</p><a class="btn btn-lg" href="png-to-jpg.html">Convert an image now {ICON["arrow"]}</a></section>
  </div>
</main>'''
    jsonld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": SITE["domain"] + "/", "description": SITE["tagline"]},
        {"@context": "https://schema.org", "@type": "Organization", "name": SITE["name"], "url": SITE["domain"] + "/", "logo": SITE["domain"] + "/og-image.png",
         "email": SITE["contact_email"], "sameAs": [v for v in SITE.get("social", {}).values() if v]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
    ]
    return page_shell(title=f'{SITE["name"]} — Free Online Image Converter & Compressor',
                      meta=f"{len(TOOLS)} free image tools that run in your browser: convert PNG, JPG, WebP, GIF, BMP, AVIF, SVG; compress; resize; image to PDF; favicon. No upload, no sign-up.",
                      path="index.html", body=body, jsonld=jsonld, current="index.html", engine=True)

def prose_page(path, title, meta, h1, sections, noindex=False):
    sec = "".join(f"<h2>{esc(h)}</h2>{p}" for h, p in sections)
    body = f'<main><div class="container prose" style="max-width:800px">{breadcrumb([("Home", "index.html"), (h1, None)])}<h1>{esc(h1)}</h1>{sec}</div></main>'
    return page_shell(title=title, meta=meta, path=path, body=body, noindex=noindex)

def static_pages():
    n, e, d = SITE["name"], SITE["contact_email"], SITE["domain"]
    yield "about.html", prose_page("about.html", f"About | {n}", f"{n} is a set of free image tools that run entirely in your browser.", f"About {n}", [
        ("What this is", f"<p>{n} is a collection of {len(TOOLS)} small, focused image tools — converters, compressors, a resizer, an image-to-PDF maker and a few developer utilities. Every one of them runs entirely inside your web browser.</p>"),
        ("Why 'in your browser' matters", "<p>Most online image tools upload your file to a server, process it there, and send the result back. That's slower than it needs to be, and it means a copy of your file — which might be a passport scan, a contract, a private photo — passes through someone else's infrastructure.</p><p>Here, your browser does the work using its built-in Canvas API. The file is read from your disk into memory, processed, and offered back as a download. It never touches a network connection. You can verify this yourself: load a tool, switch off your Wi-Fi, and it keeps working.</p>"),
        ("How it's funded", "<p>The site is supported by ads. There's no premium tier, no sign-up, no watermark, and no limit on how many files you process.</p>"),
        # TODO: replace the paragraph below with something real and specific about you — it helps both AdSense review and search engines.
        ("Who makes it", f"<p>{n} is designed, built and maintained by <a href='https://ihtishamkhalil.com/' target='_blank' rel='noopener'>Ihtisham Khalil</a>, an independent web developer. It started as a small converter built for personal use, after getting tired of image tools that either uploaded files to a server, added a watermark, or hid the download behind a sign-up. Every tool here is added and tested by hand, and the whole site runs on a single shared engine so a fix in one place fixes every tool.</p><p>Questions, bug reports and format requests are welcome at <a href='mailto:{e}'>{e}</a>.</p>"),
    ])
    c = SITE.get("contact", {}); rows = [("Email", f"<a href='mailto:{e}'>{e}</a>")]
    if c.get("phone"): rows.append(("Phone", f"<a href='tel:{c['phone'].replace(' ', '')}'>{esc(c['phone'])}</a>"))
    if c.get("whatsapp"): rows.append(("WhatsApp", f"<a href='https://wa.me/{c['whatsapp']}' target='_blank' rel='noopener'>Message on WhatsApp</a>"))
    if c.get("location"): rows.append(("Location", esc(c["location"])))
    if c.get("hours"): rows.append(("Response time", esc(c["hours"])))
    d = SITE.get("designer") or {}
    if d.get("name"): rows.append(("Built by", f"<a href='{esc(d['url'])}' target='_blank' rel='noopener'>{esc(d['name'])}</a>" if d.get("url") else esc(d["name"])))
    table = "<table class='contact-table'>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows) + "</table>"
    yield "contact.html", prose_page("contact.html", f"Contact | {n}", f"Get in touch with {n} — bug reports, feature requests and questions.", "Contact", [
        ("Get in touch", f"<p>Found a bug, want a format added, or have a question? Use any of the channels below — replies usually within a couple of days.</p>{table}{social_links('social big')}"),
        ("Before you write about a conversion problem", "<p>It helps enormously to include: which tool page you were on, your browser and version, the format and rough size of the file, and what happened (an error message, a blank result, a wrong colour…). Because nothing is uploaded, we can't see your file — so a description is all we have to go on.</p>"),
    ])
    yield "privacy-policy.html", prose_page("privacy-policy.html", f"Privacy Policy | {n}", f"{n} privacy policy: your images are never uploaded; how ads and cookies work.", "Privacy Policy", [
        ("Your images", f"<p>{n}'s tools process images entirely within your web browser. Files you drop into a tool are never uploaded to our servers and are never seen by us — all processing happens locally on your device using your browser's built-in capabilities.</p>"),
        ("Information we collect", "<p>We do not require an account and do not collect personal information to use the tools. Like most websites, our hosting provider may log basic technical information such as IP address, browser type and pages visited, for security and diagnostic purposes." + (" We use Google Analytics to understand which tools are used most; it sets cookies and collects anonymised usage data — see Google's privacy policy for details." if ANALYTICS["ga4"] else "") + "</p>"),
        ("Advertising", "<p>This site displays ads served by Google AdSense. Google and its partners may use cookies to serve ads based on your prior visits to this or other websites. You can opt out of personalised advertising at <a href='https://adssettings.google.com' target='_blank' rel='noopener'>Google Ads Settings</a>. Visitors in the EU/UK are shown a consent prompt before any advertising cookies are set.</p>"),
        ("Cookies", "<p>We set one item in your browser's local storage to remember your light/dark theme choice. All other cookies are set by third-party services (advertising, analytics) as described above.</p>"),
        ("Contact", f"<p>Questions about this policy: <a href='mailto:{e}'>{e}</a>.</p><p><em>Last updated: {datetime.date.today():%d %B %Y}</em></p>"),
    ])
    yield "terms.html", prose_page("terms.html", f"Terms of Use | {n}", f"Terms of use for {n}'s free browser-based image tools.", "Terms of Use", [
        ("Use of the tools", f"<p>{n} is provided free of charge for personal and commercial use. You may process any images you have the right to use. Because processing happens on your device, you retain full ownership and responsibility for your files and their content.</p>"),
        ("No warranty", "<p>The tools are provided 'as is'. We test them carefully, but we can't guarantee they are error-free or suitable for every purpose. Always keep your original files — the tools never modify them, but you should check results before deleting anything.</p>"),
        ("Changes", "<p>We may update, add or remove tools at any time. These terms may change; continued use after a change means you accept the updated terms.</p>"),
        ("Contact", f"<p><a href='mailto:{e}'>{e}</a></p>"),
    ])
    yield "404.html", prose_page("404.html", f"Page not found | {n}", "That page doesn't exist.", "Page not found", [
        ("Sorry — that page isn't here", "<p>The link may be out of date. Head back to the <a href='index.html'>full list of tools</a>, or try one of the popular ones: <a href='png-to-jpg.html'>PNG to JPG</a>, <a href='compress-jpg.html'>Compress JPG</a>, <a href='jpg-to-pdf.html'>JPG to PDF</a>.</p>"),
    ], noindex=True)

# =====================================================================
# 6. .htaccess for Apache/LiteSpeed hosts (Hostinger, cPanel, etc.)
#    Netlify/Vercel ignore this file — harmless to ship everywhere.
# =====================================================================
HTACCESS = """# --- PixelShrink (generated by build.py) ---
Options -Indexes
ErrorDocument 404 /404.html

<IfModule mod_rewrite.c>
RewriteEngine On

# Force HTTPS
RewriteCond %{HTTPS} !=on
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Redirect www -> non-www (delete these 2 lines if you prefer www)
RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]
RewriteRule ^ https://%1%{REQUEST_URI} [L,R=301]

# /blog/index.html -> /blog/   and  /index.html -> /
RewriteCond %{THE_REQUEST} \\s/([^\\s?]*)index\\.html[\\s?] [NC]
RewriteRule ^ /%1 [R=301,L]

# /png-to-jpg.html  ->  /png-to-jpg   (permanent, keeps old links working)
RewriteCond %{THE_REQUEST} \\s/([^\\s?]+)\\.html[\\s?] [NC]
RewriteRule ^ /%1 [R=301,L]

# /png-to-jpg  ->  serve png-to-jpg.html
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME}.html -f
RewriteRule ^([^.]+)$ $1.html [L]
</IfModule>

# Compression
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css text/plain text/xml application/javascript application/json image/svg+xml
</IfModule>

# Browser caching (pages short, so updates show quickly; assets long)
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/html "access plus 1 hour"
ExpiresByType text/xml "access plus 1 day"
ExpiresByType image/svg+xml "access plus 1 month"
</IfModule>

# Security headers
<IfModule mod_headers.c>
Header set X-Content-Type-Options "nosniff"
Header set Referrer-Policy "strict-origin-when-cross-origin"
Header set X-Frame-Options "SAMEORIGIN"
</IfModule>
"""

def logo_raster(size):
    """Logo as an RGBA Pillow image at `size` px, or None. PNG logos are resized; SVG logos are
    rasterised with cairosvg if installed, otherwise via a headless Chromium (playwright) if installed."""
    f = SITE.get("logo_file")
    if not f or not (ROOT / f).exists(): return None
    from PIL import Image
    path = ROOT / f
    if path.suffix.lower() != ".svg":
        return Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    try:
        import cairosvg, io
        return Image.open(io.BytesIO(cairosvg.svg2png(url=str(path), output_width=size, output_height=size))).convert("RGBA")
    except Exception: pass
    try:
        from playwright.sync_api import sync_playwright
        import io
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": size, "height": size}, device_scale_factor=1)
            pg.set_content(f'<body style="margin:0;background:transparent"><img src="{logo_data_uri()}" style="width:{size}px;height:{size}px;display:block"></body>')
            png = pg.screenshot(omit_background=True); b.close()
        return Image.open(io.BytesIO(png)).convert("RGBA")
    except Exception: return None

def make_og_image():
    """1200×630 social-share image. Uses Pillow if installed; otherwise skips with a note."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("note: Pillow not installed — og-image.png not generated (pip install pillow). Social previews will lack an image.")
        return
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (15, 17, 23))
    d = ImageDraw.Draw(img)
    for x in range(W):  # gradient band
        t = x / W; d.line([(x, 0), (x, 14)], fill=(int(99 + (139 - 99) * t), int(102 + (92 - 102) * t), int(241 + (246 - 241) * t)))
    def font(size, bold=True):
        for f in (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]) + ["arialbd.ttf", "arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
            try: return ImageFont.truetype(f, size)
            except Exception: pass
        return ImageFont.load_default()
    a, b = SITE.get("logo") or (SITE["name"], "")
    icon = logo_raster(160)
    if icon is not None:
        img.paste(icon, (80, 60), icon)
        # apple touch icon (180px) for iOS home-screen bookmarks
        logo_raster(180).save(DIST / "apple-touch-icon.png")
    else:
        d.rounded_rectangle((80, 100, 160, 180), radius=20, fill=(99, 102, 241))
        d.text((120, 140), (a or SITE["name"])[:1], font=font(48), fill="white", anchor="mm")
    tx = 270 if icon is not None else 190
    f1 = font(84); d.text((tx, 140), a, font=f1, fill="white", anchor="lm")
    d.text((tx + d.textlength(a, font=f1), 140), b, font=f1, fill=(139, 140, 248), anchor="lm")
    d.text((80, 300), SITE["tagline"], font=font(44, False), fill=(226, 228, 236))
    d.text((80, 380), f"{len(TOOLS)} tools · Convert · Compress · Resize · PDF · No upload", font=font(30, False), fill=(146, 152, 172))
    d.text((80, 540), SITE["domain"].replace("https://", "").replace("http://", ""), font=font(30, False), fill=(146, 152, 172))
    img.save(DIST / "og-image.png", optimize=True)

# =====================================================================
# 7. BUILD
# =====================================================================
# =====================================================================
# 6b. BLOG
# =====================================================================
def _tool_card_inline(slug, label=None):
    t = TOOLS.get(slug)
    if not t:
        return ""
    return (f'<a class="tool-cta" href="{slug}.html"><div class="ico">{tool_icon(t)}</div>'
            f'<div><b>{esc(label or t["card"])}</b><span>{esc(t["card_desc"])} — free, no upload</span></div>'
            f'<span class="go">{ICON["arrow"]}</span></a>')

def _fmt_date(d):
    try: return datetime.date.fromisoformat(d).strftime("%d %B %Y")
    except Exception: return d

def article_page(a, all_articles):
    body_html, toc = blogmod.render_markdown(a["body"], _tool_card_inline)
    toc_html = ""
    if len(toc) >= 3:
        items = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
        toc_html = f'<nav class="toc" aria-label="On this page"><b>On this page</b><ul>{items}</ul></nav>'
    tools_html = ""
    if a["tools"]:
        cards = "".join(_tool_card_inline(sl) for sl in a["tools"] if sl in TOOLS)
        if cards: tools_html = f'<section class="section"><h2>Tools mentioned in this article</h2><div class="tool-ctas">{cards}</div></section>'
    others = [x for x in all_articles if x["slug"] != a["slug"]][:3]
    more = ""
    if others:
        cards = "".join(f'<a class="post-card" href="blog/{o["slug"]}.html"><div class="t">{esc(o["h1"])}</div>'
                        f'<div class="d">{esc(o["excerpt"])}</div><div class="m">{o["minutes"]} min read</div></a>' for o in others)
        more = f'<section class="section"><h2>More from the blog</h2><div class="post-grid">{cards}</div></section>'
    updated = f' · Updated {_fmt_date(a["updated"])}' if a["updated"] else ""
    body = f'''<main><div class="layout{'' if ad("side") else ' single'}"><div>
  {breadcrumb([("Home", "index.html"), ("Blog", "blog/index.html"), (a["h1"], None)])}
  <article class="post">
    <div class="eyebrow">Guide</div>
    <h1>{esc(a["h1"])}</h1>
    <div class="post-meta">{_fmt_date(a["date"])}{updated} · {a["minutes"]} min read · by <a href="{esc((SITE.get("designer") or {}).get("url", "about.html"))}">{esc((SITE.get("designer") or {}).get("name", SITE["name"]))}</a></div>
    {ad("top")}
    {toc_html}
    <div class="prose-body">{body_html}</div>
  </article>
  {tools_html}
  {ad("mid", "rect")}
  {more}
  {ad("bottom")}
</div>
{('<aside class="sidebar"><div class="sticky">' + ad("side", "tall") + '</div></aside>') if ad("side") else ''}
</div></main>'''
    url = f'{SITE["domain"]}/blog/{a["slug"]}.html'
    author = (SITE.get("designer") or {}).get("name", SITE["name"])
    jsonld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": a["h1"], "description": a["description"],
         "datePublished": a["date"], "dateModified": a["updated"] or a["date"],
         "author": {"@type": "Person", "name": author, "url": (SITE.get("designer") or {}).get("url", SITE["domain"])},
         "publisher": {"@type": "Organization", "name": SITE["name"], "logo": {"@type": "ImageObject", "url": SITE["domain"] + "/og-image.png"}},
         "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "image": SITE["domain"] + "/og-image.png",
         "wordCount": a["words"], "inLanguage": "en"},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["domain"] + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f'{SITE["domain"]}/blog/'},
            {"@type": "ListItem", "position": 3, "name": a["h1"], "item": url}]},
    ]
    return page_shell(title=a["title"], meta=a["description"], path=f'blog/{a["slug"]}.html', body=body, jsonld=jsonld)

def blog_index(articles):
    cards = "".join(
        f'<a class="post-card lg" href="blog/{a["slug"]}.html"><div class="t">{esc(a["h1"])}</div>'
        f'<div class="d">{esc(a["excerpt"])}</div><div class="m">{_fmt_date(a["date"])} · {a["minutes"]} min read</div></a>'
        for a in articles)
    body = f'''<main><div class="container" style="max-width:900px">
  {breadcrumb([("Home", "index.html"), ("Blog", None)])}
  <div class="eyebrow">Blog</div>
  <h1>Guides to image formats, compression and the web</h1>
  <p class="lead">Practical, jargon-light explanations from the person who built the tools — what the formats actually do, which one to use, and how to make your images smaller without wrecking them.</p>
  {ad("top")}
  <h2 class="sr-head">Latest articles</h2>
  <div class="post-grid">{cards}</div>
  {ad("bottom")}
</div></main>'''
    jsonld = [{"@context": "https://schema.org", "@type": "Blog", "name": f'{SITE["name"]} Blog', "url": f'{SITE["domain"]}/blog/',
               "blogPost": [{"@type": "BlogPosting", "headline": a["h1"], "url": f'{SITE["domain"]}/blog/{a["slug"]}.html',
                             "datePublished": a["date"], "description": a["description"]} for a in articles]}]
    return page_shell(title=f'Blog — Image Format Guides & Tips | {SITE["name"]}',
                      meta="Guides on image formats, compression, favicons and web performance — from the developer behind ConvertPicto's free browser-based image tools.",
                      path="blog/index.html", body=body, jsonld=jsonld, current="blog/index.html")

def build():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    pages = []
    (DIST / "index.html").write_text(home_page(), encoding="utf-8"); pages.append(("index.html", "1.0", "weekly"))
    for t in TOOLS.values():
        (DIST / f'{t["slug"]}.html').write_text(tool_page(t), encoding="utf-8"); pages.append((f'{t["slug"]}.html', "0.8", "monthly"))
    articles = blogmod.load_articles(ROOT)
    if articles:
        (DIST / "blog").mkdir(exist_ok=True)
        (DIST / "blog" / "index.html").write_text(blog_index(articles), encoding="utf-8"); pages.append(("blog/index.html", "0.7", "weekly"))
        for a in articles:
            (DIST / "blog" / f'{a["slug"]}.html').write_text(article_page(a, articles), encoding="utf-8")
            pages.append((f'blog/{a["slug"]}.html', "0.7", "monthly"))
    for name, content in static_pages():
        (DIST / name).write_text(content, encoding="utf-8")
        if name != "404.html": pages.append((name, "0.3", "yearly"))
    today = datetime.date.today().isoformat()
    urls = "".join(f'<url><loc>{SITE["domain"] + "/" if p == "index.html" else SITE["domain"] + "/" + p}</loc><lastmod>{today}</lastmod><changefreq>{c}</changefreq><priority>{pr}</priority></url>' for p, pr, c in pages)
    (DIST / "sitemap.xml").write_text(clean(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'), encoding="utf-8")
    (DIST / ".htaccess").write_text(HTACCESS, encoding="utf-8")
    make_og_image()
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n", encoding="utf-8")
    print(f"built {len(pages) + 1} pages into {DIST}/  ({len(TOOLS)} tools, {len(articles)} articles)")

if __name__ == "__main__":
    build()
