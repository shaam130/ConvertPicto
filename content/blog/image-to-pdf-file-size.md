---
title: How Big Will Your Image PDF Be? Measured Results
h1: How big will your image PDF be? We measured it
description: Five photos combined into one PDF at three quality levels and two page settings, from JPG and PNG sources. What actually controls PDF file size.
excerpt: Page size does not change the file size, but quality does, a lot. Measured PDF sizes from JPG and PNG sources.
date: 2026-10-23
keyword: image to pdf file size
tools: jpg-to-pdf, png-to-pdf, image-to-pdf
---

You drop five photos into an image-to-PDF tool and get back one PDF. Is it going to be a modest download or a 20 MB email attachment? We measured what really controls the size.

## How we tested

The same five photographs were prepared two ways: as high-quality JPEGs (quality 95, 715 KB in total) and as lossless PNGs (2.93 MB in total). We combined each set into a single five-page PDF with ConvertPicto's image to PDF tools in headless Chromium, using A4 and "fit to image" page settings at quality 90 (the default), 70 and 50. The resulting PDFs were opened with a PDF library to check page counts and sizes.

## Results

| Source files | Page setting | Quality | PDF size | Share of source total |
|---|---|---|---|---|
| JPG (715 KB) | A4 | 90 | 512 KB | 72% |
| JPG | A4 | 70 | 231 KB | 32% |
| JPG | A4 | 50 | 160 KB | 22% |
| PNG (2.93 MB) | A4 | 90 | 476 KB | 16% |
| PNG | A4 | 70 | 230 KB | 8% |
| PNG | A4 | 50 | 160 KB | 5% |

All twelve runs produced a five-page PDF.

## What controls the size

**1. Page size does not.** The "fit to image" PDF from the JPG set at quality 90 was 524,661 bytes. The A4 version was 524,673 bytes. That is a difference of 12 bytes. The page is only a frame around the image, and each page of the A4 version measured 595 x 842 points (A4) while the fitted pages followed the picture, for example 384 x 384 points for the first square photo. Pick the page size for how it prints, not for the file size.

**2. Quality does, a lot.** Dropping from 90 to 70 took the PDF from 512 KB to 231 KB, a 55% saving. At 50 it was 160 KB.

**3. PNG sources shrink the most, because they are converted.** The PDF writer embeds images as JPEG data. PNG sources are therefore converted to JPEG on the way in, which is why 2.93 MB of PNGs became a 476 KB PDF. If your source images are already JPEGs, there is less to gain, and the PDF can end up at 72% of the sources even at the default quality.

## Why JPG sources do not shrink much

The JPG row is the one people find surprising. Our JPEG sources were saved at quality 95, which is a high-quality, camera-style setting, so the files were already efficient. Re-encoding them at quality 90 trims only a little (715 KB of sources became a 512 KB PDF), and each step down the slider saves more. The takeaway is that the PDF tool is not hiding a loss-free shortcut. Every page is re-compressed at the quality you pick, so the quality slider is the real size control, and the page-size menu is only layout.

The PNG row shows the opposite effect. A lossless PNG carries far more data than a JPEG of the same picture, which is why 2.93 MB of sources fell to 476 KB at the default quality. The price is that PNG sources are converted to lossy JPEG inside the PDF. For photographs that is fine. For a page of crisp text or a line diagram, check the result at 90 before you go lower, because JPEG blurs hard edges (see our [PNG vs JPG vs WebP measurements](/blog/png-vs-jpg-vs-webp-tested) for how much).

## What the numbers mean for common jobs

| Job | Starting point | What to expect |
|---|---|---|
| Emailing a few phone photos as one PDF | Quality 70 | About a third of the combined JPEG size |
| Printing a photo album | Quality 90 and A4 | Close to the source size, best print quality |
| Uploading a form scan with a size limit | Quality 50, after resizing wide scans | Smallest output in our test, 160 KB for five pages |
| Keeping a screenshot readable | Quality 90 | Text edges stay clean; lower settings blur small type |

Page order follows the order of the files you add, and all of our test runs kept the five pages in that order, so name your files 01, 02, 03 before you add them if sequence matters.

## Practical advice

- **Scans and photos:** quality 70 is a sensible default for documents you will view on screen or email. Go up to 90 only if the PDF will be printed.
- **PDF is too large?** Resize the images first. Halving the width leaves about a quarter of the pixels, and our [resize measurements](/blog/resize-vs-compress-image-file-size) show roughly 16% of the original file size at 50% width.
- **Mixed sources:** it does not matter whether the pictures were PNG or JPEG for the final size at a given quality. What matters is pixel count and the quality setting.
- **Privacy:** the PDF is built in your browser, so a scan of an ID or a contract is not uploaded anywhere. More on that in [how to combine images into one PDF](/blog/convert-images-to-pdf).

:::tool image-to-pdf|Combine images into a PDF:::
:::tool jpg-to-pdf|JPG to PDF:::
:::tool png-to-pdf|PNG to PDF:::

:::note Caveat: five small photographs. A document scan or a 12-megapixel phone photo will give different absolute sizes, but quality and pixel count remain the two controls.:::
