"""Full-site functional test. Optional — needs:  pip install playwright pillow pypdf && playwright install chromium
Run:  python3 tests/test_site.py
"""
import base64, io, json, re, sys, zipfile, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops, ImageStat
import pypdf

DIST = pathlib.Path(__file__).resolve().parent.parent / "dist"
A = pathlib.Path(__file__).resolve().parent / "assets"
if not (A / "photo.png").exists():
    import subprocess; subprocess.run([sys.executable, str(A.parent / "make_assets.py")], check=True)
ASSET = {"png": A/"photo.png", "jpg": A/"photo.jpg", "webp": A/"photo.webp", "gif": A/"photo.gif",
         "bmp": A/"photo.bmp", "svg": A/"vector.svg", "ico": A/"icon.ico", "avif": A/"photo.png"}  # no AVIF encoder here; page still exercised
failures, notes = [], []

def fetch_blob(page, href):
    b64 = page.evaluate("async (u) => { const r = await fetch(u); const b = await r.arrayBuffer(); let s=''; const a=new Uint8Array(b); for (let i=0;i<a.length;i+=0x8000) s+=String.fromCharCode.apply(null,a.subarray(i,i+0x8000)); return btoa(s); }", href)
    return base64.b64decode(b64)

def run_tool(page, slug, files, expect_ext, timeout=30000):
    page.goto((DIST / f"{slug}.html").as_uri())
    page.wait_for_selector("#dropZone", timeout=5000)
    page.set_input_files("#fileInput", [str(f) for f in files])
    page.wait_for_selector(".result-row.done, .result-row.error", timeout=timeout)
    page.wait_for_function("() => !document.querySelector('.result-row.pending')", timeout=timeout)
    rows = page.query_selector_all("#resultsList .result-row")
    out = []
    for r in rows:
        cls = r.get_attribute("class")
        if "error" in cls:
            failures.append(f"{slug}: ERROR row — {r.inner_text()}"); continue
        a = r.query_selector("a.btn-primary")
        if a is None:  # base64 rows have no download link
            out.append((None, None, r)); continue
        name = a.get_attribute("download"); href = a.get_attribute("href")
        if not name.lower().endswith("." + expect_ext): failures.append(f"{slug}: expected .{expect_ext}, got {name}")
        out.append((name, fetch_blob(page, href), r))
    return out

def check_image(slug, data, fmt_expect, min_w=None):
    try:
        im = Image.open(io.BytesIO(data)); im.load()
    except Exception as e:
        failures.append(f"{slug}: PIL cannot open output ({e})"); return None
    if fmt_expect and im.format != fmt_expect: failures.append(f"{slug}: PIL says format {im.format}, expected {fmt_expect}")
    if min_w and im.width < min_w: failures.append(f"{slug}: unexpected width {im.width}")
    return im

