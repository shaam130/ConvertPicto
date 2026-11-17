---
title: PNG vs JPG vs WebP: What We Measured on 5 Image Types
h1: PNG vs JPG vs WebP: what we measured on photos, screenshots, text and charts
description: Which format is smallest for photos, screenshots, text pages and charts? We ran each through PNG compression, JPG and WebP and measured size and quality.
excerpt: There is no best format, only a best format for each kind of image. Measured sizes and quality scores for photos, screenshots, text and charts.
date: 2026-10-23
keyword: png vs jpg vs webp
tools: compress-png, png-to-webp, png-to-jpg, webp-to-png
---

Format advice usually sounds like "use JPG for photos and PNG for everything else". That is a decent rule of thumb, and it hides some surprising results. So we measured it.

We took five kinds of image, saved each as a lossless PNG, and ran every one through ConvertPicto's PNG compressor, its PNG to JPG converter and its PNG to WebP converter. Then we scored each output against the original with SSIM (1.000 means identical).

## How we tested

- **Photos:** five freely licensed sample photographs, 0.14 to 0.87 megapixels.
- **Screenshots:** two real 1440 x 900 screenshots of ConvertPicto itself (the homepage and a tool page).
- **Text-heavy page:** a 1100 x 1500 screenshot of a blog article.
- **Chart:** a 1200 x 700 bar chart exported from a plotting library.
- **Settings:** the PNG compressor at its defaults (256 colours, dithering on), JPG and WebP both at 85% quality. The tools ran in headless Chromium.

## The results

Each cell shows the file size, with the SSIM score in brackets. The PNG column is the original lossless file. Remember that the "compressed PNG" here is *palette* PNG: it reduces the image to at most 256 colours, which is lossy even though the format is still PNG.

| Image | Original PNG | Compressed PNG (256 colours) | JPG 85% | WebP 85% |
|---|---|---|---|---|
| Photos (average of 5) | 599 KB | 187 KB (0.874) | 73 KB (0.927) | 64 KB (0.939) |
| Home-page screenshot | 292 KB | 154 KB (0.972) | 115 KB (0.982) | 58 KB (0.987) |
| Tool-page screenshot | 124 KB | 85 KB (0.990) | 77 KB (0.989) | 40 KB (0.994) |
| Text-heavy page | 234 KB | 117 KB (0.999) | 199 KB (0.977) | 121 KB (0.988) |
| Chart | 21 KB | 15 KB (0.999) | 47 KB (0.976) | 12 KB (0.982) |

## What each result tells you

**Photos: do not use palette PNG.** It cut the files by about 69%, but similarity dropped to 0.87, which is visible banding in skies and skin. JPG and WebP at 85% were smaller *and* scored higher (0.93 and 0.94). Photographs belong in a lossy photo format.

**Screenshots: WebP wins clearly.** On the homepage screenshot WebP was 80% smaller than the PNG, against 61% for JPG and 47% for palette PNG. On the tool page the figures were 68%, 38% and 32%.

**Text pages: JPG is the wrong tool.** JPG saved only 15% and scored the lowest (0.977), because it smears the sharp edges around letters. Palette PNG halved the file (50% smaller) with a score of 0.9988, which is effectively identical. WebP matched it on size and scored 0.988.

**Charts: JPG made the file bigger.** The chart's PNG was 21 KB. The JPG came out at 47 KB, about 2.2 times larger, and it looked worse. Flat colours and hard edges are exactly what PNG is good at and JPG is bad at. Palette PNG saved 31% with a score of 0.9994; WebP saved 45%.

## A note on palette size

Fewer colours is not always smaller. On the chart, dropping the palette from 256 to 64 colours produced a *larger* file (17 KB against 15 KB), because dithering a smaller palette adds noise that compresses badly. For photos, 64 colours saved more bytes but pushed the similarity score down to 0.78. The default of 256 is a sensible starting point. If you want to see how the palette encoder works, we wrote up [how a PNG compressor works in plain JavaScript](/blog/png-compressor-vanilla-javascript).

## What this does not tell you

Every image type here was tested at one setting per format, JPG and WebP at 85%, so the table is a snapshot, not a ranking for all settings. If you want to see how the two lossy formats behave across the whole quality slider, our [JPG vs WebP quality measurements](/blog/jpg-vs-webp-quality-settings) cover that. We also did not test AVIF, which is often smaller still but is not yet supported everywhere. And SSIM is a good proxy for how similar two images look, not a verdict on how they look to you, so always check the output at full size before you replace an original.

A last practical point: the ordering of formats changed with the image type, not with the size of the file. The photos favoured WebP and JPG, the text page favoured palette PNG, and the chart ruled JPG out entirely. If you process a folder with mixed content, sort it by what each image shows rather than choosing one format for the whole batch.

## A simple rule from these numbers

| Your image | Try first | Why |
|---|---|---|
| Photo | WebP or JPG at 80% to 85% | Smallest, and a high similarity score |
| Screenshot or interface | WebP at 85% | About 60% to 80% smaller than PNG |
| Text, diagram or chart | Compressed PNG (256 colours) | Near-identical to the original, about 30% to 50% smaller |
| Anything with transparency | PNG or WebP | JPG has no transparency |

For picking between JPG, PNG, WebP and AVIF in general, see our [image format guide](/blog/best-image-format-for-web).

:::tool compress-png|Compress a PNG:::
:::tool png-to-webp|Convert PNG to WebP:::
:::tool png-to-jpg|Convert PNG to JPG:::
