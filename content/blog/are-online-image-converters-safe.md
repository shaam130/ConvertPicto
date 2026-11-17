---
title: Are Online Image Converters Safe? What Happens to Your Files
h1: Are online image converters safe? What actually happens to your files
description: Most online image converters upload your files to a server. Here's what that means, what their privacy policies actually say, how to tell the difference, and when it genuinely matters.
excerpt: Most converters upload your file to a server you know nothing about. Here's how to tell which ones do, and when it actually matters.
date: 2026-09-09
keyword: are online image converters safe
tools: png-to-jpg, compress-png, image-to-pdf
---

You have a scanned passport, a signed contract, or a photo of something private, and it needs to be a different format. You search "convert JPG to PDF", click the first result, drag the file in, and download the result.

Where did that file just go? Most people never ask. It's a reasonable question, and the answer is more interesting than "it's fine" or "never do that".

## Two completely different kinds of tool

Online image tools work in one of two ways, and they have almost nothing in common except the interface.

**Server-side tools** upload your file over the internet to a computer somewhere, run the conversion there, and send the result back. This is how the large majority of "online converters" work, including most of the well-known ones. It's the traditional approach: it lets them support formats browsers can't handle (HEIC, RAW, PSD, TIFF), run heavy processing, and work on any device regardless of how weak it is.

**Client-side tools** run entirely in your browser using JavaScript. The file is read from your disk into your browser's memory, processed by your own CPU, and handed back to you as a download. Nothing is transmitted anywhere. This is a newer approach, made practical by browser APIs like Canvas and WebAssembly, and it's limited to what browsers can decode and encode.

From the outside, both look identical: a drop zone, a button, a download. The difference is entirely invisible unless you go looking.

## What actually happens on the server side

It's worth being precise rather than alarmist, because "they steal your photos" is not usually what's going on.

When you upload to a reputable service, your file typically lands in temporary storage, gets processed, and is deleted on a schedule — commonly after a few hours. Most such services genuinely do delete. Their business model is ads or subscriptions, not your holiday photos.

But some things are true regardless of intent:

- **Your file existed on a machine you don't control**, in a jurisdiction you may not know, subject to laws you haven't read.
- **It passed through the network**, and while HTTPS protects it in transit, it's decrypted at the other end.
- **Deletion is a promise, not a mechanism.** You have no way to verify it happened. Backups, logs and caches routinely outlive the "deleted" original.
- **Breaches happen to careful companies.** If a service is compromised, whatever is in temporary storage at that moment is exposed.
- **Terms change, and companies get acquired.** The policy you agreed to isn't necessarily the policy that applies next year.

None of that is a reason to panic about converting a screenshot of a meme. It's a reason to think for two seconds about what's *in* the file.

## What the privacy policies actually say

If you read a few of these — and they're worth skimming once — you'll find recurring patterns.

Retention periods vary from "one hour" to "as long as necessary", which means nothing. Many policies grant a broad licence to "process, store and transmit" uploaded content, which is legally necessary to run the service but is written more broadly than it needs to be. Some reserve the right to scan uploads for prohibited content, which requires reading them. And most contain a clause allowing disclosure to comply with legal requests.

Again: these are normal clauses that normal companies need. The point isn't that they're sinister. The point is that if you assumed "I convert it and it disappears", the actual arrangement is more complicated than that.

## When it genuinely matters

Being proportionate about this is more useful than being paranoid. Here's roughly where the line sits.

**Probably fine to upload anywhere:** memes, stock photos, screenshots of public web pages, images you already published, anything you'd happily post publicly.

**Think first:** family photos, unreleased work, client material under NDA, product designs, anything with faces of people who didn't consent to it being on a stranger's server.

**Don't upload to a random converter:** identity documents (passports, ID cards, driving licences), financial documents, medical records or scans, signed contracts, anything containing other people's personal data, and anything covered by GDPR, HIPAA or a professional confidentiality duty.

That last category is the one that catches people out. "I'll just convert this scan of my passport to PDF" is an extremely common thing to do and one of the worst files to hand to an unknown service — it's the single most useful document for identity fraud.

If you work somewhere with a data protection policy, uploading client material to a third-party converter may also breach it. Many people do this without realising it counts as a data transfer.

## How to tell which kind of tool you're using

You don't have to take anyone's word for it. There are two reliable checks, and they take under a minute.

**The offline test.** Load the tool's page, then disconnect from the internet (turn off Wi-Fi, or enable airplane mode). Now try to convert a file. If it still works, the processing is happening on your device — it *cannot* be uploading anything. If it fails or hangs, it needs a server.

**The network tab.** Open your browser's developer tools (F12 or Ctrl+Shift+I), go to the **Network** tab, and convert a file. Watch what happens. A client-side tool shows no new requests. A server-side tool shows a POST request with a payload roughly the size of your file, and then a download coming back.

Neither test requires any technical knowledge beyond finding the menu. The offline one is the easier of the two and is genuinely conclusive.

:::note **This site passes both tests.** Every tool on ConvertPicto runs in your browser using the Canvas API. You can load a page, switch off your connection, and keep converting. There's no upload endpoint because there's no server that could receive one.:::

## The trade-offs of the browser-based approach

I build client-side tools, so it's only fair to be clear about what they can't do.

**Format support is narrower.** Browsers can decode PNG, JPG, WebP, GIF, BMP, AVIF, SVG and ICO, and encode PNG, JPG and WebP. They cannot decode HEIC (Apple's iPhone photo format), RAW camera files, PSD, TIFF or PDF page content without shipping heavy extra code. Server-side tools using ImageMagick or libvips handle all of those easily. If you need HEIC or RAW, you need a different kind of tool — and that's a legitimate reason to use one.

**Big files depend on your device.** Processing happens on your CPU, so a 100-megapixel image on an old phone will be slow, where a server would handle it instantly.

**Some operations are genuinely impractical** in a browser — heavy batch jobs, video, complex PDF manipulation.

What you get in exchange: nothing is uploaded, there's no queue, it works offline, and there's no file-size limit imposed by someone's bandwidth bill.

## A short checklist

Before you drop a file into any online tool:

1. Ask what's in it. Would you email this file to a stranger? If not, be careful.
2. Check whether the tool is client-side — the offline test takes thirty seconds.
3. If it's server-side and the file is sensitive, use desktop software instead. Preview on Mac, Paint or Photos on Windows, and GIMP everywhere all convert formats locally for free.
4. Be suspicious of tools that require an account to download the result. That's a data-collection pattern, not a technical necessity.
5. Watch for the ones that watermark unless you pay — the free tier is often the bait.

:::tool compress-png|Try a converter that doesn't upload:::

## The honest summary

Most online image converters are run by legitimate companies that delete your files roughly when they say they do. For most images, using them is genuinely fine.

But "fine for most images" isn't the same as "fine for every image", and the failure mode is asymmetric: the convenience you gain is a few seconds, and the thing you risk — with identity documents in particular — can take years to unwind. Since the alternative costs nothing, the sensible default is to use tools that don't upload at all, and save the server-based ones for the cases that genuinely need them.

The best part is that you don't have to trust anyone's claim about this. Turn off your Wi-Fi and see for yourself.
