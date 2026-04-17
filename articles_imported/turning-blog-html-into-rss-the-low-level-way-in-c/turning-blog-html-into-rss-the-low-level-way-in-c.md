If you publish long-form posts on the web, you’ve probably felt the friction of keeping your RSS feed in sync. I did too. So I wrote a tiny command-line tool in C++ that converts a finished blog post page (the raw HTML file itself, not just the body) into a ready-to-drop `<item>` block for your RSS feed. Because yes—CLI is fun, and C++ is low-level, baby. 🛠️

## TL;DR

- **What it does:** Reads a full raw blog HTML page (not just the body) → emits a valid RSS `<item>` XML snippet.
- **Why it’s useful:** No separate markdown front matter or duplication. Your source of truth is the rendered page.
- **How to use:** `./a.out post.html rss.xml "My Title" "https://example.com/post" "2025-10-04"`
- **Where it lives:** [github.com/julienlargetpiet/automate\_rss](https://github.com/julienlargetpiet/automate_rss)

## The Problem

An RSS feed wants clean metadata and safe HTML inside `<description>` and/or `<content:encoded>`. Most blogs already produce a canonical HTML page. Duplicating metadata (title, dates, canonical URL, description, tags) across templates, markdown front-matter, and an RSS generator is fragile and error-prone.

**Goal:** parse the final HTML, extract only what we need, sanitize it, and output a single `<item>` you can paste into your feed file—or pipe into your generator.

## What the Tool Extracts

- **Title** (you pass it as an argument)
- **Link** (you pass it as an argument)
- **Date** (from argument or generated at runtime)
- **Content** (your entire HTML page, not just the body, properly escaped for XML safety — for example `<` → `&lt;`, `>` → `&gt;`, and if there’s any raw `&`, it must be converted into `&amp;`)

### Important: Ampersands in HTML

If your source HTML contains raw `&` (e.g., “A & B”), it _must_ be escaped to `&amp;` before it’s placed inside XML. Otherwise your RSS will break.

**Before:** `A & B`

**After (in RSS/XML):** `A &amp; B`

## Why C++?

I like low-level control. With C++ you handle strings, escaping, and file IO directly. Writing a simple CLI tool in C++ is lightweight and dependency-free, and frankly, fun.

## Example Usage

```bash

$ g++ -O3 automate_rss.cpp
$ ./a.out html_data.html rss_data.xml "My Blog Post" "https://example.com/post" "2025-10-04"

```

Your `rss_data.xml` should contain a `?` placeholder where you want the new `<item>` inserted.

### Minimal Example of the Inserted Item

```

<item>
<title>My Blog Post</title>
 <link>https://example.com/post</link>
<pubDate>Sat, 04 Oct 2025 12:00:00 GMT</pubDate>
<description>&lt;html&gt;...full page content escaped...&lt;/html&gt;</description>
</item>

```

## What’s Next

- Smarter HTML extraction (custom selectors).
- Optional support for `<content:encoded>` for full-content feeds.
- Date auto-detection from meta tags.
- Configurable insertion strategies beyond a single placeholder.

Check it out on GitHub: [julienlargetpiet/automate\_rss](https://github.com/julienlargetpiet/automate_rss)