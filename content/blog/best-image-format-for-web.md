---
title: JPG vs PNG vs WebP vs AVIF — Which Format Should You Use?
h1: JPG vs PNG vs WebP vs AVIF: which image format should you use?
description: A practical comparison of JPG, PNG, WebP, AVIF, GIF and SVG — what each format is good at, which one to pick for photos, logos and screenshots, and when the "best" format is the wrong choice.
excerpt: Five formats, one decision. Here's what each one is actually good at, with a rule of thumb you can apply in ten seconds.
date: 2026-09-09
keyword: best image format for web
tools: png-to-webp, jpg-to-webp, compress-png, webp-to-png
---

Most advice about image formats is either too vague to act on ("use the right format for the job") or too confident to be true ("always use WebP"). The honest answer is that four formats matter for the web, each is genuinely better at one thing, and the decision takes about ten seconds once you know what you're looking at.

Here's the short version, then the reasoning.

:::note **The ten-second rule.** Photograph → **WebP**, with JPG as the fallback. Logo, icon, screenshot or anything with transparency → **PNG**, or WebP if file size matters more than universal compatibility. Something that must open absolutely anywhere → **JPG**. A flat shape that should stay sharp at any size → **SVG**.:::

## The one thing that explains most of it: lossy vs lossless

Every format on this list falls into one of two camps, and this single distinction explains most of their behaviour.

**Lossy** formats (JPG, WebP, AVIF) throw information away permanently to make the file smaller. They exploit the fact that human eyes are bad at noticing small colour variations, so they approximate. The result is dramatically smaller files and a quality setting you control. The catch: every time you re-save a lossy image, it degrades a little more. Save a JPG ten times and you'll see it.

**Lossless** formats (PNG, GIF, and lossless modes of WebP) reconstruct the original pixel-for-pixel. Nothing is lost, ever, no matter how many times you re-save. The catch: they're much larger for photographs, because a photo has thousands of subtly different colours and lossless compression can't cheat.

That's why "which format is best" has no single answer. A photograph and a logo are fundamentally different kinds of image, and they want opposite things.

## JPG (JPEG) — the universal photo format

JPG has been around since 1992 and is supported by literally everything: every browser, every phone, every printer, every ancient piece of software in an office somewhere.

**Use it for:** photographs you need to share widely, anything going into an email, an old CMS, or a system you don't control.

**Don't use it for:** logos, screenshots, text, or anything with sharp edges. JPG's compression works by blurring detail across 8×8 pixel blocks, which is invisible in a photo of a face and horribly obvious around crisp black text on white. You'll see fuzzy grey halos, called artefacts.

**It also can't do transparency.** If you convert a transparent PNG to JPG, those areas have to become a solid colour — white by default, though a good converter lets you choose.

:::tool jpg-to-webp|Convert JPG to WebP:::

## PNG — lossless, and the only one of these with proper transparency

PNG stores every pixel exactly. It also supports an alpha channel, which means each pixel can be fully opaque, fully transparent, or anything in between — that's what gives you a logo with soft edges that sits cleanly on any background.

**Use it for:** logos, icons, screenshots, illustrations, diagrams, anything with text, and anything that needs transparency.

**Don't use it for:** photographs. A photo saved as PNG is often five to ten times bigger than the same photo as JPG or WebP, for no visible benefit.

There's a widespread belief that PNGs can't be compressed because they're lossless. That's only half true. A standard PNG stores 24-bit colour — around 16 million possible colours per pixel — but most graphics only use a few hundred distinct colours. Reducing the image to an optimised palette of up to 256 colours typically cuts the file by 50–80% with no visible change on graphics and screenshots. That's what dedicated PNG compressors do, and it's still lossless in the sense that the palette version is stored perfectly; it's the palette itself that's been simplified.

:::tool compress-png|Compress a PNG:::

## WebP — the sensible default for the web today

Google released WebP in 2010 and it's now supported by every browser people actually use. It does both lossy and lossless, it supports transparency, and it's meaningfully smaller than the alternatives: roughly 25–35% smaller than JPG at equivalent visual quality, and often 20–30% smaller than PNG for graphics.

