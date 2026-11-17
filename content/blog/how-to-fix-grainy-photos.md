---
title: How to Fix Grainy Photos (Free, With Measured Results)
h1: How to fix grainy photos, and how much a free filter really helps
description: Why photos come out grainy, how to stop it next time, and how to clean one up for free. We tested a no-upload noise filter on five photos and measured the result.
excerpt: Grain comes from too little light, not a bad camera. How to prevent it, how to reduce it for free in your browser, and what a simple filter can and cannot do.
date: 2026-11-10
keyword: how to fix grainy photos
tools: reduce-image-noise, compress-jpg, resize-image, compress-image-to-100kb
---

**The short answer:** grainy photos are caused by too little light reaching the sensor, so the camera boosts the signal and the boost amplifies random speckle. You fix a photo you already have by running a noise filter, and you prevent the next one by giving the camera more light. We tested a free filter on five photographs with known, added noise, so we can tell you how much it helps and where it stops helping.

## Why photos look grainy

A camera sensor counts light. In a dim room there is not much light to count, so the signal is weak, and the camera compensates by raising its sensitivity (the ISO setting, or the phone's equivalent). Raising sensitivity does not add detail. It amplifies everything, including the random electrical variation that is always present, and that variation shows up as coloured speckle, especially in flat, dark areas such as a night sky, a wall or skin in shadow.

Phones make this more likely for three reasons. Their sensors are tiny, so they collect little light. Digital zoom crops the image and enlarges the noise along with it. And brightening a dark photo afterwards, in an editor, lifts the shadows and makes hidden noise visible. If a photo looked fine on the phone and grainy after you edited it, that is why.

## Stop it before you take the photo

Prevention beats repair, because no filter can bring back detail that was never captured.

- **Add light.** Turn on a lamp, face a window, or move away from the corner of the room. One extra light source does more than any setting.
- **Use night mode.** Most modern phones have a mode that takes several frames and combines them, which averages noise away. Hold still for the full exposure.
- **Do not use digital zoom.** Move closer, or crop later. Cropping afterwards gives the same result without the extra processing.
- **Clean the lens.** A smudge looks like haze, and haze makes you raise exposure.
- **Tap on the subject to set exposure,** so the camera does not guess too dark and then brighten the whole frame.

## Fix a grainy photo you already have

You have three realistic options. Phone and desktop editors such as Lightroom and Photoshop include noise-reduction sliders, and recent versions have AI-based denoising that learns what real detail looks like; they are the best choice when you have them. Your phone's own editor often has a "noise" or "grain" setting. The third option is a free filter that runs in your browser: our [reduce image noise](/reduce-image-noise) tool, which needs no sign-up and never uploads the photo.

It uses an edge-preserving bilateral filter. Each pixel is replaced by a weighted average of nearby pixels, but a neighbour counts for less the more its colour differs from the centre pixel. Flat areas, where grain is most visible, get smoothed, while a sharp edge is mostly left alone. There are three strengths: Light, Medium and Strong.

## What we measured

To know how well a filter works you need to know what the clean picture looked like, so we did not use real grainy photos. We took five clean photographs, added random brightness and colour noise at two strengths, cleaned them with the tool running in the real page in headless Chromium, saved the result as JPG at quality 90, and compared each result with the clean original. PSNR and SSIM measure closeness to the original: higher is better, and SSIM of 1.000 means identical.

| Added noise | Before cleaning | Light | Medium | Strong |
|---|---|---|---|---|
| Mild: PSNR | 31.8 | 34.3 | 34.3 | 32.7 |
| Mild: SSIM | 0.764 | 0.884 | 0.896 | 0.864 |
| Heavy: PSNR | 26.0 | 27.5 | 30.0 | 31.2 |
| Heavy: SSIM | 0.521 | 0.591 | 0.728 | 0.816 |

The pattern is the one you would hope for. For mild grain, Medium gave the closest result (Light tied it on PSNR), and Strong scored lower than either, because it started removing real detail along with the grain. For heavy grain, Strong was best on all five photos, and the improvement was large: SSIM went from 0.52 to 0.82. In practice that means you should pick the weakest strength that makes the grain stop bothering you, not the strongest.

:::note Caveat: this is synthetic noise on small test photos, which lets us score the result exactly. Real camera noise is patchier and varies by colour channel, so your photos will not behave identically. The free filter also loses to AI denoisers on fine texture such as hair and fabric.:::

## Cleaner photos are also smaller files

Grain is random detail, and random detail is the hardest thing for a JPG to store. We saved the same photos as JPG at quality 90 in three ways and compared the sizes.

| Version | Mild grain | Heavy grain |
|---|---|---|
| Grainy photo, no cleaning | baseline | baseline |
| Cleaned with Light | 24% smaller | 9% smaller |
| Cleaned with Medium | 39% smaller | 26% smaller |
| Cleaned with Strong | 48% smaller | 43% smaller |
| The original clean photo | 30% smaller | 43% smaller |

Part of that saving is removed grain and part is removed detail, so a smaller file is not automatically a better photo. It also explains a common surprise: a grainy night photo is often noticeably bigger than a clean daylight photo, even at the same pixel size. If you are fighting an upload limit, cleaning the grain first and then using [compress to a target size](/compress-image-to-100kb) gives a sharper result at the same limit than compressing the grainy file directly.

## When grain is not a problem

If you will only ever view the photo small, on a phone screen or as a thumbnail, grain is mostly invisible, and shrinking the photo hides it for free. Resizing a photo to half its width averages four pixels into one, which reduces random noise on its own. In our test, halving the dimensions raised the similarity to the clean photo from a PSNR of 31.8 to 38.6 for mild grain and from 26.0 to 32.8 for heavy grain (each compared with an equally resized clean copy). The [resize tool](/resize-image) does this, and it is worth trying before the stronger filter settings if the photo does not need to be large.

## Quick steps

Open the noise reduction tool, choose Medium, drop in your photo, and compare the result with the original at full size. If grain is still visible, try Strong. If faces look waxy or text looks smeared, go back to Light. Then save as JPG for the smallest file, or PNG if you plan to edit it again.

:::tool reduce-image-noise|Reduce image noise:::
:::tool compress-jpg|Compress a JPG:::
:::tool resize-image|Resize an image:::
