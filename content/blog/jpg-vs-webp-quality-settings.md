---
title: JPG vs WebP: What Each Quality Setting Really Costs
h1: JPG vs WebP quality settings: what each level really costs in file size
description: The same five photos converted to JPG and WebP at nine quality settings, with measured file sizes and similarity scores. Where quality stops paying off.
excerpt: Nine quality settings, two formats, five photos, measured. Where the file-size curve is gentle, and where it falls off a cliff.
date: 2026-10-23
keyword: jpg vs webp quality
tools: png-to-jpg, png-to-webp, compress-jpg
---

Every converter has a quality slider, and almost nobody knows what the numbers on it mean. Is 80% noticeably worse than 90%? Is 100% worth it? Does WebP's "80" mean the same thing as JPG's "80"?

We stopped guessing and measured. The same five photographs went through ConvertPicto's own JPG and WebP converters at nine quality settings each. For every output we recorded the file size and scored how close it is to the original.

## How we tested

- **Photos:** five freely licensed sample photographs (NASA and CC0 images bundled with the scikit-image library), from 0.14 to 0.87 megapixels. Saved as lossless PNG first.
- **Conversion:** the real PNG to JPG and PNG to WebP pages, running in headless Chromium, with the quality slider set to 40, 50, 60, 70, 80, 85, 90, 95 and 100.
- **Scoring:** SSIM (structural similarity, where 1.000 means identical) and PSNR, computed against the original PNG.

One caveat up front: these photos are small, so the absolute sizes in KB are small too. The percentages and the shape of the curve are what carry over to your own images. SSIM is also a proxy for how an image looks, not a replacement for your eyes.

## JPG: gentle until 90, then a cliff

| Quality | Average size | Share of the PNG | Similarity to original (SSIM) |
|---|---|---|---|
| 40% | 26 KB | 4.9% | 0.859 |
| 50% | 31 KB | 5.7% | 0.875 |
| 60% | 37 KB | 6.7% | 0.886 |
| 70% | 45 KB | 8.1% | 0.898 |
| 80% | 59 KB | 10.3% | 0.915 |
| 85% | 73 KB | 12.5% | 0.927 |
| 90% | 95 KB | 15.9% | 0.941 |
| 95% | 140 KB | 22.8% | 0.961 |
| 100% | 372 KB | 67.0% | 0.998 |

From 40% to 90% the average file grows about 3.6 times, from 26 KB to 95 KB, while similarity climbs from 0.86 to 0.94. That is a fair trade.

Then the curve breaks. Going from 90% to 100% multiplies the file by 3.9, to 372 KB, and the 100% file is about 5.3 times the size of the 85% one. Even 95% costs 82% more than 85% for a similarity gain of 0.034. For photos you will view on a screen, the sweet spot sits between 80% and 90%.

## WebP: smaller at every setting, with one trap

| Quality | Average size | Share of the PNG | Similarity to original (SSIM) |
|---|---|---|---|
| 40% | 20 KB | 3.8% | 0.868 |
| 50% | 24 KB | 4.4% | 0.881 |
| 60% | 29 KB | 5.1% | 0.893 |
| 70% | 34 KB | 6.0% | 0.904 |
| 80% | 48 KB | 8.0% | 0.924 |
| 85% | 64 KB | 10.2% | 0.939 |
| 90% | 88 KB | 13.7% | 0.954 |
| 95% | 127 KB | 20.0% | 0.966 |
| 100% | 525 KB | 86.7% | 1.000 |

At the same slider position, WebP files are smaller than JPG files and score higher on similarity. At 80%, WebP averaged 48 KB with SSIM 0.924, against 59 KB and 0.915 for JPG.

The trap is the top of the scale. In Chromium, WebP at 100% switches to **lossless** encoding. The files average 87% of the original PNG, which is larger than JPG at 100%, and the similarity score is exactly 1.000. If you want a small WebP, stay at 90% or below.

## Same quality, how much smaller is WebP?

Slider numbers are not comparable between formats, so we matched files by **similarity** instead. For each WebP file we interpolated the JPG size that would reach the same SSIM on the same photo.

| WebP quality | WebP size as a share of equal-quality JPG | Range across the five photos |
|---|---|---|
| 60% | 70% | 58% to 79% |
| 70% | 69% | 59% to 78% |
| 80% | 68% | 58% to 77% |
| 85% | 68% | 63% to 75% |
| 90% | 71% | 68% to 75% |

On average a WebP came out about **31% smaller** than a JPG of the same measured quality. It varies by photo, from 58% to 79% of the JPG's size, so treat the average as a guide rather than a promise.

At 80% quality, per photo:

| Photo | PNG original | JPG | WebP | WebP saving vs JPG |
|---|---|---|---|---|
| Astronaut | 415 KB | 45 KB | 31 KB | 30% |
| Chelsea | 216 KB | 23 KB | 17 KB | 26% |
| Coffee | 439 KB | 47 KB | 38 KB | 20% |
| Rocket | 305 KB | 31 KB | 24 KB | 25% |
| Hubble | 1,622 KB | 150 KB | 132 KB | 12% |

## What to use

- **Default:** JPG at 80% to 85%, or WebP at 75% to 85%. Past that you pay a lot for differences that are hard to see.
- **Avoid 100%:** it is the most expensive setting in both formats and rarely buys anything visible.
- **Need to share widely or email it:** JPG still opens everywhere. WebP is smaller and works in all current browsers, but some older apps still cannot open it.
- **Already have a big JPG?** Re-compress it instead of converting it. See our guide to [reducing image file size without losing quality](/blog/reduce-image-file-size).

:::tool png-to-webp|Convert PNG to WebP:::
:::tool png-to-jpg|Convert PNG to JPG:::
:::tool compress-jpg|Compress a JPG:::

:::note Everything ran on your own CPU, the same way it does on the live site: no file was uploaded anywhere during these tests, which is the whole point of the tool.:::
