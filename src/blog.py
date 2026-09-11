"""
Blog engine for ConvertPicto — a small, dependency-free Markdown renderer plus
page builders. Articles live in content/blog/*.md and are rendered into
dist/blog/<slug>.html with an index at dist/blog.html.

Front matter (between --- lines at the top of the file):
    title:        page <title> (SEO). Keep under ~60 chars.
    h1:           on-page heading (optional; defaults to title)
    description:  meta description, ~150-160 chars
    date:         YYYY-MM-DD
    updated:      YYYY-MM-DD (optional)
    keyword:      the primary phrase this article targets (used for internal notes)
    tools:        comma-separated tool slugs to show in "Try it" section
    excerpt:      short summary for the blog index card

Body supports: ## / ### headings, paragraphs, **bold**, *italic*, `code`,
[links](url), - and 1. lists, > quotes, ``` code blocks, | tables |, ---,
plus two custom blocks:
    :::tool png-to-jpg|Optional custom label:::      -> inline tool CTA card
    :::note Some text:::                             -> highlighted callout
"""
import html as _html
import re
from pathlib import Path

esc = _html.escape


# ---------------------------------------------------------------- front matter
def parse_front_matter(text):
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = text[end + 4:].lstrip("\n")
    return meta, body


# ---------------------------------------------------------------- inline md
def inline(s, esc_first=True):
    out = esc(s) if esc_first else s
    out = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                 lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


def slugify(s):
    s = re.sub(r"<[^>]+>", "", s).lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"\s+", "-", s.strip())[:60]


# ---------------------------------------------------------------- block md
def render_markdown(body, tool_card):
    """Returns (html, toc) where toc is a list of (id, text) for each H2."""
    lines = body.split("\n")
    out, toc = [], []
    i, n = 0, len(lines)

    def flush_para(buf):
        if buf:
            out.append("<p>" + inline(" ".join(buf).strip()) + "</p>")
            buf.clear()

    para = []
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # custom blocks -------------------------------------------------
        m = re.match(r":::tool\s+([a-z0-9\-]+)(?:\|(.+?))?:::", stripped)
        if m:
            flush_para(para)
            out.append(tool_card(m.group(1), m.group(2)))
            i += 1
            continue
        m = re.match(r":::note\s+(.+?):::$", stripped)
        if m:
            flush_para(para)
            out.append('<div class="callout">' + inline(m.group(1)) + "</div>")
            i += 1
            continue

        # code fence ----------------------------------------------------
        if stripped.startswith("```"):
            flush_para(para)
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + esc("\n".join(code)) + "</code></pre>")
            continue

        # headings ------------------------------------------------------
        if stripped.startswith("### "):
            flush_para(para)
            t = inline(stripped[4:])
            out.append(f'<h3 id="{slugify(t)}">{t}</h3>')
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para(para)
            t = inline(stripped[3:])
            sid = slugify(t)
            toc.append((sid, re.sub(r"<[^>]+>", "", t)))
            out.append(f'<h2 id="{sid}">{t}</h2>')
            i += 1
            continue

        # hr ------------------------------------------------------------
        if stripped in ("---", "***"):
            flush_para(para)
            out.append("<hr>")
            i += 1
            continue

        # table ---------------------------------------------------------
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            flush_para(para)
            head = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue

        # blockquote ----------------------------------------------------
        if stripped.startswith("> "):
            flush_para(para)
            q = []
            while i < n and lines[i].strip().startswith("> "):
                q.append(lines[i].strip()[2:])
                i += 1
            out.append("<blockquote>" + inline(" ".join(q)) + "</blockquote>")
            continue

        # lists ---------------------------------------------------------
        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            flush_para(para)
            ordered = bool(re.match(r"^\d+\.\s+", stripped))
            items = []
            while i < n:
                st = lines[i].strip()
                m2 = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", st)
                if not m2:
                    break
                text = m2.group(1)
                i += 1
                # continuation lines
                while i < n and lines[i].strip() and not re.match(r"^(?:[-*]|\d+\.)\s+", lines[i].strip()) \
                        and not lines[i].strip().startswith(("#", ">", "|", ":::", "```")):
                    text += " " + lines[i].strip()
                    i += 1
                items.append("<li>" + inline(text) + "</li>")
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        # paragraph / blank ---------------------------------------------
        if not stripped:
            flush_para(para)
        else:
            para.append(stripped)
        i += 1

    flush_para(para)
    return "\n".join(out), toc


def reading_time(body):
    words = len(re.sub(r"[^\w\s]", " ", re.sub(r"```.*?```", " ", body, flags=re.S)).split())
    return max(1, round(words / 225)), words


def load_articles(root: Path):
    """Reads content/blog/*.md, returns list of dicts sorted newest first."""
    d = root / "content" / "blog"
    arts = []
    if not d.exists():
        return arts
    for f in sorted(d.glob("*.md")):
        meta, body = parse_front_matter(f.read_text(encoding="utf-8"))
        mins, words = reading_time(body)
        arts.append({
            "slug": meta.get("slug", f.stem),
            "title": meta.get("title", f.stem),
            "h1": meta.get("h1", meta.get("title", f.stem)),
            "description": meta.get("description", ""),
            "excerpt": meta.get("excerpt", meta.get("description", "")),
            "date": meta.get("date", ""),
            "updated": meta.get("updated", ""),
            "keyword": meta.get("keyword", ""),
            "tools": [t.strip() for t in meta.get("tools", "").split(",") if t.strip()],
            "body": body,
            "minutes": mins,
            "words": words,
        })
    arts.sort(key=lambda a: a["date"], reverse=True)
    return arts
