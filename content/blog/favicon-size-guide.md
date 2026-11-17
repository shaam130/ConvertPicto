---
title: How to Make a Favicon — Sizes, Formats and Code (2026 Guide)
h1: How to make a favicon: every size and format you actually need
description: A complete favicon guide for 2026 — which sizes matter, ICO vs PNG vs SVG, the exact HTML to paste, and why your favicon might not be showing up.
excerpt: Which sizes you actually need, the exact HTML to paste, and the three reasons a favicon usually fails to appear.
date: 2026-09-09
keyword: favicon size guide
tools: favicon-generator, resize-image, png-to-ico
---

Favicons are one of those small tasks that look like a two-minute job and turn into an afternoon. Half the guides online list fourteen different files. The other half say "just use a 16×16 ICO" and leave you wondering why it looks blurry on your phone.

Here's what you actually need in 2026, why, and the exact code to paste.

:::note **The short answer.** For most sites: one `favicon.ico` containing 16, 32 and 48 pixel versions, one 180×180 PNG for iPhones, and three lines in your `<head>`. That's it. Everything beyond that is optional polish.:::

## Favicon size: what each size is for

A favicon isn't one image — it's the same artwork at several sizes, because different places display it at different scales. These are the ones that still matter:

| Size | Where it's used |
|---|---|
| 16×16 | Browser tab, bookmarks bar |
| 32×32 | Retina tabs, Windows taskbar shortcut, browser bookmark lists |
| 48×48 | Windows site shortcuts |
| 180×180 | iOS "Add to Home Screen" (apple-touch-icon) |
| 192×192 & 512×512 | Android home screen and PWA install prompt (web manifest) |

You do not need 57×57, 60×60, 72×72, 76×76, 114×114, 120×120 or 144×144. Those come from generators that still target iOS 6 and Android devices from 2013. Including them costs you nothing but clutter — but leaving them out costs you nothing at all.

## Favicon format: ICO, PNG or SVG?

**ICO** is a container format: a single `.ico` file can hold several sizes at once, and the browser picks the best fit. It's the most universally understood favicon format — every browser back to Internet Explorer reads it, and Windows uses it for desktop shortcuts. This is why `favicon.ico` in your site root still works even with no HTML at all: browsers look for it automatically.

**PNG** is supported by all modern browsers via `<link rel="icon" type="image/png">`. It's simpler to produce and better for large sizes. It's required for the iOS touch icon.

**SVG** favicons are supported in Chrome, Firefox and Edge. Safari has historically lagged behind, so check current support before relying on one. They're sharp at every size and can even adapt to dark mode using a media query inside the SVG. Nice to have, not a replacement — always pair with an ICO fallback.

The pragmatic combination: **ICO for the classic favicon, PNG for iOS and Android, SVG if you feel like it.**

| Format | Works in | Best for |
|---|---|---|
| ICO | Every browser, plus Windows shortcuts | The baseline favicon, several sizes in one file |
| PNG | All modern browsers | iPhone home screen (180×180), Android and web app icons |
| SVG | Chrome, Firefox and Edge | One sharp icon at every size, optional dark mode |

How big is the ICO file? We made one from an 800×500 PNG logo with our [favicon generator](/favicon-generator) and read it back with an image library. With the default 16, 32 and 48 pixel sizes it was 3.7 KB. With six sizes (16, 32, 48, 64, 128 and 256 pixels) the same file was 21.1 KB, about six times larger, and it still contained exactly the sizes we had ticked. For a favicon, the three small sizes are all most sites need, and they keep the file tiny.

:::tool favicon-generator|Generate a multi-size favicon.ico:::

## The HTML you actually need

Put this in your `<head>`. Three lines cover the overwhelming majority of cases:

```
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

If you want Android home-screen and PWA support, add a web manifest:

```
<link rel="manifest" href="/site.webmanifest">
```

…with a `site.webmanifest` containing:

```
{
  "name": "Your Site",
  "short_name": "Site",
  "icons": [
    { "src": "/icon-192.png", "type": "image/png", "sizes": "192x192" },
    { "src": "/icon-512.png", "type": "image/png", "sizes": "512x512" }
  ],
  "theme_color": "#6366f1",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

Note the `sizes="any"` on the ICO line. Without it, some Chrome versions prefer the SVG in contexts where the ICO would look better. It's a small detail that saves a confusing afternoon.

## Designing artwork that survives 16 pixels

This is where most favicons fail, and it's a design problem rather than a technical one. At 16×16 you have 256 pixels total — about the area of a full stop on this page.

**Don't shrink your full logo.** A wordmark that reads perfectly on your site becomes an unreadable smudge. Take the most distinctive *element* — a single letter, a shape, a symbol — and use that alone.

**Use high contrast.** Thin lines and subtle gradients disappear. Bold shapes and strong colour differences survive.

**Fill the frame.** Leave only a couple of pixels of padding at the smallest size, or your icon looks smaller than everyone else's in the tab bar.

**Test it small before you commit.** Zoom your design to 16 pixels and look at it from normal viewing distance. If you can't identify it, simplify further.

**Start from a large square.** Work at 512×512 or larger, ideally as a vector, and scale down. Scaling a small image up produces a soft, blurry icon.

:::tool resize-image|Resize your logo to the right dimensions:::

## Why your favicon isn't showing up

Almost every "my favicon isn't working" case is one of these three.

**1. Browser caching.** Favicons are cached extremely aggressively — far more than normal images — and a hard refresh often isn't enough. To check whether the file itself is fine, visit `yoursite.com/favicon.ico` directly in the address bar. If the icon loads there, your file is correct and you're looking at a cache. Clear site data, or test in a private window. Others visiting for the first time will see it correctly.

**2. Wrong path.** A `href="favicon.ico"` without the leading slash resolves relative to the current page, so it breaks on any URL below the root. Use `/favicon.ico`.

**3. The file isn't where you think.** It needs to be in your public web root — `public_html`, `www`, `dist`, or whatever your host serves from. If you can't load it directly in the browser, no amount of HTML will help.

A fourth, rarer one: some hosts serve `.ico` with the wrong content type. If the file loads as a download instead of an image, that's the cause.

## How long until Google shows it?

Favicons appear next to your site in Google's mobile search results, but not instantly. Google crawls the favicon separately from the page and it can take days to weeks to appear. The requirements are simple: the file must be a square, must be reachable by Googlebot (not blocked in robots.txt), and should be a square whose size is a multiple of 48 pixels (48×48, 96×96 and so on), according to Google's favicon guidelines. The 48×48 version inside your ICO already meets that. If you're wondering whether it's working, check the mobile results specifically — desktop doesn't show favicons the same way.

## The whole process, start to finish

1. Design or pick a square graphic, at least 256×256, ideally vector. Simplify it until it reads at thumbnail size.
2. Generate a multi-size `favicon.ico` (16, 32, 48).
3. Export a 180×180 PNG as `apple-touch-icon.png`, and 192/512 PNGs if you want Android and PWA support.
4. Put them all in your site root.
5. Paste the three `<link>` lines into your `<head>`.
6. Check `yoursite.com/favicon.ico` loads directly, then test in a private window.

That's the whole job. If a generator hands you 27 files and a folder structure, you're being sold complexity you don't need.

:::tool favicon-generator|Make your favicon now — free, in your browser:::
