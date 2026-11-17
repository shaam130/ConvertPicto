---
title: How I Wrote a PNG Compressor in Plain JavaScript
h1: Writing a real PNG compressor in vanilla JavaScript (no WASM, no libraries)
description: Browsers can only encode PNG, JPEG and WebP. Here is how a real palette-based PNG compressor works in plain JavaScript: median cut, dithering, CRC32, and four traps that cost hours.
excerpt: Median-cut quantization, Floyd–Steinberg dithering, hand-built PNG chunks, and the four browser traps that cost me an evening each.
date: 2026-10-07
keyword: png compressor javascript
tools: compress-png, svg-to-png, png-to-jpg
---

Every online image converter I tried had the same shape: drag your file in, it uploads to a server somewhere, you get a download link back.

That's fine for a meme. It's less fine for a scan of your passport, and it's the most common thing people convert. So I wanted to know how far a browser could get on its own.

Quite far, as it turns out — but not without a few traps that cost me an evening each. Here are the four that were worth writing down.

:::note Update, November 2026: the PNG compressor described here is still plain JavaScript with no libraries. Since writing this I added one third-party piece: the open-source libwebp encoder, compiled to WebAssembly, which the site loads only for lossless WebP. Chrome's built-in WebP encoder turned out to produce files larger than PNG for graphics, and libwebp fixed that. The measurements are in [WebP vs PNG, measured](/blog/webp-vs-png).:::

## The constraint

Browsers decode plenty of formats: PNG, JPEG, WebP, GIF, BMP, AVIF, SVG, ICO.

They **encode** exactly three: PNG, JPEG, WebP. That's the whole list `canvas.toBlob()` will give you.

Everything else — BMP, ICO, PDF, and crucially a *properly compressed* PNG — you write yourself, byte by byte.

## Trap 1: `toBlob` lies to you

This is the one I'd most like to have known first.

`canvas.toBlob()` takes a MIME type. Pass it one the browser can't encode, and it does not throw, does not return null, and does not warn. It silently gives you a **PNG** with a success callback.

```js
canvas.toBlob((blob) => {
  console.log(blob.type); // "image/png" — but I asked for image/avif
}, 'image/avif', 0.8);
```

So you ship a converter that appears to work perfectly, and your users get files named `.avif` that are actually PNGs. Nothing errors. You find out from a bug report.

The fix is two lines:

```js
function encodeNative(canvas, mime, quality) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob && blob.type === mime) resolve(blob);
      else reject(new Error("Your browser can't export " + mime));
    }, mime, quality);
  });
}
```

Check the type you got against the type you asked for. Never trust the callback firing as proof of anything.

## Trap 2: "compressing" a PNG usually does nothing

Here's the thing that surprised me most. Draw a PNG to a canvas, call `toBlob('image/png')`, and you get a file that's often *larger* than the original.

PNG has no quality slider. It's lossless. So there's no knob for `toBlob` to turn, and re-encoding just re-does the same lossless compression, usually worse than whatever tool made the original.

Real PNG compression works differently. A standard PNG stores 24-bit colour — about 16 million possible values per pixel. Almost no real image uses that many. A logo might use twelve. A screenshot might use two hundred.

So you build an optimised palette of at most 256 colours and store a one-byte *index* per pixel instead of three or four bytes of colour. That's where the savings live, and `toBlob` will never do it for you.

Which means writing the PNG yourself.

## Writing a PNG by hand

A PNG is an 8-byte signature followed by chunks. Each chunk is: length, 4-byte type, data, CRC32.

```js
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
```

Note the CRC covers the type **and** the data, but not the length field. Get that wrong and every decoder rejects the file with no useful message.

CRC32 itself is a table and a loop:

```js
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();
```

For an indexed PNG you need four chunks: `IHDR` (dimensions, bit depth, colour type 3 for palette), `PLTE` (the palette), `tRNS` (per-palette-entry alpha, only if anything is transparent), and `IDAT` (the pixel data).

One detail that's easy to miss: every scanline in the raw data is prefixed with a filter byte. Zero means "no filter". Forget it and your image comes out sheared diagonally — which is at least a memorable way to find the bug.

Bit depth is worth packing properly too. Two colours fit in 1 bit per pixel, four in 2 bits, sixteen in 4. A two-colour image at 8 bits per pixel wastes 87% of its bytes.

## Trap 3: `deflate` vs `deflate-raw`

`IDAT` data is zlib-compressed, and browsers have that built in now via `CompressionStream`:

```js
async function zlibDeflate(bytes) {
  const cs = new CompressionStream('deflate');
  const writer = cs.writable.getWriter();
  writer.write(bytes);
  writer.close();
  return new Uint8Array(await new Response(cs.readable).arrayBuffer());
}
```

