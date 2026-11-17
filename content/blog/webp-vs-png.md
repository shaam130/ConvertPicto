---
title: WebP vs PNG: Which Is Smaller? We Measured 6 Image Types
h1: WebP vs PNG: which is smaller, and when should you use each?
description: WebP vs PNG tested on photos, screenshots, text, a chart and a transparent logo. Lossy and lossless sizes, quality scores, and when PNG still wins.
excerpt: WebP is usually smaller, but lossless WebP depends on the encoder. Measured sizes for six kinds of image, including a correction on our own tool.
date: 2026-11-09
keyword: webp vs png
tools: png-to-webp, webp-to-png, compress-png, png-to-jpg
---

**The short answer:** WebP is smaller than PNG in most cases, often by a wide margin, but how much depends on two choices you may not know you are making: lossy or lossless, and which encoder made the file. We measured both on six kinds of image so you do not have to guess.

## How we tested

We took six sets of images, each saved as a normal PNG: five photographs, two website screenshots, a text-heavy page, a bar chart, and a logo with a transparent background and a soft shadow. Every one went through ConvertPicto's PNG to WebP converter in headless Chromium at 85% quality (lossy) and at 100% (lossless). To check the browser's results against a dedicated encoder, we also saved each image as lossless WebP with libwebp, the reference WebP encoder, and re-saved each PNG with PNG optimisation switched on. Lossless outputs were compared pixel by pixel with the original. Lossy outputs were scored with SSIM, where 1.000 means identical.

## Lossy WebP (85%) vs PNG

| Image | PNG | WebP 85% | WebP vs PNG | Similarity (SSIM) |
|---|---|---|---|---|
| Photos (5, combined) | 2,997 KB | 320 KB | 89% smaller | 0.939 |
| Home-page screenshot | 292 KB | 58 KB | 80% smaller | 0.987 |
| Tool-page screenshot | 124 KB | 40 KB | 68% smaller | 0.994 |
| Text-heavy page | 234 KB | 121 KB | 48% smaller | 0.988 |
| Bar chart | 21 KB | 12 KB | 45% smaller | 0.982 |
| Transparent logo | 13 KB | 14 KB | 7% larger | 0.965 |

For photographs and screenshots lossy WebP is dramatically smaller. The five photos went from 2,997 KB to 320 KB, which is 89% smaller, and the home-page screenshot dropped 80%. The small logo is the exception: it is so simple that PNG already stores it efficiently, and lossy WebP came out slightly larger. The price of lossy WebP is that it changes pixels, which shows in the scores: the text page and the chart stay close to the original, but nothing is bit-for-bit identical.

## Lossless WebP vs PNG: the encoder matters

If you need the picture to stay exactly the same, you compare PNG with *lossless* WebP. Here our results were surprising.

| Image | PNG | PNG optimised | WebP lossless (browser's encoder) | WebP lossless (libwebp) |
|---|---|---|---|---|
| Photos (5, combined) | 2,997 KB | 2,925 KB | 2,626 KB | 2,449 KB |
| Home-page screenshot | 292 KB | 273 KB | 310 KB | 197 KB |
| Tool-page screenshot | 124 KB | 126 KB | 151 KB | 76 KB |
| Text-heavy page | 234 KB | 241 KB | 280 KB | 76 KB |
| Bar chart | 21 KB | 21 KB | 90 KB | 5.2 KB |
| Transparent logo | 13 KB | 10 KB | 16 KB | 5.6 KB |

Both WebP columns reproduce the original's opaque pixels exactly. The difference is size. The browser's built-in encoder gave lossless WebP files that were **larger than the PNG** for the screenshots, the text page, the chart and the logo. The chart, for example, grew from 21 KB to 90 KB. The photographs did shrink, to 2,626 KB from 2,997 KB. libwebp gave a very different picture: the chart came out at 5.2 KB (76% smaller than the PNG), the text page at 76 KB (67% smaller), the tool-page screenshot 39% smaller and the logo 56% smaller. Photographs, which are already hard to compress without losing detail, shrank by 18%.

We measured the output, not the reason. The likely explanation is that a browser prefers speed over squeezing out every byte. The practical lesson is that "WebP is smaller than PNG" is reliably true for lossy WebP, and for lossless WebP only if the tool uses a strong encoder.

**A correction on our own tool.** When we first ran this test, ConvertPicto's PNG to WebP converter used the browser's encoder at 100% quality, so it produced the larger files in the fourth column. We have since switched 100% quality to libwebp, compiled to WebAssembly and run inside your browser, so nothing is uploaded. The libwebp column is what the converter now produces, measured through the real page. We use libwebp's balanced effort setting, which takes about a second on these images. Its maximum-effort setting saved a further 14% on the home-page screenshot, but took 6 to 10 times longer on the screenshots and photos we timed it on, so we did not make it the default.

## Transparency

Both formats support transparency, and WebP kept the alpha channel intact in every test: for the logo it matched the original at 100%, 85% and 75% quality. One caveat applies to any browser-based converter, ours included. Browsers store canvas colours premultiplied by alpha, so a partly transparent pixel can shift by a level or two; in a separate test, half-transparent pixels differed by at most 1 level out of 255, and opaque pixels were identical. At 85% the colours shifted slightly (SSIM 0.965), which is the usual lossy trade-off, so for logos and icons where exact colours matter, use lossless WebP or keep the PNG.

## So which should you use?

| Situation | Pick | Why |
|---|---|---|
| Photo on a web page | Lossy WebP, 80% to 85% | About 89% smaller than PNG in our test |
| Screenshot or interface image | Lossy WebP, 85% | About 80% smaller on our screenshot |
| Logo, icon or chart that must stay exact | Lossless WebP from a strong encoder, or PNG | libwebp was 76% smaller than PNG on our chart |
| Text-heavy image | Lossless WebP from a strong encoder, or PNG | Lossy WebP blurs small text; lossless libwebp was 67% smaller than PNG |
| You need the widest compatibility | PNG | Some older apps still cannot open WebP |
| Transparent image for the web | WebP or PNG | Both keep the alpha channel |

If you already have WebP files and need PNGs for an app that cannot open them, our [WebP to PNG converter](/webp-to-png) does that in your browser, and our guide to [what a WebP file is and how to open one](/blog/what-is-a-webp-file) covers the rest. For a wider comparison that includes JPG, see [PNG vs JPG vs WebP, measured](/blog/png-vs-jpg-vs-webp-tested).

## Limits of this test

Six image types is a sample, not a survey, and a different photo or screenshot will give different percentages. We tested one browser encoder and one full-effort encoder. We did not test AVIF, animated WebP, or the effect of different quality settings in this article; the [JPG vs WebP quality measurements](/blog/jpg-vs-webp-quality-settings) cover the quality slider.

:::tool png-to-webp|Convert PNG to WebP:::
:::tool webp-to-png|Convert WebP to PNG:::
:::tool compress-png|Compress a PNG:::