**Use it for:** basically every image on a website you control.

**Don't use it for:** files you're sending to other people, or uploading to a platform you don't control. Support in browsers is universal; support in *desktop software* is not. Older versions of Photoshop, some email clients, various CMSes, and plenty of corporate systems still choke on it. If someone's going to download the file and open it in a desktop app, send JPG or PNG.

This is the practical distinction most guides miss: WebP is excellent for *displaying* images, and still a mild nuisance for *exchanging* them.

:::tool png-to-webp|Convert PNG to WebP:::

## AVIF — the most efficient, and the least universally supported

AVIF is derived from the AV1 video codec, and it's genuinely impressive: typically 20–30% smaller than WebP at the same quality, with better handling of gradients and dark areas. It supports transparency and high dynamic range.

**Use it for:** performance-critical sites where you can serve a fallback, using the `<picture>` element so browsers that can't handle AVIF get WebP or JPG instead.

**Don't use it as your only format.** Browser support is good in Chrome, Firefox, Edge and Safari 16+, but AVIF encoding is slow, tooling is patchier than WebP's, and support outside browsers is thin. Most sites get the majority of the benefit from WebP with a fraction of the hassle.

## GIF and SVG — different jobs entirely

**GIF** is limited to 256 colours and compresses poorly. Its one remaining purpose is short animations, and even there, a muted autoplaying MP4 or WebM is smaller and looks better. For a still image, GIF is essentially never the right answer.

**SVG** isn't a pixel format at all — it's a set of drawing instructions, so it stays perfectly sharp at any size and is usually tiny. Use it for logos, icons and simple illustrations that were drawn as vectors. It can't represent a photograph. You'll sometimes need to rasterise an SVG into PNG for platforms that don't accept vectors.

:::tool svg-to-png|Convert SVG to PNG:::

## Side by side

| Format | Lossy? | Transparency | Animation | Best for | Rough file size* |
|---|---|---|---|---|---|
| JPG | Yes | No | No | Photos, maximum compatibility | Baseline (100%) |
| PNG | No | Yes | No | Logos, screenshots, transparency | 300–800% for photos |
| WebP | Both | Yes | Yes | Almost everything on the web | 65–75% |
| AVIF | Both | Yes | Yes | Performance-critical sites | 45–60% |
| GIF | Lossy (256 colours) | 1-bit only | Yes | Short animations only | Poor |
| SVG | N/A (vector) | Yes | Yes | Logos, icons, vector art | Usually tiny |

\\* Approximate, for a typical photograph at equivalent perceived quality. Real numbers vary enormously with content.

## Some practical situations

**A photo for your website.** WebP at 80–85% quality. Serve JPG as a fallback if you support old software. Resize it to the size it's actually displayed at first — that usually saves more bytes than any format choice.

**A logo with a transparent background.** PNG, or WebP if it's for your own site. Never JPG.

**A screenshot for documentation.** PNG, then run it through a palette-based compressor — screenshots typically use very few distinct colours and shrink enormously.

**A photo to email to a client.** JPG at 85%. It will open on anything they own.

**An image for a print shop.** Ask them. Most want a high-resolution PNG, TIFF or PDF, not a compressed web format.

**A favicon.** ICO for maximum compatibility, plus a PNG for modern browsers.

## The thing that matters more than format

Choosing between WebP and JPG might save you 30% of a file's size. Resizing a 4000-pixel-wide camera photo down to the 800 pixels it's actually displayed at will save you 95%.

The single most common cause of a slow, image-heavy web page isn't the format — it's serving images at three or four times the dimensions they're shown at. Check the actual displayed size, resize to roughly double that for high-DPI screens, *then* pick your format and compress.

:::tool resize-image|Resize an image:::

## Summary

Use **WebP** for images on a site you control. Use **JPG** when the file has to open anywhere. Use **PNG** when you need transparency, sharp edges or text. Use **SVG** when the artwork is vector. Consider **AVIF** if you're chasing performance and can serve a fallback. Skip **GIF** unless it's animated.

And before you agonise over any of it, check whether your images are simply too big in dimensions. They usually are.
