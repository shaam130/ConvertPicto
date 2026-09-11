/* ===========================================================
   PixelShrink engine — every tool on the site runs on this file.
   100% client-side. Nothing is ever uploaded.

   A page declares what it is with:
     <div id="tool" data-config='{"mode":"convert","from":"png","to":"jpg"}'></div>
   and this engine renders the right controls and does the work.

   Modes: convert | compress | resize | rotate | flip | grayscale | pdf | base64
   =========================================================== */
(function () {
  'use strict';

  const root = document.getElementById('tool');
  if (!root) return;

  let cfg = {};
  try { cfg = JSON.parse(root.getAttribute('data-config') || '{}'); } catch (e) { cfg = {}; }
  cfg.mode = cfg.mode || 'convert';

  /* ---------- format metadata ---------- */
  const FORMATS = {
    png:  { label: 'PNG',  ext: 'png',  mime: 'image/png',  lossy: false, alpha: true,  native: true },
    jpg:  { label: 'JPG',  ext: 'jpg',  mime: 'image/jpeg', lossy: true,  alpha: false, native: true },
    webp: { label: 'WebP', ext: 'webp', mime: 'image/webp', lossy: true,  alpha: true,  native: true },
    bmp:  { label: 'BMP',  ext: 'bmp',  mime: 'image/bmp',  lossy: false, alpha: false, native: false },
    ico:  { label: 'ICO',  ext: 'ico',  mime: 'image/x-icon', lossy: false, alpha: true, native: false },
  };
  const OUTPUT_ORDER = ['png', 'jpg', 'webp', 'bmp', 'ico'];

  /* ---------- small helpers ---------- */
  const $ = (sel, el) => (el || root).querySelector(sel);
  const el = (tag, attrs, children) => {
    const n = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      if (k === 'class') n.className = attrs[k];
      else if (k === 'html') n.innerHTML = attrs[k];
      else if (k === 'text') n.textContent = attrs[k];
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    }
    (children || []).forEach((c) => c && n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c));
    return n;
  };
  const humanSize = (b) => b < 1024 ? b + ' B' : b < 1048576 ? (b / 1024).toFixed(1) + ' KB' : (b / 1048576).toFixed(2) + ' MB';
  const baseName = (name) => name.replace(/\.[^.]+$/, '');
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  /* ---------- CRC32 (PNG + ZIP) ---------- */
  const CRC_TABLE = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
    return t;
  })();
  function crc32(bytes) {
    let c = 0xFFFFFFFF;
    for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
  }

  /* ---------- image loading (handles SVG without intrinsic size) ---------- */
  function readAsText(file) {
    return new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = () => rej(new Error('Could not read file')); r.readAsText(file); });
  }
  async function loadImage(file) {
    const isSvg = /svg/i.test(file.type) || /\.svg$/i.test(file.name);
    let blob = file;
    if (isSvg) {
      // Browsers give an SVG without explicit width/height a default 300×150 box.
      // If the file lacks a real pixel size, render it 1024px wide at its viewBox aspect ratio.
      const text = await readAsText(file);
      const open = /<svg\b[^>]*>/i.exec(text);
      const tag = open ? open[0] : '';
      const px = (attr) => { const m = new RegExp(attr + '\\s*=\\s*["\']\\s*([\\d.]+)\\s*(px)?\\s*["\']', 'i').exec(tag); return m ? parseFloat(m[1]) : 0; };
      const hasSize = px('width') > 0 && px('height') > 0;
      if (!hasSize) {
        const vb = /viewBox\s*=\s*["']\s*([\d.\-]+)[\s,]+([\d.\-]+)[\s,]+([\d.\-]+)[\s,]+([\d.\-]+)/i.exec(tag);
        let w = 1024, h = 1024;
        if (vb) { const vw = parseFloat(vb[3]), vh = parseFloat(vb[4]); if (vw > 0 && vh > 0) { w = 1024; h = Math.round(1024 * vh / vw); } }
        const cleaned = tag.replace(/\s(width|height)\s*=\s*["'][^"']*["']/gi, '');
        const patched = text.replace(tag, cleaned.replace(/<svg\b/i, '<svg width="' + w + '" height="' + h + '"'));
        blob = new Blob([patched], { type: 'image/svg+xml' });
      }
    }
    const url = URL.createObjectURL(blob);
    const img = await new Promise((resolve, reject) => {
      const i = new Image();
      i.onload = () => resolve(i);
      i.onerror = () => reject(new Error(isSvg ? 'This SVG could not be rendered' : 'This file could not be decoded as an image by your browser'));
      i.src = url;
    });
    return { img, url, width: img.naturalWidth || img.width, height: img.naturalHeight || img.height };
  }

  /* ---------- canvas building (resize / rotate / flip / grayscale / flatten) ---------- */
  function buildCanvas(src, opts) {
    const angle = ((opts.rotate || 0) % 360 + 360) % 360;
    let w = opts.width || src.width, h = opts.height || src.height;
    const swap = angle === 90 || angle === 270;
    const canvas = document.createElement('canvas');
    canvas.width = swap ? h : w;
    canvas.height = swap ? w : h;
    const ctx = canvas.getContext('2d');
    if (opts.background) { ctx.fillStyle = opts.background; ctx.fillRect(0, 0, canvas.width, canvas.height); }
    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate(angle * Math.PI / 180);
    ctx.scale(opts.flipH ? -1 : 1, opts.flipV ? -1 : 1);
    if (opts.grayscale) ctx.filter = 'grayscale(100%)';
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(src.img, -w / 2, -h / 2, w, h);
    ctx.restore();
    return canvas;
  }

  function encodeNative(canvas, mime, quality) {
    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob && blob.type === mime) resolve(blob);
        else reject(new Error("Your browser can't export " + mime.replace('image/', '').toUpperCase() + ' — try the latest Chrome, Firefox, or Edge'));
      }, mime, quality);
    });
  }
  const blobBytes = async (blob) => new Uint8Array(await blob.arrayBuffer());

  /* ---------- BMP encoder (24-bit, uncompressed) ---------- */
  function encodeBmp(canvas) {
    const w = canvas.width, h = canvas.height;
    const data = canvas.getContext('2d').getImageData(0, 0, w, h).data;
    const rowSize = Math.floor((24 * w + 31) / 32) * 4;
    const pixelArraySize = rowSize * h;
    const buf = new ArrayBuffer(54 + pixelArraySize);
    const v = new DataView(buf);
    v.setUint8(0, 0x42); v.setUint8(1, 0x4D);
    v.setUint32(2, 54 + pixelArraySize, true);
    v.setUint32(10, 54, true);
    v.setUint32(14, 40, true);
    v.setInt32(18, w, true); v.setInt32(22, h, true);
    v.setUint16(26, 1, true); v.setUint16(28, 24, true);
    v.setUint32(34, pixelArraySize, true);
    v.setInt32(38, 2835, true); v.setInt32(42, 2835, true);
    let o = 54;
    for (let y = h - 1; y >= 0; y--) {
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4;
        v.setUint8(o++, data[i + 2]); v.setUint8(o++, data[i + 1]); v.setUint8(o++, data[i]);
      }
      o += rowSize - w * 3;
    }
    return new Blob([buf], { type: 'image/bmp' });
  }

  /* ---------- ICO encoder (PNG-compressed, multi-size) ---------- */
  async function encodeIco(src, sizes) {
    const images = [];
    for (const size of sizes) {
      // fit the image inside a square, centered, transparent padding (no stretching)
      const c = document.createElement('canvas'); c.width = c.height = size;
      const ctx = c.getContext('2d');
      ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
      const s = Math.min(size / src.width, size / src.height);
      const dw = src.width * s, dh = src.height * s;
      ctx.drawImage(src.img, (size - dw) / 2, (size - dh) / 2, dw, dh);
      images.push({ size, bytes: await blobBytes(await encodeNative(c, 'image/png')) });
    }
    let offset = 6 + images.length * 16;
    const header = new Uint8Array(6); const hv = new DataView(header.buffer);
    hv.setUint16(2, 1, true); hv.setUint16(4, images.length, true);
    const dir = new Uint8Array(images.length * 16); const dv = new DataView(dir.buffer);
    images.forEach((im, i) => {
      const b = i * 16;
      dv.setUint8(b, im.size >= 256 ? 0 : im.size); dv.setUint8(b + 1, im.size >= 256 ? 0 : im.size);
      dv.setUint16(b + 4, 1, true); dv.setUint16(b + 6, 32, true);
      dv.setUint32(b + 8, im.bytes.length, true); dv.setUint32(b + 12, offset, true);
      offset += im.bytes.length;
    });
    return new Blob([header, dir, ...images.map((i) => i.bytes)], { type: 'image/x-icon' });
  }

  /* ---------- Real PNG compression: palette quantization + indexed PNG encoder ---------- */
  function quantize(rgba, count, maxColors, dither, width) {
    // 1. collect samples (transparent pixels handled separately)
    const step = Math.max(1, Math.floor(count / 150000));
    const samples = [];
    let hasTransparent = false;
    for (let i = 0; i < count; i += step) {
      const o = i * 4;
      if (rgba[o + 3] === 0) { hasTransparent = true; continue; }
      samples.push([rgba[o], rgba[o + 1], rgba[o + 2], rgba[o + 3]]);
    }
    if (!hasTransparent) for (let i = 0; i < count; i++) if (rgba[i * 4 + 3] === 0) { hasTransparent = true; break; }
    const target = Math.max(2, maxColors - (hasTransparent ? 1 : 0));

    // 2. median cut
    const stats = (box) => {
      const mn = [255, 255, 255, 255], mx = [0, 0, 0, 0];
      for (const p of box.pix) for (let c = 0; c < 4; c++) { if (p[c] < mn[c]) mn[c] = p[c]; if (p[c] > mx[c]) mx[c] = p[c]; }
      let axis = 0, range = -1;
      for (let c = 0; c < 4; c++) { const r = mx[c] - mn[c]; if (r > range) { range = r; axis = c; } }
      box.axis = axis; box.range = range;
    };
    let boxes = [{ pix: samples.length ? samples : [[0, 0, 0, 255]] }];
    stats(boxes[0]);
    while (boxes.length < target) {
      let bi = -1, br = 0;
      for (let i = 0; i < boxes.length; i++) if (boxes[i].pix.length > 1 && boxes[i].range > br) { br = boxes[i].range; bi = i; }
      if (bi < 0) break;
      const box = boxes[bi], ax = box.axis;
      box.pix.sort((a, b) => a[ax] - b[ax]);
      const mid = box.pix.length >> 1;
      const b1 = { pix: box.pix.slice(0, mid) }, b2 = { pix: box.pix.slice(mid) };
      stats(b1); stats(b2);
      boxes.splice(bi, 1, b1, b2);
    }
    const palette = boxes.map((b) => {
      let r = 0, g = 0, bl = 0, a = 0;
      for (const p of b.pix) { r += p[0]; g += p[1]; bl += p[2]; a += p[3]; }
      const k = b.pix.length;
      return [Math.round(r / k), Math.round(g / k), Math.round(bl / k), Math.round(a / k)];
    });
    let transparentIndex = -1;
    if (hasTransparent) { transparentIndex = palette.length; palette.push([0, 0, 0, 0]); }

    // 3. map every pixel to nearest palette entry (with cache + optional dithering)
    const cache = new Map();
    const nearest = (r, g, b, a) => {
      const key = ((r >> 2) << 18) | ((g >> 2) << 12) | ((b >> 2) << 6) | (a >> 2);
      let idx = cache.get(key);
      if (idx !== undefined) return idx;
      let best = 0, bd = Infinity;
      for (let i = 0; i < palette.length; i++) {
        if (i === transparentIndex) continue;
        const p = palette[i];
        const dr = p[0] - r, dg = p[1] - g, db = p[2] - b, da = p[3] - a;
        const d = dr * dr + dg * dg + db * db + da * da * 2;
        if (d < bd) { bd = d; best = i; }
      }
      cache.set(key, best);
      return best;
    };
    const indices = new Uint8Array(count);
    if (!dither) {
      for (let i = 0; i < count; i++) {
        const o = i * 4;
        indices[i] = rgba[o + 3] === 0 && transparentIndex >= 0 ? transparentIndex : nearest(rgba[o], rgba[o + 1], rgba[o + 2], rgba[o + 3]);
      }
    } else {
      const height = count / width;
      let errCur = new Float32Array((width + 2) * 3), errNext = new Float32Array((width + 2) * 3);
      for (let y = 0; y < height; y++) {
        errNext.fill(0);
        for (let x = 0; x < width; x++) {
          const i = y * width + x, o = i * 4, e = (x + 1) * 3;
          const a = rgba[o + 3];
          if (a === 0 && transparentIndex >= 0) { indices[i] = transparentIndex; continue; }
          const r = clamp(Math.round(rgba[o] + errCur[e]), 0, 255);
          const g = clamp(Math.round(rgba[o + 1] + errCur[e + 1]), 0, 255);
          const b = clamp(Math.round(rgba[o + 2] + errCur[e + 2]), 0, 255);
          const idx = nearest(r, g, b, a);
          indices[i] = idx;
          const p = palette[idx];
          const er = r - p[0], eg = g - p[1], eb = b - p[2];
          errCur[e + 3] += er * 7 / 16; errCur[e + 4] += eg * 7 / 16; errCur[e + 5] += eb * 7 / 16;
          errNext[e - 3] += er * 3 / 16; errNext[e - 2] += eg * 3 / 16; errNext[e - 1] += eb * 3 / 16;
          errNext[e] += er * 5 / 16; errNext[e + 1] += eg * 5 / 16; errNext[e + 2] += eb * 5 / 16;
          errNext[e + 3] += er / 16; errNext[e + 4] += eg / 16; errNext[e + 5] += eb / 16;
        }
        const t = errCur; errCur = errNext; errNext = t;
      }
    }
    return { palette, indices };
  }

  async function zlibDeflate(bytes) {
    if (typeof CompressionStream === 'undefined') throw new Error('PNG compression needs a newer browser (Chrome 80+, Firefox 113+, Safari 16.4+)');
    const cs = new CompressionStream('deflate');
    const writer = cs.writable.getWriter();
    writer.write(bytes); writer.close();
    return new Uint8Array(await new Response(cs.readable).arrayBuffer());
  }

  function pngChunk(type, data) {
    const out = new Uint8Array(12 + data.length);
    const v = new DataView(out.buffer);
    v.setUint32(0, data.length);
    for (let i = 0; i < 4; i++) out[4 + i] = type.charCodeAt(i);
    out.set(data, 8);
    const crcBody = out.subarray(4, 8 + data.length);
    v.setUint32(8 + data.length, crc32(crcBody));
    return out;
  }

  async function encodeIndexedPng(canvas, maxColors, dither) {
    const w = canvas.width, h = canvas.height;
    const rgba = canvas.getContext('2d').getImageData(0, 0, w, h).data;
    const { palette, indices } = quantize(rgba, w * h, maxColors, dither, w);
    const bitDepth = palette.length <= 2 ? 1 : palette.length <= 4 ? 2 : palette.length <= 16 ? 4 : 8;
    const rowBytes = Math.ceil(w * bitDepth / 8);
    const raw = new Uint8Array((rowBytes + 1) * h);
    for (let y = 0; y < h; y++) {
      const rowStart = y * (rowBytes + 1);
      raw[rowStart] = 0; // filter: none
      if (bitDepth === 8) {
        raw.set(indices.subarray(y * w, y * w + w), rowStart + 1);
      } else {
        for (let x = 0; x < w; x++) {
          const bit = x * bitDepth;
          raw[rowStart + 1 + (bit >> 3)] |= indices[y * w + x] << (8 - bitDepth - (bit & 7));
        }
      }
    }
    const ihdr = new Uint8Array(13); const iv = new DataView(ihdr.buffer);
    iv.setUint32(0, w); iv.setUint32(4, h); ihdr[8] = bitDepth; ihdr[9] = 3; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
    const plte = new Uint8Array(palette.length * 3);
    palette.forEach((p, i) => { plte[i * 3] = p[0]; plte[i * 3 + 1] = p[1]; plte[i * 3 + 2] = p[2]; });
    let trnsLen = palette.length;
    while (trnsLen > 0 && palette[trnsLen - 1][3] === 255) trnsLen--;
    const trns = new Uint8Array(trnsLen);
    for (let i = 0; i < trnsLen; i++) trns[i] = palette[i][3];
    const idat = await zlibDeflate(raw);
    const parts = [new Uint8Array([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]), pngChunk('IHDR', ihdr), pngChunk('PLTE', plte)];
    if (trnsLen > 0) parts.push(pngChunk('tRNS', trns));
    parts.push(pngChunk('IDAT', idat), pngChunk('IEND', new Uint8Array(0)));
    return new Blob(parts, { type: 'image/png' });
  }

  /* ---------- PDF writer (images embedded as JPEG) ---------- */
  const PAGE_SIZES = { a4: [595.28, 841.89], letter: [612, 792] };
  async function buildPdf(pages, opts) {
    // pages: [{ canvas }]  opts: { pageSize, orientation, margin, quality, background }
    const enc = new TextEncoder();
    const parts = []; let offset = 0; const offsets = [];
    const push = (x) => { const b = typeof x === 'string' ? enc.encode(x) : x; parts.push(b); offset += b.length; };
    push('%PDF-1.4\n'); push(new Uint8Array([0x25, 0xE2, 0xE3, 0xCF, 0xD3, 0x0A]));
    const n = pages.length;
    const ids = pages.map((_, i) => ({ img: 3 + i * 3, content: 4 + i * 3, page: 5 + i * 3 }));
    const addObj = (id, body) => { offsets[id] = offset; push(id + ' 0 obj\n'); push(body); push('\nendobj\n'); };
    addObj(1, '<< /Type /Catalog /Pages 2 0 R >>');
    addObj(2, '<< /Type /Pages /Kids [' + ids.map((x) => x.page + ' 0 R').join(' ') + '] /Count ' + n + ' >>');
    for (let i = 0; i < n; i++) {
      const c = pages[i].canvas;
      const jpg = await blobBytes(await encodeNative(c, 'image/jpeg', opts.quality));
      const iw = c.width, ih = c.height;
      let pw, ph;
      if (opts.pageSize === 'fit') { pw = iw * 0.75; ph = ih * 0.75; }
      else {
        const [a, b] = PAGE_SIZES[opts.pageSize] || PAGE_SIZES.a4;
        const landscape = opts.orientation === 'landscape' || (opts.orientation === 'auto' && iw > ih);
        pw = landscape ? b : a; ph = landscape ? a : b;
      }
      const m = opts.pageSize === 'fit' ? 0 : (opts.margin || 0);
      const scale = Math.min((pw - 2 * m) / iw, (ph - 2 * m) / ih);
      const dw = iw * scale, dh = ih * scale, dx = (pw - dw) / 2, dy = (ph - dh) / 2;
      const f = (v) => v.toFixed(2);
      offsets[ids[i].img] = offset;
      push(ids[i].img + ' 0 obj\n<< /Type /XObject /Subtype /Image /Width ' + iw + ' /Height ' + ih + ' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ' + jpg.length + ' >>\nstream\n');
      push(jpg); push('\nendstream\nendobj\n');
      const content = 'q ' + f(dw) + ' 0 0 ' + f(dh) + ' ' + f(dx) + ' ' + f(dy) + ' cm /Im' + i + ' Do Q';
      addObj(ids[i].content, '<< /Length ' + enc.encode(content).length + ' >>\nstream\n' + content + '\nendstream');
      addObj(ids[i].page, '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ' + f(pw) + ' ' + f(ph) + '] /Resources << /XObject << /Im' + i + ' ' + ids[i].img + ' 0 R >> >> /Contents ' + ids[i].content + ' 0 R >>');
    }
    const total = 3 + n * 3;
    const xref = offset;
    let x = 'xref\n0 ' + total + '\n0000000000 65535 f \n';
    for (let i = 1; i < total; i++) x += String(offsets[i]).padStart(10, '0') + ' 00000 n \n';
    push(x);
    push('trailer\n<< /Size ' + total + ' /Root 1 0 R >>\nstartxref\n' + xref + '\n%%EOF\n');
    return new Blob(parts, { type: 'application/pdf' });
  }

  /* ---------- ZIP writer (store, no compression — images are already compressed) ---------- */
  function buildZip(entries) {
    const enc = new TextEncoder();
    const parts = []; let offset = 0; const central = [];
    const d = new Date();
    const dosTime = ((d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1)) & 0xFFFF;
    const dosDate = (((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate()) & 0xFFFF;
    for (const e of entries) {
      const name = enc.encode(e.name), crc = crc32(e.bytes), size = e.bytes.length;
      const lh = new Uint8Array(30 + name.length); const v = new DataView(lh.buffer);
      v.setUint32(0, 0x04034b50, true); v.setUint16(4, 20, true); v.setUint16(6, 0x0800, true); v.setUint16(8, 0, true);
      v.setUint16(10, dosTime, true); v.setUint16(12, dosDate, true); v.setUint32(14, crc, true);
      v.setUint32(18, size, true); v.setUint32(22, size, true); v.setUint16(26, name.length, true); v.setUint16(28, 0, true);
      lh.set(name, 30);
      const ch = new Uint8Array(46 + name.length); const cv = new DataView(ch.buffer);
      cv.setUint32(0, 0x02014b50, true); cv.setUint16(4, 20, true); cv.setUint16(6, 20, true); cv.setUint16(8, 0x0800, true); cv.setUint16(10, 0, true);
      cv.setUint16(12, dosTime, true); cv.setUint16(14, dosDate, true); cv.setUint32(16, crc, true);
      cv.setUint32(20, size, true); cv.setUint32(24, size, true); cv.setUint16(28, name.length, true);
      cv.setUint32(42, offset, true); ch.set(name, 46);
      central.push(ch);
      parts.push(lh, e.bytes); offset += lh.length + size;
    }
    const cdStart = offset; let cdSize = 0;
    for (const c of central) { parts.push(c); cdSize += c.length; }
    const end = new Uint8Array(22); const ev = new DataView(end.buffer);
    ev.setUint32(0, 0x06054b50, true); ev.setUint16(8, entries.length, true); ev.setUint16(10, entries.length, true);
    ev.setUint32(12, cdSize, true); ev.setUint32(16, cdStart, true);
    parts.push(end);
    return new Blob(parts, { type: 'application/zip' });
  }

  /* ===========================================================
     UI
     =========================================================== */
  const state = {
    to: cfg.to || (cfg.mode === 'compress' ? cfg.format : 'webp'),
    quality: cfg.quality || (cfg.mode === 'compress' ? 70 : 85),
    colors: 256, dither: true,
    background: '#ffffff',
    icoSizes: [16, 32, 48],
    width: '', height: '', lockAspect: true,
    rotate: cfg.rotate || 0, flipH: !!cfg.flipH, flipV: !!cfg.flipV,
    pageSize: 'a4', orientation: 'auto', margin: 20, combine: true,
    results: [],
  };
  if (cfg.mode === 'compress' && cfg.format === 'png') state.quality = 100;
  if (cfg.mode === 'pdf') state.quality = 90;

  const NOTES = {
    ico: 'ICO bundles several sizes into one favicon file — transparency is preserved.',
    bmp: 'BMP is uncompressed: files will be much larger than PNG or JPG. Use it only when a program specifically needs BMP.',
  };

  /* Live settings: any control change re-processes every file already in the list. */
  let reprocessTimer = null;
  function scheduleReprocess(delay) {
    clearTimeout(reprocessTimer);
    reprocessTimer = setTimeout(reprocessAll, delay == null ? 220 : delay);
  }
  async function reprocessAll() {
    for (const r of state.results.slice()) {
      if (r.src || r.srcs) await processResult(r);
    }
  }
  function allSourceFiles() {
    const out = [];
    state.results.forEach((r) => { if (r.files) out.push(...r.files); else if (r.file) out.push(r.file); });
    return out;
  }

  function render() {
    root.innerHTML = '';
    root.appendChild(el('div', { class: 'dropzone', id: 'dropZone', tabindex: '0', role: 'button', 'aria-label': 'Upload images' }, [
      el('div', { class: 'dz-icon', html: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-2-2h-1.26a8 8 0 1 0-15.48 0H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2Z"/></svg>' }),
      el('div', { class: 'dz-title', text: cfg.dropTitle || 'Drop images here or click to upload' }),
      el('div', { class: 'dz-sub', text: cfg.dropSub || 'PNG, JPG, WebP, GIF, BMP, AVIF, SVG — processed entirely in your browser' }),
      el('input', { type: 'file', id: 'fileInput', accept: 'image/*,.svg,.avif,.ico,.bmp', multiple: '', hidden: '' }),
    ]));

    const controls = el('div', { class: 'controls' });
    const mode = cfg.mode;
    const showFormatPicker = mode === 'convert' || mode === 'resize' || mode === 'rotate' || mode === 'flip' || mode === 'grayscale';

    if (showFormatPicker) {
      const picker = el('div', { class: 'format-picker', role: 'group', 'aria-label': 'Output format' });
      OUTPUT_ORDER.forEach((k) => picker.appendChild(el('button', {
        type: 'button', class: 'format-btn' + (state.to === k ? ' active' : ''), 'data-format': k, text: FORMATS[k].label,
        onclick: () => { state.to = k; render(); scheduleReprocess(0); },
      })));
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Convert to' }), picker]));
    }

    if (mode === 'resize') {
      const wIn = el('input', { type: 'number', min: '1', placeholder: 'auto', value: state.width, class: 'num', 'aria-label': 'Width', oninput: (e) => { state.width = e.target.value; scheduleReprocess(350); } });
      const hIn = el('input', { type: 'number', min: '1', placeholder: 'auto', value: state.height, class: 'num', 'aria-label': 'Height', oninput: (e) => { state.height = e.target.value; scheduleReprocess(350); } });
      const lock = el('input', { type: 'checkbox', id: 'lockAspect', onchange: (e) => { state.lockAspect = e.target.checked; scheduleReprocess(0); } });
      lock.checked = state.lockAspect;
      controls.appendChild(el('div', { class: 'control-group' }, [
        el('label', { text: 'Size' }), wIn, el('span', { class: 'x', text: '×' }), hIn, el('span', { class: 'unit', text: 'px' }),
        el('label', { class: 'check', for: 'lockAspect' }, [lock, ' Keep aspect ratio']),
      ]));
      const presets = el('div', { class: 'preset-row' });
      [25, 50, 75].forEach((p) => presets.appendChild(el('button', { type: 'button', class: 'chip' + (state.percent === p ? ' active' : ''), text: p + '%', onclick: (ev) => { state.width = ''; state.height = ''; state.percent = p; wIn.value = ''; hIn.value = ''; presets.querySelectorAll('.chip').forEach((c) => c.classList.remove('active')); ev.currentTarget.classList.add('active'); scheduleReprocess(0); } })));
      presets.appendChild(el('span', { class: 'hint', text: 'Leave a field blank to scale it automatically.' }));
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Or scale' }), presets]));
      wIn.addEventListener('input', () => { state.percent = null; presets.querySelectorAll('.chip').forEach((c) => c.classList.remove('active')); });
      hIn.addEventListener('input', () => { state.percent = null; presets.querySelectorAll('.chip').forEach((c) => c.classList.remove('active')); });
    }

    if (mode === 'rotate' || mode === 'flip') {
      const group = el('div', { class: 'format-picker' });
      [0, 90, 180, 270].forEach((a) => group.appendChild(el('button', { type: 'button', class: 'format-btn' + (state.rotate === a ? ' active' : ''), text: a + '°', onclick: () => { state.rotate = a; render(); scheduleReprocess(0); } })));
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Rotate' }), group]));
      const fh = el('input', { type: 'checkbox', id: 'flipH', onchange: (e) => { state.flipH = e.target.checked; scheduleReprocess(0); } }); fh.checked = state.flipH;
      const fv = el('input', { type: 'checkbox', id: 'flipV', onchange: (e) => { state.flipV = e.target.checked; scheduleReprocess(0); } }); fv.checked = state.flipV;
      controls.appendChild(el('div', { class: 'control-group' }, [
        el('label', { text: 'Flip' }),
        el('label', { class: 'check', for: 'flipH' }, [fh, ' Horizontal']),
        el('label', { class: 'check', for: 'flipV' }, [fv, ' Vertical']),
      ]));
    }

    if (mode === 'pdf') {
      const sel = el('select', { class: 'select', onchange: (e) => { state.pageSize = e.target.value; render(); scheduleReprocess(0); } });
      [['a4', 'A4'], ['letter', 'US Letter'], ['fit', 'Fit to image']].forEach(([v, t]) => { const o = el('option', { value: v, text: t }); if (state.pageSize === v) o.selected = true; sel.appendChild(o); });
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Page' }), sel]));
      if (state.pageSize !== 'fit') {
        const orient = el('select', { class: 'select', onchange: (e) => { state.orientation = e.target.value; scheduleReprocess(0); } });
        [['auto', 'Auto orientation'], ['portrait', 'Portrait'], ['landscape', 'Landscape']].forEach(([v, t]) => { const o = el('option', { value: v, text: t }); if (state.orientation === v) o.selected = true; orient.appendChild(o); });
        const margin = el('input', { type: 'number', min: '0', max: '100', value: state.margin, class: 'num', 'aria-label': 'Margin', oninput: (e) => { state.margin = Number(e.target.value) || 0; scheduleReprocess(350); } });
        controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Layout' }), orient, el('span', { class: 'unit', text: 'margin' }), margin, el('span', { class: 'unit', text: 'pt' })]));
      }
      const combine = el('input', { type: 'checkbox', id: 'combine', onchange: (e) => { state.combine = e.target.checked; const files = allSourceFiles(); clearResults(); if (files.length) handleFiles(files); } }); combine.checked = state.combine;
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { class: 'check', for: 'combine' }, [combine, ' Combine all images into one PDF'])]));
    }

    // quality / colors
    const effectiveTarget = mode === 'compress' ? cfg.format : mode === 'pdf' ? 'jpg' : state.to;
    const isPngCompress = mode === 'compress' && cfg.format === 'png';
    if (isPngCompress) {
      const colors = el('input', { type: 'range', min: '2', max: '256', value: state.colors, oninput: (e) => { state.colors = Number(e.target.value); $('#colorsValue').textContent = state.colors + ' colors'; scheduleReprocess(300); } });
      const dither = el('input', { type: 'checkbox', id: 'dither', onchange: (e) => { state.dither = e.target.checked; scheduleReprocess(0); } }); dither.checked = state.dither;
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Palette' }), colors, el('span', { id: 'colorsValue', class: 'val', text: state.colors + ' colors' })]));
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { class: 'check', for: 'dither' }, [dither, ' Dithering (smoother gradients)'])]));
    } else if (effectiveTarget && FORMATS[effectiveTarget] && FORMATS[effectiveTarget].lossy) {
      const q = el('input', { type: 'range', min: '10', max: '100', value: state.quality, oninput: (e) => { state.quality = Number(e.target.value); $('#qualityValue').textContent = state.quality + '%'; scheduleReprocess(); } });
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Quality' }), q, el('span', { id: 'qualityValue', class: 'val', text: state.quality + '%' })]));
    }

    // background for formats without alpha
    if (effectiveTarget && FORMATS[effectiveTarget] && !FORMATS[effectiveTarget].alpha) {
      const bg = el('input', { type: 'color', value: state.background, 'aria-label': 'Background color', oninput: (e) => { state.background = e.target.value; scheduleReprocess(300); } });
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Transparent areas' }), bg, el('span', { class: 'hint', text: FORMATS[effectiveTarget].label + ' has no transparency — this color fills them.' })]));
    }

    // ico sizes
    if (effectiveTarget === 'ico') {
      const wrap = el('div', { class: 'preset-row' });
      [16, 32, 48, 64, 128, 256].forEach((s) => {
        const cb = el('input', { type: 'checkbox', id: 'ico' + s, onchange: (e) => { if (e.target.checked) state.icoSizes.push(s); else state.icoSizes = state.icoSizes.filter((x) => x !== s); state.icoSizes.sort((a, b) => a - b); scheduleReprocess(0); } });
        cb.checked = state.icoSizes.includes(s);
        wrap.appendChild(el('label', { class: 'check', for: 'ico' + s }, [cb, ' ' + s + '×' + s]));
      });
      controls.appendChild(el('div', { class: 'control-group' }, [el('label', { text: 'Icon sizes' }), wrap]));
    }

    if (mode !== 'base64') root.appendChild(controls);
    if (effectiveTarget && NOTES[effectiveTarget] && mode !== 'pdf') root.appendChild(el('div', { class: 'note', text: NOTES[effectiveTarget] }));
    if (cfg.note) root.appendChild(el('div', { class: 'note', text: cfg.note }));

    root.appendChild(el('div', { class: 'results-head', id: 'resultsHead', hidden: '' }, [
      el('span', { id: 'resultsSummary', class: 'summary' }),
      el('div', { class: 'actions' }, [
        el('button', { type: 'button', class: 'btn btn-secondary', id: 'clearBtn', text: 'Clear', onclick: clearResults }),
        el('button', { type: 'button', class: 'btn btn-primary', id: 'zipBtn', text: 'Download all (.zip)', onclick: downloadZip }),
      ]),
    ]));
    root.appendChild(el('div', { id: 'emptyState', class: 'empty', text: 'No files yet — drop an image above to get started.' }));
    root.appendChild(el('div', { id: 'resultsList', class: 'results' }));

    wireDropzone();
    if (state.results.length) state.results.forEach((r) => $('#resultsList').appendChild(r.row));
    refreshHead();
  }

  function wireDropzone() {
    const dz = $('#dropZone'), input = $('#fileInput');
    ['dragenter', 'dragover'].forEach((e) => dz.addEventListener(e, (ev) => { ev.preventDefault(); dz.classList.add('dragover'); }));
    ['dragleave', 'drop'].forEach((e) => dz.addEventListener(e, (ev) => { ev.preventDefault(); dz.classList.remove('dragover'); }));
    dz.addEventListener('drop', (ev) => handleFiles(ev.dataTransfer.files));
    dz.addEventListener('click', () => input.click());
    dz.addEventListener('keydown', (ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); input.click(); } });
    input.addEventListener('change', () => { handleFiles(input.files); input.value = ''; });
    document.addEventListener('paste', (ev) => {
      const items = ev.clipboardData && ev.clipboardData.files;
      if (items && items.length) handleFiles(items);
    });
  }

  function refreshHead() {
    const head = $('#resultsHead'), empty = $('#emptyState');
    const done = state.results.filter((r) => r.blob);
    head.hidden = state.results.length === 0;
    empty.hidden = state.results.length > 0;
    const zip = $('#zipBtn'); if (zip) zip.hidden = done.length < 2;
    if (done.length) {
      const inSize = done.reduce((a, r) => a + r.inSize, 0), outSize = done.reduce((a, r) => a + r.blob.size, 0);
      const pct = inSize ? Math.round((1 - outSize / inSize) * 100) : 0;
      $('#resultsSummary').textContent = done.length + ' file' + (done.length > 1 ? 's' : '') + ' · ' + humanSize(inSize) + ' → ' + humanSize(outSize) + (pct > 0 ? ' · saved ' + pct + '%' : '');
    } else $('#resultsSummary').textContent = '';
  }

  function releaseResult(r) {
    if (r.url) URL.revokeObjectURL(r.url);
    if (r.thumb) URL.revokeObjectURL(r.thumb);
    if (r.src && r.src.url) URL.revokeObjectURL(r.src.url);
    if (r.srcs) r.srcs.forEach((s) => s.url && URL.revokeObjectURL(s.url));
  }
  function removeResult(r) {
    releaseResult(r);
    state.results = state.results.filter((x) => x !== r);
    r.row.remove();
    refreshHead();
  }
  function clearResults() {
    state.results.forEach(releaseResult);
    state.results = [];
    $('#resultsList').innerHTML = '';
    refreshHead();
  }

  async function downloadZip() {
    const done = state.results.filter((r) => r.blob);
    const entries = [];
    for (const r of done) entries.push({ name: r.name, bytes: await blobBytes(r.blob) });
    const zip = buildZip(entries);
    const a = el('a', { href: URL.createObjectURL(zip), download: (cfg.zipName || 'pixelshrink') + '.zip' });
    document.body.appendChild(a); a.click(); a.remove();
  }

  function makeRow(label) {
    const row = el('div', { class: 'result-row pending' }, [
      el('div', { class: 'thumb' }),
      el('div', { class: 'result-info' }, [el('div', { class: 'result-name', text: label }), el('div', { class: 'result-status', text: 'Working…' })]),
    ]);
    return row;
  }
  function finishRow(r) {
    const pct = r.inSize ? Math.round((1 - r.blob.size / r.inSize) * 100) : 0;
    const badge = pct > 0 ? '<span class="pill pill-good">−' + pct + '%</span>' : pct < 0 ? '<span class="pill pill-bad">+' + Math.abs(pct) + '%</span>' : '';
    r.url = URL.createObjectURL(r.blob);
    r.row.className = 'result-row done';
    r.row.innerHTML = '';
    const thumb = el('div', { class: 'thumb' });
    if (r.thumb) thumb.appendChild(el('img', { src: r.thumb, alt: '' })); else thumb.appendChild(el('span', { class: 'thumb-ext', text: r.name.split('.').pop().toUpperCase() }));
    r.row.appendChild(thumb);
    r.row.appendChild(el('div', { class: 'result-info' }, [
      el('div', { class: 'result-name', text: r.name }),
      el('div', { class: 'result-size', html: (r.meta ? r.meta + ' · ' : '') + humanSize(r.inSize) + ' → <strong>' + humanSize(r.blob.size) + '</strong> ' + badge }),
    ]));
    r.row.appendChild(el('a', { class: 'btn btn-primary', href: r.url, download: r.name, text: 'Download' }));
    r.row.appendChild(el('button', { type: 'button', class: 'row-remove', title: 'Remove', 'aria-label': 'Remove ' + r.name, html: '&times;', onclick: () => removeResult(r) }));
  }
  function failRow(row, err) {
    row.className = 'result-row error';
    const status = row.querySelector('.result-status');
    if (status) status.textContent = err.message || 'Something went wrong';
    else {
      const name = row.querySelector('.result-name');
      row.innerHTML = '';
      row.appendChild(el('div', { class: 'result-info' }, [el('div', { class: 'result-name', text: name ? name.textContent : 'File' }), el('div', { class: 'result-status', text: err.message || 'Something went wrong' })]));
    }
  }
  function markUpdating(r) {
    if (!r.row.classList.contains('done')) return;
    r.row.classList.add('updating');
    const size = r.row.querySelector('.result-size');
    if (size) size.innerHTML = '<span class="updating-text">Updating…</span>';
  }

  const targetFormat = () => (cfg.mode === 'compress' ? cfg.format : cfg.mode === 'pdf' ? 'pdf' : state.to);

  async function processResult(r) {
    const gen = (r.gen = (r.gen || 0) + 1);
    markUpdating(r);
    try {
      let out;
      if (cfg.mode === 'pdf') {
        const pages = r.srcs.map((s) => ({ canvas: buildCanvas(s, { background: state.background }) }));
        const blob = await buildPdf(pages, { pageSize: state.pageSize, orientation: state.orientation, margin: state.margin, quality: state.quality / 100 });
        out = { blob, name: (r.files.length === 1 ? baseName(r.files[0].name) : 'images') + '.pdf', meta: pages.length + ' page' + (pages.length > 1 ? 's' : '') };
      } else {
        out = await processImage(r.file, r.src);
      }
      if (gen !== r.gen) return;            // a newer setting change superseded this run
      if (r.url) URL.revokeObjectURL(r.url);
      if (r.thumb) URL.revokeObjectURL(r.thumb);
      r.blob = out.blob; r.name = out.name; r.meta = out.meta;
      r.thumb = ['png', 'jpg', 'webp'].includes(targetFormat()) ? URL.createObjectURL(r.blob) : null;
      finishRow(r);
    } catch (err) {
      if (gen === r.gen) failRow(r.row, err);
    }
    refreshHead();
  }

  function outputOptions(src) {
    const o = { rotate: state.rotate, flipH: state.flipH, flipV: state.flipV, grayscale: cfg.mode === 'grayscale' };
    if (cfg.mode === 'resize') {
      let w = parseInt(state.width, 10), h = parseInt(state.height, 10);
      if (state.percent) { w = Math.max(1, Math.round(src.width * state.percent / 100)); h = Math.max(1, Math.round(src.height * state.percent / 100)); }
      else if (w && h && state.lockAspect) { const s = Math.min(w / src.width, h / src.height); w = Math.max(1, Math.round(src.width * s)); h = Math.max(1, Math.round(src.height * s)); }
      else if (w && !h) h = Math.max(1, Math.round(src.height * w / src.width));
      else if (h && !w) w = Math.max(1, Math.round(src.width * h / src.height));
      else if (!w && !h) { w = src.width; h = src.height; }
      o.width = w; o.height = h;
    }
    return o;
  }

  async function processImage(file, src) {
    const mode = cfg.mode;
    const target = mode === 'compress' ? cfg.format : state.to;
    const fmt = FORMATS[target];
    const opts = outputOptions(src);
    if (!fmt.alpha) opts.background = state.background;
    let blob, meta = '';
    if (target === 'ico') {
      const sizes = state.icoSizes.length ? state.icoSizes : [16, 32, 48];
      blob = await encodeIco(src, sizes);
      meta = sizes.map((s) => s + 'px').join(', ');
    } else {
      const canvas = buildCanvas(src, opts);
      meta = canvas.width + '×' + canvas.height;
      if (mode === 'compress' && target === 'png') blob = await encodeIndexedPng(canvas, state.colors, state.dither);
      else if (target === 'bmp') blob = encodeBmp(canvas);
      else blob = await encodeNative(canvas, fmt.mime, fmt.lossy ? state.quality / 100 : undefined);
    }
    return { blob, name: baseName(file.name) + '.' + fmt.ext, meta };
  }

  async function handleFiles(fileList) {
    const files = Array.from(fileList).filter((f) => f.type.startsWith('image/') || /\.(png|jpe?g|webp|gif|bmp|avif|svg|ico)$/i.test(f.name));
    if (!files.length) return;
    refreshHead();

    if (cfg.mode === 'base64') { for (const f of files) await doBase64(f); return; }

    if (cfg.mode === 'pdf' && state.combine) {
      const r = { row: makeRow(files.length + ' image' + (files.length > 1 ? 's' : '') + ' → PDF'), inSize: files.reduce((a, f) => a + f.size, 0), files: files };
      state.results.push(r); $('#resultsList').prepend(r.row); refreshHead();
      try {
        r.srcs = [];
        for (const f of files) r.srcs.push(await loadImage(f));
        await processResult(r);
      } catch (err) { failRow(r.row, err); refreshHead(); }
      return;
    }

    for (const file of files) {
      const r = { row: makeRow(file.name), inSize: file.size, file: file, files: [file] };
      state.results.push(r); $('#resultsList').prepend(r.row); refreshHead();
      try {
        const src = await loadImage(file);
        if (cfg.mode === 'pdf') r.srcs = [src]; else r.src = src;
        await processResult(r);
      } catch (err) { failRow(r.row, err); refreshHead(); }
    }
  }

  async function doBase64(file) {
    const r = { row: makeRow(file.name), inSize: file.size };
    state.results.push(r); $('#resultsList').prepend(r.row); refreshHead();
    try {
      const dataUrl = await new Promise((res, rej) => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.onerror = () => rej(new Error('Could not read file')); fr.readAsDataURL(file); });
      r.row.className = 'result-row done b64';
      r.row.innerHTML = '';
      const ta = el('textarea', { class: 'b64', readonly: '', rows: '4' }); ta.value = dataUrl;
      const copy = (text, btn) => () => { navigator.clipboard.writeText(text).then(() => { const t = btn.textContent; btn.textContent = 'Copied!'; setTimeout(() => (btn.textContent = t), 1200); }); };
      const b1 = el('button', { type: 'button', class: 'btn btn-primary', text: 'Copy data URI' }); b1.addEventListener('click', copy(dataUrl, b1));
      const b2 = el('button', { type: 'button', class: 'btn btn-secondary', text: 'Copy <img> tag' }); b2.addEventListener('click', copy('<img src="' + dataUrl + '" alt="">', b2));
      const b3 = el('button', { type: 'button', class: 'btn btn-secondary', text: 'Copy CSS' }); b3.addEventListener('click', copy('background-image: url("' + dataUrl + '");', b3));
      const b4 = el('button', { type: 'button', class: 'btn btn-secondary', text: 'Copy raw Base64' }); b4.addEventListener('click', copy(dataUrl.split(',')[1], b4));
      r.row.appendChild(el('div', { class: 'result-info wide' }, [
        el('div', { class: 'result-name', text: file.name }),
        el('div', { class: 'result-size', text: humanSize(file.size) + ' → ' + humanSize(dataUrl.length) + ' as text (' + Math.round((dataUrl.length / file.size - 1) * 100) + '% larger, as Base64 always is)' }),
        ta,
        el('div', { class: 'btn-row' }, [b1, b2, b3, b4]),
      ]));
      r.blob = new Blob([dataUrl], { type: 'text/plain' }); r.name = baseName(file.name) + '.base64.txt';
    } catch (err) { failRow(r.row, err); }
    refreshHead();
  }

  render();
})();