PIL_FMT = {"png": "PNG", "jpg": "JPEG", "webp": "WEBP", "bmp": "BMP", "ico": "ICO"}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(accept_downloads=True)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" and "net::" not in m.text else None)

    sys.path.insert(0, str(DIST.parent)); import build
    tools = [{"slug": t["slug"], "category": t["category"], "src": t.get("src"), "dst": t.get("dst")} for t in build.TOOLS.values()]
    conv = [t for t in tools if t["category"] == "convert"]

    # ---- 1. every conversion page with its real source format ----
    for t in conv:
        src, dst = t["src"], t["dst"]
        res = run_tool(page, t["slug"], [ASSET[src]], dst)
        if not res: failures.append(f"{t['slug']}: no result"); continue
        name, data, row = res[0]
        im = check_image(t["slug"], data, PIL_FMT[dst])
        if im and dst == "ico":
            if not im.size == (48, 48) and not im.size == (256, 256): notes.append(f"{t['slug']}: ico largest frame {im.size}")
        if im and src == "svg" and dst != "ico":
            if im.width != 1024 and src == "svg": failures.append(f"{t['slug']}: svg without size should render 1024 wide, got {im.width}")
        if im and dst == "jpg":
            # transparent corner should be white-filled (default background)
            if im.getpixel((5, 5))[:3] != (255, 255, 255) and src in ("png", "webp", "svg", "gif"):
                notes.append(f"{t['slug']}: top-left pixel {im.getpixel((5,5))} (expected white fill for transparent source)")
        print(f"ok  {t['slug']:14s} -> {name} {len(data)} bytes {im.size if im else ''}")

    # ---- 2. svg with explicit size keeps it ----
    res = run_tool(page, "svg-to-png", [A/"sized.svg"], "png")
    im = check_image("svg-to-png(sized)", res[0][1], "PNG")
    if im and im.size != (300, 150): failures.append(f"svg sized: got {im.size}, expected (300,150)")

    # ---- 3. compressors ----
    for fmt in ["jpg", "webp"]:
        res = run_tool(page, f"compress-{fmt}", [ASSET[fmt]], fmt)
        name, data, row = res[0]
        im = check_image(f"compress-{fmt}", data, PIL_FMT[fmt])
        src_size = ASSET[fmt].stat().st_size
        if len(data) >= src_size: failures.append(f"compress-{fmt}: not smaller ({len(data)} vs {src_size})")
        print(f"ok  compress-{fmt}: {src_size} -> {len(data)} ({round((1-len(data)/src_size)*100)}% smaller)")

    # real PNG compressor: photo + graphic
    for asset in ["photo.png", "graphic.png"]:
        res = run_tool(page, "compress-png", [A/asset], "png")
        name, data, row = res[0]
        im = check_image("compress-png:" + asset, data, "PNG")
        src = Image.open(A/asset).convert("RGBA"); src_size = (A/asset).stat().st_size
        if im:
            if im.mode != "P": failures.append(f"compress-png:{asset}: output mode {im.mode}, expected P (indexed)")
            if len(data) >= src_size: failures.append(f"compress-png:{asset}: not smaller ({len(data)} vs {src_size})")
            out = im.convert("RGBA")
            # compare only opaque region for photo (alpha preserved separately)
            diff = ImageChops.difference(src.convert("RGB"), out.convert("RGB"))
            mean = sum(ImageStat.Stat(diff).mean) / 3
            alpha_src = src.getchannel("A"); alpha_out = out.getchannel("A")
            adiff = ImageStat.Stat(ImageChops.difference(alpha_src, alpha_out)).mean[0]
            if mean > 12: failures.append(f"compress-png:{asset}: mean pixel diff too high ({mean:.1f})")
            if adiff > 3: failures.append(f"compress-png:{asset}: alpha not preserved (mean alpha diff {adiff:.1f})")
            print(f"ok  compress-png {asset}: {src_size} -> {len(data)} ({round((1-len(data)/src_size)*100)}% smaller), mode={im.mode}, colors={len(im.getcolors(256) or [])}, mean diff={mean:.2f}, alpha diff={adiff:.2f}")

    # ---- 4. edit tools ----
    res = run_tool(page, "grayscale-image", [A/"photo.jpg"], "jpg")
    im = check_image("grayscale", res[0][1], "JPEG")
    if im:
        px = im.convert("RGB").getpixel((320, 210));
        if max(px) - min(px) > 6: failures.append(f"grayscale: pixel not gray {px}")
        print("ok  grayscale-image", im.size, px)

    # rotate page defaults to 90°
    res = run_tool(page, "rotate-image", [A/"photo.jpg"], "jpg")
    im = check_image("rotate", res[0][1], "JPEG")
    if im and im.size != (420, 640): failures.append(f"rotate 90: size {im.size}, expected (420,640)")
    print("ok  rotate-image", im.size if im else None)

    # flip page defaults to horizontal flip → compare with PIL
    res = run_tool(page, "flip-image", [A/"graphic.png"], "png")
    im = check_image("flip", res[0][1], "PNG")
    if im:
        ref = Image.open(A/"graphic.png").convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
        d = sum(ImageStat.Stat(ImageChops.difference(ref, im.convert("RGBA"))).mean) / 4
        if d > 1: failures.append(f"flip: differs from PIL flip (mean {d})")
        print("ok  flip-image mean diff vs PIL", round(d, 3))

    # resize: width only → aspect kept
    page.goto((DIST / "resize-image.html").as_uri()); page.wait_for_selector("#dropZone")
    page.fill("input[aria-label='Width']", "320")
    page.set_input_files("#fileInput", str(A/"photo.png"))
    page.wait_for_selector(".result-row.done", timeout=20000)
    a = page.query_selector("#resultsList a.btn-primary"); data = fetch_blob(page, a.get_attribute("href"))
    im = check_image("resize-w", data, "PNG")
    if im and im.size != (320, 210): failures.append(f"resize width-only: {im.size}, expected (320,210)")
    print("ok  resize-image (width 320)", im.size if im else None)
    # resize: percent preset
    page.goto((DIST / "resize-image.html").as_uri()); page.wait_for_selector("#dropZone")
    page.click(".chip:has-text('50%')")
    page.set_input_files("#fileInput", str(A/"photo.png"))
    page.wait_for_selector(".result-row.done", timeout=20000)
    a = page.query_selector("#resultsList a.btn-primary"); data = fetch_blob(page, a.get_attribute("href"))
    im = check_image("resize-50", data, "PNG")
    if im and im.size != (320, 210): failures.append(f"resize 50%: {im.size}, expected (320,210)")
    print("ok  resize-image (50%)", im.size if im else None)
    # resize: exact w+h, aspect unlocked
    page.goto((DIST / "resize-image.html").as_uri()); page.wait_for_selector("#dropZone")
    page.fill("input[aria-label='Width']", "100"); page.fill("input[aria-label='Height']", "100"); page.uncheck("#lockAspect")
    page.click(".format-btn[data-format='webp']")
    page.set_input_files("#fileInput", str(A/"photo.jpg"))
    page.wait_for_selector(".result-row.done", timeout=20000)
    a = page.query_selector("#resultsList a.btn-primary"); data = fetch_blob(page, a.get_attribute("href"))
    im = check_image("resize-exact", data, "WEBP")
    if im and im.size != (100, 100): failures.append(f"resize exact: {im.size}")
    print("ok  resize-image (exact 100x100 webp)", im.size if im else None)

    # ---- 5. PDF tools ----
    for slug, files in [("jpg-to-pdf", [A/"photo.jpg", A/"graphic.png"]), ("png-to-pdf", [A/"photo.png"]), ("webp-to-pdf", [A/"photo.webp"]), ("image-to-pdf", [A/"vector.svg", A/"photo.gif", A/"photo.bmp"])]:
        res = run_tool(page, slug, files, "pdf")
        name, data, row = res[0]
        try:
            r = pypdf.PdfReader(io.BytesIO(data)); n = len(r.pages)
            if n != len(files): failures.append(f"{slug}: {n} pages, expected {len(files)}")
            box = r.pages[0].mediabox
            imgs = r.pages[0].images
            if len(imgs) != 1: failures.append(f"{slug}: page has {len(imgs)} images")
            print(f"ok  {slug}: {n} page(s), mediabox {float(box.width):.0f}x{float(box.height):.0f}, {len(data)} bytes")
        except Exception as e:
            failures.append(f"{slug}: pypdf failed: {e}")
    # fit-to-image page size
    page.goto((DIST / "jpg-to-pdf.html").as_uri()); page.wait_for_selector("#dropZone")
    page.select_option("select.select", "fit")
    page.set_input_files("#fileInput", str(A/"photo.jpg"))
    page.wait_for_selector(".result-row.done", timeout=20000)
    a = page.query_selector("#resultsList a.btn-primary"); data = fetch_blob(page, a.get_attribute("href"))
    r = pypdf.PdfReader(io.BytesIO(data)); box = r.pages[0].mediabox
    if abs(float(box.width) - 480) > 1 or abs(float(box.height) - 315) > 1: failures.append(f"pdf fit: mediabox {box}")
    print(f"ok  jpg-to-pdf fit-to-image: {float(box.width):.2f}x{float(box.height):.2f} pt")

    # ---- 6. favicon + base64 ----
    res = run_tool(page, "favicon-generator", [A/"graphic.png"], "ico")
    im = check_image("favicon", res[0][1], "ICO")
    if im:
        ico = Image.open(io.BytesIO(res[0][1])); sizes = sorted(ico.ico.sizes()) if hasattr(ico, "ico") else None
        print("ok  favicon-generator sizes:", sizes)
        if sizes and sizes != [(16, 16), (32, 32), (48, 48)]: failures.append(f"favicon sizes {sizes}")
    page.goto((DIST / "image-to-base64.html").as_uri()); page.wait_for_selector("#dropZone")
    page.set_input_files("#fileInput", str(A/"graphic.png"))
    page.wait_for_selector("textarea.b64", timeout=10000)
    val = page.input_value("textarea.b64")
    if not val.startswith("data:image/png;base64,"): failures.append("base64: bad prefix")
    dec = base64.b64decode(val.split(",")[1])
    if dec != (A/"graphic.png").read_bytes(): failures.append("base64: decoded bytes differ from original")
    print("ok  image-to-base64 round-trips byte-for-byte")

    # ---- 7. batch + ZIP download ----
    page.goto((DIST / "png-to-jpg.html").as_uri()); page.wait_for_selector("#dropZone")
    page.set_input_files("#fileInput", [str(A/"photo.png"), str(A/"graphic.png"), str(A/"vector.svg")])
    page.wait_for_function("() => document.querySelectorAll('.result-row.done').length === 3", timeout=20000)
    with page.expect_download() as dl:
        page.click("#zipBtn")
    path = dl.value.path()
    with zipfile.ZipFile(path) as z:
        names = sorted(z.namelist()); bad = z.testzip()
        if bad: failures.append(f"zip: corrupt entry {bad}")
        if names != ["graphic.jpg", "photo.jpg", "vector.jpg"]: failures.append(f"zip names {names}")
        for n in names: check_image("zip:" + n, z.read(n), "JPEG")
    print("ok  batch of 3 -> zip", names, "(testzip clean)")
    # clear button
    page.click("#clearBtn")
    if page.query_selector_all("#resultsList .result-row"): failures.append("clear button did not clear")

    # ---- 8. background colour for transparent -> jpg ----
    page.goto((DIST / "png-to-jpg.html").as_uri()); page.wait_for_selector("#dropZone")
    page.evaluate("() => { const c=document.querySelector('input[type=color]'); c.value='#ff0000'; c.dispatchEvent(new Event('input')); }")
    page.set_input_files("#fileInput", str(A/"photo.png"))
    page.wait_for_selector(".result-row.done", timeout=20000)
    a = page.query_selector("#resultsList a.btn-primary"); data = fetch_blob(page, a.get_attribute("href"))
    im = Image.open(io.BytesIO(data)).convert("RGB"); px = im.getpixel((5, 5))
    if not (px[0] > 240 and px[1] < 20 and px[2] < 20): failures.append(f"background colour not applied: {px}")
    print("ok  transparent->jpg background colour applied", px)

    # ---- 9. format switching on a convert page (all 5 outputs) ----
    for fmt in ["png", "jpg", "webp", "bmp", "ico"]:
        page.goto((DIST / "gif-to-png.html").as_uri()); page.wait_for_selector("#dropZone")
        page.click(f".format-btn[data-format='{fmt}']")
        page.set_input_files("#fileInput", str(A/"photo.gif"))
        page.wait_for_selector(".result-row.done, .result-row.error", timeout=20000)
        row = page.query_selector("#resultsList .result-row")
        if "error" in row.get_attribute("class"): failures.append(f"switch to {fmt}: {row.inner_text()}"); continue
        a = row.query_selector("a.btn-primary"); check_image("switch:" + fmt, fetch_blob(page, a.get_attribute("href")), PIL_FMT[fmt])
    print("ok  output-format switching on a convert page (5 formats)")

    # ---- 9b. LIVE SETTINGS: changing a control re-processes files already in the list ----
    def wait_settled(pg):
        pg.wait_for_function("() => !document.querySelector('.result-row.pending') && !document.querySelector('.result-row.updating')", timeout=20000)
    def first_row_size_bytes(pg):
        a = pg.query_selector("#resultsList .result-row a.btn-primary"); return len(fetch_blob(pg, a.get_attribute("href")))
    # quality slider on compress-jpg
    page.goto((DIST / "compress-jpg.html").as_uri()); page.wait_for_selector("#dropZone")
    page.set_input_files("#fileInput", str(A/"photo.jpg")); wait_settled(page)
    before = first_row_size_bytes(page)
    page.evaluate("() => { const r=document.querySelector('input[type=range]'); r.value=25; r.dispatchEvent(new Event('input')); }")
    page.wait_for_timeout(400); wait_settled(page)
    after = first_row_size_bytes(page)
    if not after < before * 0.8: failures.append(f"live quality: size did not drop ({before} -> {after})")
    print(f"ok  live quality slider: {before} -> {after} bytes without re-upload")
    # format switch on png-to-jpg
    page.goto((DIST / "png-to-jpg.html").as_uri()); page.wait_for_selector("#dropZone")
    page.set_input_files("#fileInput", [str(A/"photo.png"), str(A/"graphic.png")]); wait_settled(page)
    page.click(".format-btn[data-format='webp']"); page.wait_for_timeout(300); wait_settled(page)
    names = page.eval_on_selector_all("#resultsList a.btn-primary", "els => els.map(e => e.getAttribute('download'))")
    if not all(n.endswith(".webp") for n in names) or len(names) != 2: failures.append(f"live format switch: {names}")
    for a in page.query_selector_all("#resultsList a.btn-primary"): check_image("live-webp", fetch_blob(page, a.get_attribute("href")), "WEBP")
    print("ok  live format switch: both rows re-encoded ->", names)
    # resize width change
    page.goto((DIST / "resize-image.html").as_uri()); page.wait_for_selector("#dropZone")
    page.set_input_files("#fileInput", str(A/"photo.png")); wait_settled(page)
    page.fill("input[aria-label='Width']", "200"); page.wait_for_timeout(500); wait_settled(page)
    im = check_image("live-resize", first_row_size_bytes.__class__ and fetch_blob(page, page.query_selector("#resultsList a.btn-primary").get_attribute("href")), "PNG")
    if im and im.size != (200, 131): failures.append(f"live resize: {im.size}")
    print("ok  live resize: re-processed to", im.size if im else None)
    # pdf combine toggle rebuilds rows from stored files
    page.goto((DIST / "jpg-to-pdf.html").as_uri()); page.wait_for_selector("#dropZone")
    page.set_input_files("#fileInput", [str(A/"photo.jpg"), str(A/"graphic.png")]); wait_settled(page)
    if len(page.query_selector_all("#resultsList .result-row")) != 1: failures.append("pdf combine: expected 1 row")
    page.uncheck("#combine"); wait_settled(page)
    rows = page.query_selector_all("#resultsList .result-row")
    if len(rows) != 2: failures.append(f"pdf uncombine: expected 2 rows, got {len(rows)}")
    page.evaluate("() => { const r=document.querySelector('input[aria-label=Margin]'); r.value=0; r.dispatchEvent(new Event('input')); }"); page.wait_for_timeout(500); wait_settled(page)
    print("ok  live PDF: combine toggle rebuilt", len(rows), "rows; margin change re-processed")
    # remove button
    page.click("#resultsList .result-row .row-remove"); 
    if len(page.query_selector_all("#resultsList .result-row")) != 1: failures.append("remove button did not remove row")
    print("ok  per-row remove button")

    # ---- 10. static pages load + links resolve + JSON-LD parses ----
    all_pages = sorted(DIST.glob("*.html")) + sorted(DIST.glob("blog/*.html"))
    for f in all_pages:
        page.goto(f.as_uri())
        hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
        for h in hrefs:
            if h.startswith(("http", "mailto:", "#", "data:")): continue
            target = h.split("#")[0]
            if target in ("", "/"): target = "index.html"
            if "." not in target.split("/")[-1]: target += ".html"
            resolved = (DIST / target.lstrip("/")).resolve() if target.startswith("/") else (f.parent / target).resolve()
            if not resolved.exists(): failures.append(f"{f.name}: broken link {h} -> {resolved}")
        for ld in page.eval_on_selector_all("script[type='application/ld+json']", "els => els.map(e => e.textContent)"):
            json.loads(ld)
        if not page.query_selector("title") or not page.query_selector("meta[name=description]") or not page.query_selector("link[rel=canonical]"):
            failures.append(f"{f.name}: missing SEO head tags")
    titles = {}
    for f in all_pages:
        t = re.search(r"<title>(.*?)</title>", f.read_text()).group(1)
        titles.setdefault(t, []).append(f.name)
    for t, fs in titles.items():
        if len(fs) > 1: failures.append(f"duplicate title across {fs}")
    print(f"ok  {len(all_pages)} pages: links resolve, JSON-LD valid, titles unique, head tags present")

    # ---- 10b. BLOG: index, articles, structure, links, JSON-LD ----
    import re as _re2
    arts = sorted(f for f in (DIST / "blog").glob("*.html") if f.name != "index.html")
    if len(arts) < 1: failures.append("blog: no articles built")
    page.goto((DIST / "blog" / "index.html").as_uri())
    cards = page.query_selector_all(".post-card")
    if len(cards) != len(arts): failures.append(f"blog index: {len(cards)} cards vs {len(arts)} articles")
    for f in arts:
        page.goto(f.as_uri())
        txt = page.inner_text(".prose-body") if page.query_selector(".prose-body") else ""
        words = len(txt.split())
        if words < 300: failures.append(f"{f.name}: only {words} words")
        if not page.query_selector("h1"): failures.append(f"{f.name}: no h1")
        h2s = page.query_selector_all(".prose-body h2")
        if len(h2s) < 3: failures.append(f"{f.name}: {len(h2s)} h2 headings")
        ids = [h.get_attribute("id") for h in h2s]
        if not all(ids): failures.append(f"{f.name}: h2 missing id (TOC anchors broken)")
        toc_links = page.eval_on_selector_all(".toc a", "els => els.map(e => e.getAttribute('href'))")
        for tl in toc_links:
            if not page.query_selector(tl): failures.append(f"{f.name}: TOC anchor {tl} has no target")
        if not page.query_selector(".tool-cta"): failures.append(f"{f.name}: no tool CTA")
        for cta in page.eval_on_selector_all(".tool-cta", "els => els.map(e => e.getAttribute('href'))"):
            tgt = cta.split("#")[0]
            if "." not in tgt.split("/")[-1]: tgt += ".html"
            resolved = (f.parent / tgt).resolve() if not tgt.startswith("/") else (DIST / tgt.lstrip("/")).resolve()
            if not resolved.exists(): failures.append(f"{f.name}: CTA points at missing {cta}")
        lds = page.eval_on_selector_all("script[type='application/ld+json']", "els => els.map(e => e.textContent)")
        types = [json.loads(x).get("@type") for x in lds]
        if "Article" not in types: failures.append(f"{f.name}: no Article JSON-LD")
        art = json.loads([x for x in lds if json.loads(x).get("@type") == "Article"][0])
        for k in ("headline", "datePublished", "author", "description"):
            if not art.get(k): failures.append(f"{f.name}: Article JSON-LD missing {k}")
        if page.query_selector(".prose-body table") and not page.query_selector(".table-wrap"):
            failures.append(f"{f.name}: table not wrapped for mobile scroll")
        # no raw markdown left over
        if _re2.search(r"(\*\*|:::|^## )", txt, _re2.M): failures.append(f"{f.name}: unrendered markdown in body")
        print(f"ok  blog/{f.name}: {words} words, {len(h2s)} sections, {len(page.query_selector_all('.tool-cta'))} CTAs")
    print(f"ok  blog: {len(arts)} articles + index")

    # ---- 11. home search + theme toggle + mobile menu ----
    page.goto((DIST / "index.html").as_uri())
    total = len(page.query_selector_all(".tool-card"))
    page.fill("#toolSearch", "pdf")
    vis = page.evaluate("() => [...document.querySelectorAll('.tool-card')].filter(c => c.style.display !== 'none').length")
    if not (0 < vis < total): failures.append(f"search: {vis}/{total} visible for 'pdf'")
    page.fill("#toolSearch", "zzzz")
    if page.eval_on_selector("#noResults", "e => getComputedStyle(e).display") == "none": failures.append("search: no-results message not shown")
    page.click("#themeBtn")
    if page.evaluate("() => document.documentElement.getAttribute('data-theme')") not in ("dark", "light"): failures.append("theme toggle did nothing")
    print(f"ok  home search ({vis}/{total} for 'pdf'), theme toggle")

    # ---- 12. screenshots ----
    for name, w, url in [("home-desktop", 1280, "index.html"), ("tool-desktop", 1280, "png-to-jpg.html"), ("home-mobile", 390, "index.html"), ("tool-mobile", 390, "compress-png.html")]:
        pg = ctx.new_page(); pg.set_viewport_size({"width": w, "height": 900})
        pg.goto((DIST / url).as_uri())
        if "tool" in name:
            pg.set_input_files("#fileInput", [str(A/"photo.png"), str(A/"graphic.png")])
            pg.wait_for_function("() => document.querySelectorAll('.result-row.done').length === 2", timeout=20000)
        if name == "tool-mobile": pg.click("#menuBtn")
        pg.screenshot(path=str(A.parent / f"shot-{name}.png"), full_page=(name != "home-desktop"))
        pg.close()
    pg = ctx.new_page(); pg.set_viewport_size({"width": 1280, "height": 900}); pg.goto((DIST / "jpg-to-pdf.html").as_uri()); pg.click("#themeBtn"); pg.screenshot(path=str(A.parent / "shot-dark.png")); pg.close()

    browser.close()

print("\n" + "=" * 60)
for n in notes: print("note:", n)
if errors: print("JS ERRORS:", errors)
if failures or errors:
    print(f"FAILURES ({len(failures)}):"); [print(" -", f) for f in failures]; sys.exit(1)
print("ALL SITE TESTS PASSED")
