---
title: Example Post — How the Blog System Works
h1: Example post: how the blog system works
description: A sample article showing every feature the built-in Markdown renderer supports — front matter, headings, tables, code blocks, tool call-outs and notes.
excerpt: A sample article demonstrating the front matter fields and custom blocks the renderer supports.
date: 2026-01-01
keyword: example post
tools: png-to-jpg, compress-png
---

This file is a working example of the blog format. Drop a `.md` file into `content/blog/`, run `python3 build.py`, and it becomes a full article page with schema markup, a table of contents, breadcrumbs and internal links to your tools.

The renderer lives in `src/blog.py`. It is about 200 lines and has no dependencies — no `markdown`, no `mistune`, nothing to install.

## Front matter

Every article starts with a YAML-ish block between `---` fences:

| Key | Required | What it does |
|---|---|---|
| `title` | yes | The `<title>` tag and the browser tab text |
| `h1` | yes | The on-page heading, usually phrased differently from the title |
| `description` | yes | The meta description and Open Graph description |
| `excerpt` | yes | The summary shown on the blog index card |
| `date` | yes | Publication date, `YYYY-MM-DD` |
| `keyword` | no | The primary target keyword, used in the JSON-LD |
| `tools` | no | Comma-separated tool slugs to link in the related section |
| `slug` | no | Overrides the filename-derived URL |

## Headings and the table of contents

Every `##` heading gets an automatic `id` and appears in the sidebar table of contents. `###` headings render normally but stay out of the contents list, so use them freely for sub-points.

### A third-level heading

Nested content works as you would expect.

## Text formatting

The usual Markdown applies: **bold**, *italic*, `inline code`, and [links](https://example.com). Lists work too:

- Unordered items
- With as many entries as you like

1. Ordered items
2. Numbered automatically

> Blockquotes render as a styled callout with a left border.

## Code blocks

Fenced blocks are escaped and styled, and scroll horizontally on narrow screens rather than breaking the layout:

```javascript
function encodeCanvas(canvas, mime, quality) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      // toBlob silently falls back to PNG for unsupported types,
      // so the resulting blob's type must be verified.
      if (blob && blob.type === mime) resolve(blob);
      else reject(new Error("Unsupported output format"));
    }, mime, quality);
  });
}
```

## Custom blocks

Two non-standard blocks are available beyond ordinary Markdown.

A **tool call-out** renders an inline card linking to one of your tool pages. The syntax is a tool slug, optionally followed by a pipe and custom label:

:::tool png-to-jpg|Convert PNG to JPG:::

A **note** renders a highlighted aside, useful for the one thing a reader should take away:

:::note **Order matters.** Resize first, then compress. Compressing before resizing throws away most of the work, because the resize discards those pixels anyway.:::

## Tables

Tables are wrapped in a scrolling container so they stay usable on phones:

| Format | Lossy | Transparency | Best for |
|---|---|---|---|
| JPG | yes | no | Photographs |
| PNG | no | yes | Graphics, logos, screenshots |
| WebP | both | yes | Almost everything on the web |
| AVIF | both | yes | Maximum compression |

## Writing a real article

Replace this file with your own. A few things that matter more than the formatting:

**Answer the question in the first paragraph.** Readers arriving from search want the answer, not a preamble about how images have become important in modern web design.

**Link to the tools where they are genuinely useful,** not every second paragraph. Two or three well-placed call-outs beat eight.

**Aim for 1,000–1,500 words.** Long enough to cover the topic properly, short enough to finish.

:::tool compress-png|Try a tool:::

## Build it

```bash
python3 build.py
```

The article appears at `/blog/<filename>/`, is added to the blog index, and is included in `sitemap.xml` automatically.
