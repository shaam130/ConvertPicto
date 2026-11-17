---
title: Resize or Compress First? What Saves More File Size
h1: Resize or compress first? Measuring what actually shrinks an image
description: Resizing to 50% cut photo files to about 16% of the original. Compressing at full size only got to 29% to 53%. Measured on five photos with real tools.
excerpt: Image size scales with pixel count, so resizing beats lowering quality. Here are the measured numbers, and the order that works best.
date: 2026-10-23
keyword: resize or compress image first
tools: resize-image, compress-jpg
---

When an image is too big, there are two levers: change the pixel dimensions, or lower the quality. People reach for the quality slider first. The numbers say that is usually the weaker lever.

## How we tested

Five photographs were saved as high-quality JPEGs (quality 95) to stand in for camera or download originals, with sizes from 0.14 to 0.87 megapixels. Each went through ConvertPicto's resize tool at 75%, 50% and 25%, and through the JPG compressor at 85%, 70% and 60%. We also ran each resized file through the compressor at 70% to see what doing both gives. Everything ran in headless Chromium on the real pages.

## The results

Every figure is the average size as a percentage of the original JPEG.

| What we did | Average size vs original |
|---|---|
| Compress to 85%, full size | 53% |
| Compress to 70%, full size | 35% |
| Compress to 60%, full size | 28% |
| Resize to 75% of width | 30% |
| Resize to 50% of width | 16% |
| Resize to 25% of width | 6% |
| Resize to 75%, then compress to 70% | 23% |
| Resize to 50%, then compress to 70% | 12% |
| Resize to 25%, then compress to 70% | 4% |

The resize tool saved its output at its default 85% quality, so the fair comparison for the resize rows is the first row. At the same quality setting, shrinking the width to 75% gave **30%** of the original size, against **53%** from compression alone.

## Why resizing wins

Image data grows with the number of pixels, and pixels grow with the *square* of the width. Halving the width leaves a quarter of the pixels. That is why 50% width landed near 16% of the file size, while dropping the quality slider from 85% to 60% only reached 28%.

One photo, in kilobytes, to make it concrete. This is the largest of our five, 1000 x 872 pixels:

| Version | Size |
|---|---|
| Original JPEG (quality 95) | 395 KB |
| Compressed to 85% | 187 KB |
| Compressed to 60% | 89 KB |
| Resized to 50% (500 x 436) | 52 KB |
| Resized to 50%, then compressed to 70% | 38 KB |

The last row is about **10 times smaller** than the original. The 60%-quality version at full size, which also looks softer, is still 2.3 times larger than that.

## What this looks like in practice

The pattern repeated across all five photos, not just the largest one. Whatever the starting size, resizing to 75% of the width always beat compressing to 85%, and resizing to half the width always beat compressing all the way down to 60%. The bigger the starting image, the bigger the absolute saving, which is why this matters most for phone and camera photos, often 3000 pixels wide or more, that end up displayed in a column a few hundred pixels across. Our test images were small (0.14 to 0.87 megapixels), so a modern 12-megapixel phone photo will show an even larger gap.

There is also a quality argument for resizing. Lowering the quality slider adds compression artefacts such as blocky skies and ringing around edges. Resizing keeps every remaining pixel at the same quality, so the picture is smaller but not dirtier. Combining the two, a resize to half and a compression to 70%, is a good default for blog and web images.

## A short checklist before you export

1. Decide where the image will appear and how wide it will be shown.
2. Resize to that width, or twice that width if the audience is on high-density screens.
3. Compress the resized copy to about 70% to 85% quality and look at it at 100% zoom.
4. Keep the untouched original in a separate folder.

## The catch

Resizing throws away detail permanently. It is only the right lever when you know how large the image will actually be shown. A few rules that work:

1. **Find the display size.** A blog column might show an image 800 pixels wide. A phone screen is rarely wider than 1200 physical pixels. Resize to about that, or at most twice the CSS width for sharp high-DPI screens.
2. **Resize first, compress second.** Compressing before resizing wastes effort, because the extra detail is discarded anyway.
3. **Do not resize images you will print or crop later.** Keep the full-size original and make smaller copies.
4. **Do not enlarge.** Upscaling cannot invent detail and increases the file.

If you only need a smaller file and the dimensions are already right, compression alone is the correct tool. Our guide on [reducing image file size without losing quality](/blog/reduce-image-file-size) covers that order of operations. For the quality side of the story, see our [JPG vs WebP quality measurements](/blog/jpg-vs-webp-quality-settings).

:::tool resize-image|Resize an image:::
:::tool compress-jpg|Compress a JPG:::

:::note Caveat: five small photographs is a small test. The direction of the result, that resizing beats quality reduction, follows from how pixels scale, but the exact percentages will differ on your images.:::
