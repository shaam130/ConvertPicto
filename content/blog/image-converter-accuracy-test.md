---
title: We Checked All 28 Image Conversions Pixel by Pixel
h1: We checked all 28 image conversions pixel by pixel
description: Every ConvertPicto conversion run in a real browser and compared with a reference decoder: which are bit-identical, which are lossy, and the one quirk to know about.
excerpt: 28 conversions, each run in headless Chromium and compared against an independent decoder. What is identical, what is lossy, and why.
date: 2026-10-23
keyword: image converter accuracy test
tools: png-to-jpg, webp-to-png, svg-to-png, png-to-ico
---

A converter that "works" can still be wrong: the right file type with shifted colours, a lost transparent edge, an icon in the wrong size. So we test ConvertPicto the hard way. Every one of its 28 conversions is run in a real browser, and the output is compared to the source using a separate image library.

This page shows the results, so you know what each conversion actually guarantees.

## How we tested

- **One test file per source format** (PNG, JPG, WebP, GIF, BMP, AVIF, ICO and SVG). They are synthetic images built to be hard cases: smooth gradients, hard edges and transparent regions, rather than ordinary photographs.
- **Each conversion page** was loaded in headless Chromium, given the file, and the downloaded output was read back.
- **The reference** was Pillow's own decode of the source file. We compared dimensions, file type and per-pixel differences. For targets that cannot hold transparency (JPG and BMP), both images were flattened onto white first.

## The headline results

- **All 28 outputs had the correct file type** (and for ICO, the correct frame sizes).
- **7 conversions were bit-for-bit identical** to the reference, with a mean difference of exactly 0.00: png-to-bmp, jpg-to-png, jpg-to-bmp, gif-to-png, gif-to-bmp, bmp-to-png, avif-to-png. Lossless to lossless is exactly what it sounds like.
- **Lossy targets (JPG and WebP) moved each channel by 1.4 to 3.9 levels on average** (out of 255), with PSNR between 25.8 and 39.9 dB. That is expected: JPG and WebP discard detail, and these test images are deliberately harsh on lossy codecs.
- **SVG sources rendered at 1024 pixels wide** when the file has no explicit size, keeping the aspect ratio. Without that step browsers use 300 x 150. We explain why in [our write-up on building the PNG encoder](/blog/png-compressor-vanilla-javascript).

## All 28 conversions

| Conversion | Output size (bytes) | Correct file type | Result |
|---|---|---|---|
| png-to-jpg | 30,671 | Yes | PSNR 33.6 dB |
| png-to-webp | 25,518 | Yes | PSNR 25.8 dB |
| png-to-bmp | 806,454 | Yes | Identical |
| png-to-ico | 5,810 | Yes | Frames: 16x16, 32x32, 48x48 |
| jpg-to-png | 419,602 | Yes | Identical |
| jpg-to-webp | 26,820 | Yes | PSNR 39.9 dB |
| jpg-to-bmp | 806,454 | Yes | Identical |
| jpg-to-ico | 5,957 | Yes | Frames: 16x16, 32x32, 48x48 |
| webp-to-png | 410,583 | Yes | PSNR 27.9 dB |
| webp-to-jpg | 31,005 | Yes | PSNR 37.7 dB |
| webp-to-bmp | 806,454 | Yes | PSNR 67.6 dB |
| webp-to-ico | 5,992 | Yes | Frames: 16x16, 32x32, 48x48 |
| gif-to-png | 126,488 | Yes | Identical |
| gif-to-jpg | 36,275 | Yes | PSNR 30.2 dB |
| gif-to-webp | 32,152 | Yes | PSNR 32.0 dB |
| gif-to-bmp | 806,454 | Yes | Identical |
| bmp-to-png | 384,368 | Yes | Identical |
| bmp-to-jpg | 31,559 | Yes | PSNR 33.6 dB |
| bmp-to-webp | 26,270 | Yes | PSNR 35.1 dB |
| bmp-to-ico | 5,845 | Yes | Frames: 16x16, 32x32, 48x48 |
| avif-to-png | 406,981 | Yes | Identical |
| avif-to-jpg | 31,506 | Yes | PSNR 38.5 dB |
| avif-to-webp | 20,560 | Yes | PSNR 39.7 dB |
| svg-to-png | 30,369 | Yes | Rendered 1024 x 512 |
| svg-to-jpg | 15,398 | Yes | Rendered 1024 x 512 |
| svg-to-webp | 7,800 | Yes | Rendered 1024 x 512 |
| svg-to-ico | 1,851 | Yes | Icon frames |
| ico-to-png | 7,149 | Yes | PSNR 67.9 dB |

## The one quirk: invisible pixels

WebP to PNG showed a small mean difference, and it is worth explaining. We checked where it came from: across every pixel that is actually visible, the mean difference was 0.02 levels out of 255 (the largest single difference was 2), and the transparency channel matched exactly. The rest comes from colours stored *underneath* fully transparent pixels. Browsers keep canvas pixels in premultiplied form, so the colour data hidden under a 100% transparent pixel is not preserved. You cannot see those pixels, and they do not affect how the image displays, but a byte-for-byte file comparison will show them as different.

## What this means for you

- **Converting between lossless formats** (PNG, BMP, and lossless sources like GIF) does not change visible pixels.
- **Converting to JPG or WebP** is lossy by design. Use the quality slider, and see our [measurements of what each quality level costs](/blog/jpg-vs-webp-quality-settings).
- **JPG and BMP have no transparency.** Transparent areas are filled with a colour you choose, white by default.
- **Everything runs locally.** None of these test files, or yours, are ever uploaded.

The site is open source, so the test suite that does this is in the [GitHub repository](https://github.com/shaam130/ConvertPicto) if you want to run it yourself.

:::tool png-to-jpg|PNG to JPG:::
:::tool webp-to-png|WebP to PNG:::
:::tool svg-to-png|SVG to PNG:::
:::tool png-to-ico|PNG to ICO:::

:::note Limits of this test: one file per source format, and synthetic rather than photographic. It checks that the conversions are correct, not how they compare to other converters.:::