The trap is the argument. `CompressionStream` accepts `'deflate'`, `'deflate-raw'` and `'gzip'`, and the naming is genuinely misleading:

- `'deflate'` produces **zlib** format — RFC 1950, a 2-byte header plus an Adler-32 checksum
- `'deflate-raw'` produces **raw deflate** — RFC 1951, no header, no checksum

PNG's `IDAT` requires the zlib wrapper, so you want `'deflate'`. If you reach for `'deflate-raw'` because "raw deflate" sounds like what a binary format wants, you get a file that is byte-for-byte plausible and refuses to open anywhere.

## The quantizer: median cut and Floyd–Steinberg

Two classic algorithms, both about thirty lines.

**Median cut** builds the palette. Put every pixel in one box. Repeatedly take the box with the widest spread, find which channel it spreads on most, sort by that channel, split at the median. Stop at your colour count. Average each box to get its palette entry.

It's better than it sounds because it spends palette entries where the image actually has variation, rather than spreading them evenly across a colour space the image never visits.

**Floyd–Steinberg dithering** handles the error. When a pixel's true colour isn't in the palette, you pick the nearest and you're left with a difference. Throw it away and smooth gradients turn into visible bands. Instead, push that error onto the neighbours that haven't been processed yet:

```js
errCur[e + 3]  += er * 7 / 16;   // pixel to the right
errNext[e - 3] += er * 3 / 16;   // below-left
errNext[e]     += er * 5 / 16;   // directly below
errNext[e + 3] += er * 1 / 16;   // below-right
```

Those four fractions are from 1976 and they still work. The error gets scattered into a fine pattern your eye averages back out, and banding disappears.

## Does it actually work?

Numbers from the test suite, on real files:

| Input | Before | After | Saving | Palette |
|---|---|---|---|---|
| Photograph | 308,526 B | 71,411 B | **77%** | 227 colours |
| Flat graphic | 2,849 B | 2,161 B | **24%** | 59 colours |

The graphic came out with a mean per-pixel difference of **0.00** — mathematically identical output, 24% smaller. The photograph averaged 8.96 per channel, which is invisible at normal viewing size but is a real loss, and worth being honest about: palette quantization is lossy on photographs. Photos should generally be WebP or JPEG anyway.

## Trap 4: SVGs are 300×150

Draw an SVG to a canvas and you may get a 300×150 image regardless of its `viewBox`. That's the CSS default replaced-element size, and it applies whenever the SVG has no explicit `width` and `height`.

The fix is to parse the `viewBox`, strip any existing dimensions, and inject real ones before rasterising:

```js
const vb = /viewBox\s*=\s*["']\s*([\d.\-]+)[\s,]+([\d.\-]+)[\s,]+([\d.\-]+)[\s,]+([\d.\-]+)/i.exec(tag);
let w = 1024, h = 1024;
if (vb) {
  const vw = parseFloat(vb[3]), vh = parseFloat(vb[4]);
  if (vw > 0 && vh > 0) { w = 1024; h = Math.round(1024 * vh / vw); }
}
```

## Testing binary output

Unit-testing "did the conversion work" is harder than it looks, because a file can be the right size, the right type, and still be wrong.

What worked: drive the real pages in headless Chromium with Playwright, then verify the **bytes** in Python. Pillow checks dimensions, colour mode and how many palette entries were actually used. `pypdf` checks page counts and sizes. `zipfile` verifies archive integrity. Rotation and flipping get compared pixel-wise against Pillow's own implementations.

That combination caught the SVG bug, the `toBlob` fallback, and a filter-byte mistake that produced a file every viewer opened happily at the wrong dimensions.

## What a browser still can't do

Worth stating plainly, because "it all runs client-side" can sound like a claim that it does everything:

- **No HEIC, RAW, PSD or TIFF decoding.** Browsers can't, and shipping a WASM decoder for each would outweigh the entire project. If you need those, a server is the right answer.
- **Big files depend on the device.** A 100-megapixel image on an old phone is slow where a server would be instant.
- **AVIF encoding** only exists where the browser supports it — which is exactly why trap 1 matters.

What you get in exchange: nothing is uploaded, there's no queue, there's no file size limit set by someone's bandwidth bill, and the page keeps working with the network switched off.

## Code

The site's own code is MIT licensed, with one JavaScript file for the engine and one Python script that generates the site. The only bundled third-party code is the libwebp WebAssembly encoder, shipped with its Apache 2.0 licence: **[github.com/shaam130/ConvertPicto](https://github.com/shaam130/ConvertPicto)**

The running version is at [convertpicto.com](https://convertpicto.com) if you want to try breaking it. I'd like to hear about the files it fails on.

*A version of this article also appears on [DEV Community](https://dev.to/ihtisham130/writing-a-real-png-compressor-in-vanilla-javascript-no-wasm-no-libraries-2amn).*
