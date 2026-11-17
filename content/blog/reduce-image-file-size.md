---
title: How to Reduce Image File Size Without Losing Quality
h1: How to reduce image file size without losing quality
description: Practical, ordered steps to shrink photos and make images smaller — resize first, choose the right format, then compress. With real numbers, sensible quality settings, and the mistakes that waste the most bytes.
excerpt: Do these three things in the right order and a 4 MB photo becomes 80 KB with no visible difference. The order matters more than the tools.
date: 2026-09-09
keyword: reduce image file size without losing quality
tools: compress-jpg, compress-png, resize-image, png-to-webp
---

Whether you want to shrink a photo for email, a website or an upload form, the method is the same. "Without losing quality" is doing a lot of work in that phrase, so let's be precise about it up front: you can absolutely make images dramatically smaller with no *visible* difference. What you can't do is make them smaller with no *mathematical* difference — unless the file was badly saved to begin with, which, to be fair, it often was.

The good news is that most oversized images are oversized for a boring reason that has nothing to do with compression settings. Fix that first and the rest is easy.

:::note **The order that matters.** 1. Resize to the dimensions you actually need. 2. Pick the right format. 3. Compress. Doing these in the wrong order wastes most of the potential saving.:::

## Step 1: resize — this is where the real savings are

A photo from a modern phone is around 4000×3000 pixels. If you display it in a 800-pixel-wide column on a web page, the browser downloads all twelve million pixels and then throws away 96% of them.

File size scales with *area*, not width. Halving the width and height quarters the pixel count. Going from 4000px wide to 1000px wide is a 16× reduction before you've compressed anything at all.

Practical targets:

| Use | Sensible width |
|---|---|
| Full-width hero image | 1920–2400 px |
| Content image in an article | 1200–1600 px |
| Thumbnail or card image | 400–600 px |
| Avatar or icon | 200–400 px |
| Email attachment | 1200–1600 px |

Those already include a 2× allowance for high-DPI screens, which is why they look larger than the display size. If an image is shown at 600px wide on your page, exporting it at 1200px covers retina displays and stops there.

This single step routinely takes a 4 MB photo to under 400 KB. Every other technique on this page is fighting for the remaining crumbs by comparison.

:::tool resize-image|Resize an image:::

## Step 2: choose the format that suits the content

Different formats are good at different kinds of image, and using the wrong one can cost you a factor of five.

**Photographs** — continuous tones, thousands of colours, no sharp edges — want a lossy format. Use **WebP**, or **JPG** if the file needs to open in old software. A photograph saved as PNG will typically be five to ten times larger for no benefit whatsoever. This is the single most common format mistake.

**Graphics, logos, screenshots, anything with text or flat colour** want either **PNG** or lossless **WebP**. Save these as JPG and you get visible grey fuzz around every letter and edge — JPG's compression is designed for photos and actively damages sharp boundaries.

If you're unsure which camp an image is in, ask whether it came from a camera. If yes, it's a photo. If it came from software, it's a graphic.

## Step 3: compress properly

Now, and only now, does the quality slider matter.

### For JPG and WebP: the quality setting

Both use a 0–100 quality scale, and the relationship between that number and file size is steep and non-linear. Dropping from 100 to 85 typically halves the file with essentially no visible change. Dropping from 85 to 75 saves another 25% and is still invisible on most photos. Below about 60 you start seeing blockiness in smooth areas like skies.

Practical settings:

- **85–90** — photography portfolios, product shots, anything where detail matters
- **75–85** — the default for most web images; this is the sweet spot
- **60–75** — background images, thumbnails, anything displayed small
- **Below 60** — only when you have a hard size limit to hit

WebP at a given quality number is roughly comparable to JPG at the same number, but produces a file 25–35% smaller.

:::tool compress-jpg|Compress a JPG:::

### For PNG: reduce the palette, not the "quality"

PNG has no quality slider, which is why people believe PNGs can't be compressed. They can — the technique is just different.

A standard PNG stores 24-bit colour: about 16 million possible values per pixel. Almost no graphic actually uses that many. A logo might use twelve colours. A screenshot might use two hundred. By building an optimised palette of up to 256 colours and storing an index per pixel instead of a full colour, the file typically shrinks by 50–80%.

For graphics, screenshots and illustrations, the result is visually identical — you genuinely cannot tell. For photographs with smooth gradients, palette reduction can produce visible banding, though dithering (scattering the available colours in a fine pattern) hides most of it. If a PNG photo still looks banded after dithering, that's your signal that it should have been a WebP or JPG in the first place.

:::tool compress-png|Compress a PNG:::

## A worked example

A 12-megapixel phone photo destined for a blog post:

| Step | Result |
|---|---|
| Original JPG from phone, 4032×3024 | 4.2 MB |
| Resized to 1600px wide | 780 KB |
| Saved as JPG quality 82 | 310 KB |
| Saved as WebP quality 82 instead | 195 KB |

That's a 95% reduction, and side by side on a screen you would not be able to tell which is which. Notice that the resize did the heavy lifting: 82% of the total saving came from step one.

## Mistakes that cost the most

**Re-saving a JPG repeatedly.** JPG is lossy, so every save discards a little more. Edit from the original if you have it; if you're compressing a JPG that's already been compressed, expect diminishing returns and more artefacts.

**Compressing before resizing.** If you carefully compress a 4000px image and then scale it down, you've thrown away the work — the resize discards most of those pixels anyway. Resize first, compress second.

**Uploading straight from the camera.** Phone cameras save at maximum quality and full resolution by design. Nothing on the web needs that.

**Using PNG for photographs.** Worth repeating because it's so common and so expensive.

**Ignoring the dimensions in your HTML.** An image tag with no `width` and `height` causes layout shift, and a CSS rule that scales a huge image down doesn't reduce what gets downloaded. The browser fetches the full file either way.

**Forgetting that transparency has a cost.** If an image doesn't need a transparent background, don't use a format that carries one. Flattening a PNG onto a solid colour and saving as JPG or WebP is often a large saving.

## When you shouldn't compress

Some images should stay large, and it's worth knowing which:

- **Anything going to print.** Print needs roughly 300 DPI, so a photo printed at A4 wants around 3500×2500 pixels. Web-sized images look terrible on paper.
- **Master copies.** Keep your originals. Compression is one-way, and you'll want the original when you need a different crop or size later.
- **Images you'll edit again.** Each lossy round-trip degrades quality. Edit from the master, export a compressed copy.
- **Archival or legal material.** If a scan is evidence of something, don't throw pixels away.

## Quick checklist

1. Is it a photo or a graphic? That decides the format.
2. What size is it actually displayed at? Resize to roughly double that.
3. Photo → WebP or JPG at 80–85. Graphic → PNG with palette compression, or lossless WebP.
4. Compare before and after at 100% zoom, not at thumbnail size.
5. Keep the original somewhere.

Do those five things and you'll get 90%+ savings on almost any image, with nothing anyone could see. The tools matter far less than the order you use them in.
