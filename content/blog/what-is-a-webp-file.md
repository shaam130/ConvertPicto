---
title: What Is a WebP File — and How Do You Open or Convert One?
h1: What is a WebP file, and how do you open one?
description: WebP explained in plain terms — why you keep downloading them, how to open a WebP on Windows, Mac, iPhone and Android, how to convert one to JPG or PNG, and whether you should use them yourself.
excerpt: Why the internet keeps giving you files you can't open, how to open them anyway, and when WebP is actually the right choice.
date: 2026-09-09
updated: 2026-11-09
keyword: what is a webp file
tools: webp-to-png, webp-to-jpg, png-to-webp
---

You right-clicked an image, saved it, and got a file ending in `.webp`. Now Photoshop won't open it, your client says they can't view it, and you're wondering what happened to plain old JPG.

Here's what a WebP file is, why you keep getting them, and how to deal with it.

## The short answer

WebP is an image format created by Google in 2010. It does the same job as JPG and PNG but produces smaller files — roughly 25–35% smaller than JPG at the same visual quality. In our own tests, lossy WebP was between 45% and 89% smaller than PNG on five of six kinds of image (see [WebP vs PNG, measured](/blog/webp-vs-png)).

Every modern web browser displays WebP without issue. That's precisely why you're encountering it: websites serve WebP because smaller images mean faster pages, and when you save one, you get the format the site was using rather than the JPG you expected.

The friction isn't in browsers. It's in everything else — older desktop software, some email clients, various content management systems and plenty of corporate tools that were written before 2015 and never updated.

:::tool webp-to-png|Convert WebP to PNG:::

## How to open a WebP file in ten seconds

Drag the file into Chrome, Edge, Firefox or Safari and it opens. If you need to edit it, or use it in an app that does not understand WebP, convert it to PNG or JPG with the converter above. It runs in your browser, so the file is not uploaded anywhere. Step-by-step instructions for Windows, Mac, iPhone and Android are further down.

## Why websites use it

Images are usually the heaviest thing on a web page, and page speed affects both user patience and search rankings. If a site can cut its image weight by a third without any visible quality loss, that's an easy decision.

WebP also does something neither JPG nor PNG can do alone: it supports **both** lossy compression (like JPG) **and** transparency (like PNG), in the same format. Before WebP, a designer who needed a transparent background was forced into PNG and its large file sizes, even for a photographic image. WebP removed that trade-off.

It can also do animation, making it a smaller replacement for animated GIFs.

## How to open a WebP file

### The easiest method, on any device

Drag it into your web browser. Chrome, Firefox, Edge and Safari all display WebP natively. If you just want to *see* the image, that's the whole answer — you don't need to convert anything.

### Windows

Windows 10 and 11 open WebP in the Photos app and show thumbnails in File Explorer without any extra software. If yours doesn't, you're on an older build; installing the free "Webp Image Extensions" from the Microsoft Store fixes it.

Paint, Paint 3D and the Photos app can all re-save a WebP as JPG or PNG via **Save as**.

### macOS

macOS Big Sur (2020) and later support WebP in Preview, Finder and Quick Look. To convert: open in Preview, then **File → Export**, and choose JPEG or PNG.

Older macOS versions can't open them without third-party software, which is where a browser-based converter is the quickest route.

### iPhone and iPad

Safari displays WebP fine. Saving one to your Photos library is less reliable — iOS sometimes converts it automatically, sometimes refuses. If you need it in your camera roll, converting it to JPG first is the dependable path.

### Android

Android has supported WebP since version 4.0, so Google Photos and most gallery apps handle it natively.

### Photoshop and design software

Photoshop added native WebP support in version 23.2 (2022). If you're on an older release, you'll need the free WebPShop plugin from Google, or you can convert to PNG first. GIMP has supported WebP since 2.10. Figma imports WebP but doesn't export it. Affinity Photo supports it via a plugin.

## How to convert a WebP file

You have three broad options.

**Use built-in software.** Preview on Mac (File → Export) or Paint/Photos on Windows (Save as). Free, offline, and no upload — but tedious for more than a few files.

**Use a browser-based converter.** Fast, works on any device, handles batches. Choose one that processes in your browser rather than uploading, particularly if the image is private — you can verify this by turning off your Wi-Fi and seeing whether the tool still works.

**Use the command line**, if that's your thing. With ImageMagick installed: `magick input.webp output.png`. Google's own `dwebp` tool does the same: `dwebp input.webp -o output.png`.

### Which format should you convert to?

**PNG** if the image has transparency, or contains text, logos or sharp edges. PNG is lossless, so nothing further is lost in the conversion.

**JPG** if it's a photograph and you need maximum compatibility or a smaller file. Note that transparent areas will be filled with a solid colour, since JPG can't store transparency — a decent converter lets you choose which colour.

One thing worth understanding: converting a lossy WebP to PNG does **not** restore lost detail. The WebP was already compressed; PNG simply stores that compressed result perfectly. The file will get *bigger* without getting better. That's expected, not a bug.

:::tool webp-to-jpg|Convert WebP to JPG:::

## Should you use WebP on your own site?

Mostly yes, with one caveat.

**Use it for images displayed on your website.** Every browser your visitors use supports it, and the file size saving is real and free. If you want to be thorough, serve it with a fallback:

```
<picture>
  <source srcset="photo.webp" type="image/webp">
  <img src="photo.jpg" alt="Description">
</picture>
```

Browsers that understand WebP take the first source; anything else falls back to the JPG.

**Don't use it for files you send to other people.** Email attachments, files for a client, anything that will be opened in desktop software you don't control — send JPG or PNG. The compatibility gap is in applications, not browsers, and you can't predict what the recipient is running.

That's the whole rule: **WebP for display, JPG/PNG for exchange.**

:::tool png-to-webp|Convert PNG to WebP:::

## Common questions

**Is WebP better quality than JPG?** At the same file size, generally yes — it holds detail better and produces fewer visible artefacts. At the same quality *setting*, it produces a smaller file. Both are lossy, so neither is "lossless" in the strict sense unless you specifically use WebP's lossless mode.

**Does converting WebP to JPG lose quality?** Slightly, because you're re-encoding a lossy image with another lossy codec. Use quality 90 or above and it's imperceptible. Converting to PNG loses nothing, but produces a much larger file.

**Why can't I open WebP in an email?** Most email clients don't render WebP inline. Send JPG or PNG instead.

**Is AVIF replacing WebP?** AVIF is more efficient — typically 20–30% smaller again — and browser support is now good. But encoding is slower, tooling is less mature, and support outside browsers is thinner than WebP's. WebP remains the pragmatic choice for most sites; AVIF is worth adding as a progressive enhancement.

**Can I recover the original JPG from a WebP?** No. If a site converted a JPG to WebP, the original is gone from your copy. Converting back gives you an image derived from the WebP, not the original file.

## Summary

WebP is a modern image format that's smaller than JPG and PNG while supporting both lossy compression and transparency. Browsers all handle it; desktop software is catching up but hasn't fully arrived. Use it on your website, convert it to JPG or PNG when you need to send a file to someone else, and open it by dragging it into a browser when you just want to look at it.
