#!/usr/bin/env python3
"""
Single-File Standalone SPA Slide Deck Generator
Compiles Markdown (slides.md) into a 100% self-contained, emailable HTML presentation.
Zero external dependencies - uses standard Python 3 libraries only.
"""

import sys
import os
import re
import html
import base64
import mimetypes
from pathlib import Path


def inline_image(match, base_dir: Path) -> str:
    """Replaces markdown image ![alt](path) with inlined base64 data URI if file exists locally."""
    alt = match.group(1)
    src = match.group(2).strip()

    # If it's already a data URI or external URL, keep as is
    if src.startswith("data:") or src.startswith("http://") or src.startswith("https://"):
        return f'<img src="{src}" alt="{html.escape(alt)}" class="slide-image" />'

    img_path = (base_dir / src).resolve()
    if img_path.is_file():
        mime_type, _ = mimetypes.guess_type(str(img_path))
        if not mime_type:
            mime_type = "image/png"
        encoded = base64.b64encode(img_path.read_bytes()).decode("ascii")
        data_uri = f"data:{mime_type};base64,{encoded}"
        return f'<img src="{data_uri}" alt="{html.escape(alt)}" class="slide-image" />'
    
    # If not found, output standard img tag
    return f'<img src="{src}" alt="{html.escape(alt)}" class="slide-image" />'


def render_markdown_chunk(text: str, base_dir: Path) -> str:
    """Parses markdown text into semantic HTML elements."""
    lines = text.split("\n")
    out = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_ul = False
    in_ol = False
    in_table = False
    table_lines = []

    def close_lists():
        nonlocal in_ul, in_ol
        res = []
        if in_ul:
            res.append("</ul>")
            in_ul = False
        if in_ol:
            res.append("</ol>")
            in_ol = False
        return res

    def flush_table():
        nonlocal in_table, table_lines
        if not table_lines:
            return []
        res = ["<div class=\"table-container\"><table>"]
        header_processed = False
        for idx, row in enumerate(table_lines):
            cols = [c.strip() for c in row.strip().strip("|").split("|")]
            # Check if this is the separator row like |:---|---:|
            if idx == 1 and all(re.match(r"^:?-+:?$", c) for c in cols if c):
                continue
            if not header_processed:
                res.append("<thead><tr>" + "".join(f"<th>{render_inline(c, base_dir)}</th>" for c in cols) + "</tr></thead><tbody>")
                header_processed = True
            else:
                res.append("<tr>" + "".join(f"<td>{render_inline(c, base_dir)}</td>" for c in cols) + "</tr>")
        if header_processed:
            res.append("</tbody>")
        res.append("</table></div>")
        table_lines = []
        in_table = False
        return res

    for line in lines:
        stripped = line.strip()

        # Fenced code block handling
        if stripped.startswith("```"):
            if in_code_block:
                code_content = html.escape("\n".join(code_lines))
                lang_attr = f' class="language-{code_lang}"' if code_lang else ""
                out.append(f'<pre><code{lang_attr}>{code_content}</code></pre>')
                code_lines = []
                in_code_block = False
                code_lang = ""
            else:
                out.extend(close_lists())
                out.extend(flush_table())
                in_code_block = True
                code_lang = stripped[3:].strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Table detection
        if stripped.startswith("|") and stripped.endswith("|"):
            out.extend(close_lists())
            in_table = True
            table_lines.append(stripped)
            continue
        elif in_table:
            out.extend(flush_table())

        # Empty line
        if not stripped:
            out.extend(close_lists())
            continue

        # Badges comment: <!-- badge: ... -->
        badge_match = re.match(r"^<!--\s*badge:\s*(.*?)\s*-->$", stripped, re.IGNORECASE)
        if badge_match:
            out.extend(close_lists())
            out.append(f'<div class="badge">{badge_match.group(1)}</div>')
            continue

        # Headings
        if stripped.startswith("#"):
            out.extend(close_lists())
            level = len(stripped) - len(stripped.lstrip("#"))
            level = min(max(level, 1), 6)
            heading_text = render_inline(stripped[level:].strip(), base_dir)
            out.append(f'<h{level}>{heading_text}</h{level}>')
            continue

        # Blockquote
        if stripped.startswith(">"):
            out.extend(close_lists())
            quote_text = render_inline(stripped.lstrip(">").strip(), base_dir)
            out.append(f'<blockquote><p>{quote_text}</p></blockquote>')
            continue

        # Bullet List (- or *)
        bullet_match = re.match(r"^[-*+]\s+(.*)$", stripped)
        if bullet_match:
            item_text = bullet_match.group(1)
            # Checkbox items
            if item_text.startswith("[x] ") or item_text.startswith("[X] "):
                item_text = '<span class="checkbox checked">&#10003;</span> ' + item_text[4:]
            elif item_text.startswith("[ ] "):
                item_text = '<span class="checkbox unchecked">&#9633;</span> ' + item_text[4:]
            
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f'<li>{render_inline(item_text, base_dir)}</li>')
            continue

        # Ordered List (1. )
        num_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if num_match:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f'<li>{render_inline(num_match.group(1), base_dir)}</li>')
            continue

        # Fallback to paragraph
        out.extend(close_lists())
        out.append(f'<p>{render_inline(stripped, base_dir)}</p>')

    if in_code_block:
        code_content = html.escape("\n".join(code_lines))
        out.append(f'<pre><code>{code_content}</code></pre>')

    out.extend(close_lists())
    out.extend(flush_table())
    return "\n".join(out)


def render_inline(text: str, base_dir: Path) -> str:
    """Processes inline markdown elements (bold, italic, code, links, images)."""
    # Images: ![alt](url)
    text = re.sub(r"!\[(.*?)\]\((.*?)\)", lambda m: inline_image(m, base_dir), text)

    # Inline code: `code`
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", text)

    # Links: [text](url)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)

    # Bold: **text** or __text__
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.*?)__", r"<strong>\1</strong>", text)

    # Italic: *text* or _text_
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(.*?)_(?!\w)", r"<em>\1</em>", text)

    # Strikethrough: ~~text~~
    text = re.sub(r"~~(.*?)~~", r"<del>\1</del>", text)

    return text


def parse_slides(md_content: str, base_dir: Path):
    """Splits markdown into individual slide dictionaries with content, notes, and titles."""
    # Split on horizontal slide separator: \n---\n
    raw_slides = re.split(r"(?:^|\n)---\s*(?:\n|$)", md_content.strip())
    slides = []

    for idx, raw in enumerate(raw_slides):
        raw = raw.strip()
        if not raw:
            continue

        # Split speaker notes
        notes = ""
        notes_match = re.search(r"(?:^|\n)Note:\s*\n(.*)$", raw, re.DOTALL | re.IGNORECASE)
        if notes_match:
            notes = notes_match.group(1).strip()
            slide_body = raw[:notes_match.start()].strip()
        else:
            slide_body = raw

        # Extract title (first H1 or H2)
        title = f"Slide {idx + 1}"
        for line in slide_body.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                clean_title = re.sub(r"^#+\s*", "", line).strip()
                clean_title = re.sub(r"<!--.*?-->", "", clean_title).strip()
                if clean_title:
                    title = clean_title
                    break

        html_content = render_markdown_chunk(slide_body, base_dir)
        html_notes = render_markdown_chunk(notes, base_dir) if notes else ""

        slides.append({
            "index": len(slides) + 1,
            "title": title,
            "html": html_content,
            "notes": html_notes,
            "has_notes": bool(notes)
        })

    return slides


def generate_spa_html(slides, deck_title="Presentation") -> str:
    """Generates the single-file self-contained HTML presentation."""
    total_slides = len(slides)
    slides_html_list = []
    overview_cards_list = []

    for s in slides:
        idx = s["index"]
        title_escaped = html.escape(s["title"])
        notes_section = ""
        if s["has_notes"]:
            notes_section = f'<div class="slide-notes-content" style="display:none;">{s["notes"]}</div>'

        slides_html_list.append(f"""
        <!-- Slide {idx} -->
        <section class="slide" id="slide-{idx}" data-slide-index="{idx}" aria-label="Slide {idx}: {title_escaped}">
          <div class="slide-inner">
            {s["html"]}
            {notes_section}
          </div>
        </section>
        """)

        overview_cards_list.append(f"""
        <div class="overview-card" data-target-slide="{idx}" tabindex="0" role="button" aria-label="Go to slide {idx}: {title_escaped}">
          <div class="overview-num">{idx:02d}</div>
          <div class="overview-title">{title_escaped}</div>
        </div>
        """)

    slides_rendered = "\n".join(slides_html_list)
    overview_cards_rendered = "\n".join(overview_cards_list)

    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(deck_title)}</title>
  <style>
    :root {{
      /* Clean Minimalist Light (Paper & Charcoal) */
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --card-border: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-subtle: #94a3b8;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-subtle: #eff6ff;
      --code-bg: #1e293b;
      --code-text: #f8fafc;
      --tag-bg: #f1f5f9;
      --tag-text: #475569;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
      --shadow-md: 0 10px 25px -5px rgba(0,0,0,0.06), 0 8px 10px -6px rgba(0,0,0,0.04);
      --shadow-lg: 0 20px 40px -15px rgba(0,0,0,0.08);
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    }}

    [data-theme="dark"] {{
      /* Sleek Charcoal Dark (Charcoal & Electric Sky) */
      --bg: #090d16;
      --card-bg: #131b2e;
      --card-border: #22304d;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-subtle: #64748b;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --accent-subtle: rgba(56, 189, 248, 0.12);
      --code-bg: #0b1120;
      --code-text: #e2e8f0;
      --tag-bg: #1e293b;
      --tag-text: #94a3b8;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
      --shadow-md: 0 10px 25px -5px rgba(0,0,0,0.4);
      --shadow-lg: 0 20px 40px -15px rgba(0,0,0,0.5);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text-main);
      height: 100vh;
      width: 100vw;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      user-select: text;
      transition: background-color 0.25s ease, color 0.25s ease;
    }}

    /* Top Progress Bar */
    #progress-bar-container {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 4px;
      background: rgba(0, 0, 0, 0.05);
      z-index: 100;
    }}
    #progress-bar {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent), #38bdf8);
      transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* Top Header Bar */
    header.deck-header {{
      height: 54px;
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--card-border);
      background: var(--card-bg);
      z-index: 50;
      flex-shrink: 0;
    }}
    .header-left {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 600;
      font-size: 0.95rem;
      letter-spacing: -0.01em;
    }}
    .deck-badge {{
      background: var(--tag-bg);
      color: var(--tag-text);
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 6px;
      letter-spacing: 0.05em;
    }}
    .header-center {{
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.02em;
    }}
    .header-right {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .icon-btn {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      border-radius: 8px;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .icon-btn:hover {{
      background: var(--accent-subtle);
      color: var(--accent);
      border-color: var(--card-border);
    }}
    .icon-btn svg {{
      width: 18px;
      height: 18px;
      fill: none;
      stroke: currentColor;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}

    /* Main Presentation Viewport */
    main#deck-viewport {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px 32px 72px 32px;
      position: relative;
      overflow: hidden;
    }}

    /* Slide Box */
    .slide {{
      display: none;
      opacity: 0;
      transform: scale(0.985);
      transition: opacity 0.22s ease, transform 0.22s ease;
      width: 100%;
      max-width: 1120px;
      max-height: 85vh;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      box-shadow: var(--shadow-lg);
      overflow-y: auto;
      padding: 48px 56px;
    }}
    .slide.active {{
      display: flex;
      flex-direction: column;
      justify-content: center;
      opacity: 1;
      transform: scale(1);
    }}

    /* Slide Typography & Content */
    .slide-inner {{
      width: 100%;
    }}
    .slide h1 {{
      font-size: 2.75rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.15;
      margin-bottom: 16px;
      color: var(--text-main);
    }}
    .slide h2 {{
      font-size: 2.1rem;
      font-weight: 750;
      letter-spacing: -0.025em;
      line-height: 1.25;
      margin-bottom: 20px;
      color: var(--text-main);
      border-bottom: 2px solid var(--accent-subtle);
      padding-bottom: 8px;
    }}
    .slide h3 {{
      font-size: 1.45rem;
      font-weight: 650;
      line-height: 1.35;
      margin-top: 18px;
      margin-bottom: 12px;
      color: var(--text-muted);
    }}
    .slide h4, .slide h5, .slide h6 {{
      font-size: 1.15rem;
      font-weight: 600;
      margin-top: 14px;
      margin-bottom: 8px;
    }}
    .slide p {{
      font-size: 1.15rem;
      line-height: 1.65;
      color: var(--text-main);
      margin-bottom: 16px;
    }}
    .slide p:last-child {{
      margin-bottom: 0;
    }}
    .slide strong {{
      font-weight: 700;
      color: var(--text-main);
    }}
    .slide em {{
      font-style: italic;
    }}

    .badge {{
      display: inline-block;
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      background: var(--accent-subtle);
      color: var(--accent);
      padding: 4px 12px;
      border-radius: 9999px;
      margin-bottom: 20px;
    }}

    /* Lists */
    .slide ul, .slide ol {{
      font-size: 1.15rem;
      line-height: 1.7;
      margin: 16px 0 20px 24px;
      color: var(--text-main);
    }}
    .slide li {{
      margin-bottom: 8px;
    }}
    .slide li::marker {{
      color: var(--accent);
    }}
    .checkbox.checked {{
      color: #10b981;
      font-weight: bold;
      margin-right: 6px;
    }}
    .checkbox.unchecked {{
      color: var(--text-muted);
      margin-right: 6px;
    }}

    /* Blockquote */
    .slide blockquote {{
      border-left: 4px solid var(--accent);
      background: var(--accent-subtle);
      padding: 18px 24px;
      border-radius: 0 12px 12px 0;
      margin: 20px 0;
      font-style: italic;
      color: var(--text-main);
      font-size: 1.15rem;
    }}

    /* Code Blocks */
    .slide pre {{
      background: var(--code-bg);
      color: var(--code-text);
      font-family: var(--font-mono);
      font-size: 0.95rem;
      line-height: 1.5;
      padding: 20px;
      border-radius: 12px;
      overflow-x: auto;
      margin: 20px 0;
      border: 1px solid var(--card-border);
    }}
    .slide code {{
      font-family: var(--font-mono);
      font-size: 0.92em;
      background: var(--tag-bg);
      color: var(--accent);
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .slide pre code {{
      background: transparent;
      color: inherit;
      padding: 0;
    }}

    /* Tables */
    .table-container {{
      width: 100%;
      overflow-x: auto;
      margin: 20px 0;
      border-radius: 10px;
      border: 1px solid var(--card-border);
    }}
    .slide table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 1.05rem;
    }}
    .slide th {{
      background: var(--tag-bg);
      color: var(--text-main);
      font-weight: 700;
      padding: 12px 16px;
      border-bottom: 2px solid var(--card-border);
    }}
    .slide td {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--card-border);
      color: var(--text-main);
    }}
    .slide tr:last-child td {{
      border-bottom: none;
    }}

    /* Images */
    .slide-image {{
      max-width: 100%;
      max-height: 480px;
      border-radius: 10px;
      object-fit: contain;
      display: block;
      margin: 16px auto;
      border: 1px solid var(--card-border);
    }}

    /* Floating Navigation Controls */
    #nav-controls {{
      position: fixed;
      bottom: 20px;
      right: 28px;
      display: flex;
      align-items: center;
      gap: 10px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      padding: 6px 14px;
      border-radius: 9999px;
      box-shadow: var(--shadow-md);
      z-index: 60;
    }}
    .nav-btn {{
      background: var(--tag-bg);
      border: 1px solid var(--card-border);
      color: var(--text-main);
      padding: 7px 14px;
      border-radius: 9999px;
      font-weight: 600;
      font-size: 0.85rem;
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .nav-btn:hover:not(:disabled) {{
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
    }}
    .nav-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}
    .slide-indicator-pill {{
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-muted);
      padding: 0 6px;
    }}

    /* Speaker Notes Drawer */
    #notes-drawer {{
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      max-height: 240px;
      background: var(--card-bg);
      border-top: 2px solid var(--accent);
      box-shadow: 0 -10px 25px rgba(0,0,0,0.15);
      padding: 18px 32px;
      overflow-y: auto;
      z-index: 70;
      transform: translateY(100%);
      transition: transform 0.25s ease;
    }}
    #notes-drawer.open {{
      transform: translateY(0);
    }}
    .notes-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      font-weight: 700;
      font-size: 0.9rem;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    #notes-body {{
      font-size: 1rem;
      line-height: 1.6;
      color: var(--text-main);
    }}

    /* Overview Modal (Grid View) */
    #overview-modal {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(8px);
      z-index: 200;
      display: none;
      opacity: 0;
      transition: opacity 0.2s ease;
      padding: 48px;
      overflow-y: auto;
    }}
    #overview-modal.open {{
      display: flex;
      flex-direction: column;
      opacity: 1;
    }}
    .overview-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      color: #ffffff;
    }}
    .overview-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 20px;
      width: 100%;
    }}
    .overview-card {{
      background: var(--card-bg);
      border: 2px solid transparent;
      border-radius: 12px;
      padding: 20px;
      cursor: pointer;
      min-height: 130px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.15s ease;
      color: var(--text-main);
    }}
    .overview-card:hover, .overview-card:focus {{
      border-color: var(--accent);
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
      outline: none;
    }}
    .overview-card.active-card {{
      border-color: var(--accent);
      background: var(--accent-subtle);
    }}
    .overview-num {{
      font-size: 0.8rem;
      font-weight: 800;
      color: var(--accent);
    }}
    .overview-title {{
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.35;
      margin-top: 8px;
    }}

    /* Help Modal */
    #help-modal {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(6px);
      z-index: 210;
      display: none;
      align-items: center;
      justify-content: center;
    }}
    #help-modal.open {{
      display: flex;
    }}
    .help-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 32px;
      max-width: 520px;
      width: 90%;
      box-shadow: var(--shadow-lg);
    }}
    .help-card h3 {{
      font-size: 1.4rem;
      margin-bottom: 16px;
      color: var(--text-main);
    }}
    .shortcut-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid var(--card-border);
      font-size: 0.95rem;
    }}
    kbd {{
      background: var(--tag-bg);
      color: var(--text-main);
      padding: 2px 8px;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      border: 1px solid var(--card-border);
    }}

    @media (max-width: 768px) {{
      .slide {{
        padding: 24px 20px;
      }}
      .slide h1 {{ font-size: 2rem; }}
      .slide h2 {{ font-size: 1.6rem; }}
      header.deck-header {{ padding: 0 16px; }}
      #nav-controls {{ bottom: 12px; right: 12px; }}
    }}
  </style>
</head>
<body>
  <!-- Progress Bar -->
  <div id="progress-bar-container"><div id="progress-bar"></div></div>

  <!-- Top Header -->
  <header class="deck-header">
    <div class="header-left">
      <span class="deck-badge">SPA Deck</span>
      <span>{html.escape(deck_title)}</span>
    </div>
    <div class="header-center">
      <span id="slide-counter-top">01 / {total_slides:02d}</span>
    </div>
    <div class="header-right">
      <button class="icon-btn" id="btn-theme" title="Toggle Theme (T)" aria-label="Toggle Theme">
        <svg viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
      </button>
      <button class="icon-btn" id="btn-notes" title="Speaker Notes (S)" aria-label="Toggle Speaker Notes">
        <svg viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
      </button>
      <button class="icon-btn" id="btn-overview" title="Slide Overview Grid (O / Esc)" aria-label="Slide Overview">
        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
      </button>
      <button class="icon-btn" id="btn-fullscreen" title="Toggle Fullscreen (F)" aria-label="Fullscreen">
        <svg viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3m0 18h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3"></path></svg>
      </button>
      <button class="icon-btn" id="btn-help" title="Help & Shortcuts (?)" aria-label="Help">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3m.08 4h.01"></path></svg>
      </button>
    </div>
  </header>

  <!-- Viewport for Active Slide -->
  <main id="deck-viewport">
    {slides_rendered}
  </main>

  <!-- Floating Nav Controls -->
  <div id="nav-controls">
    <button class="nav-btn" id="btn-prev" aria-label="Previous Slide">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"></polyline></svg>
      <span>Prev</span>
    </button>
    <div class="slide-indicator-pill" id="slide-pill">01 / {total_slides:02d}</div>
    <button class="nav-btn" id="btn-next" aria-label="Next Slide">
      <span>Next</span>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
    </button>
  </div>

  <!-- Speaker Notes Drawer -->
  <div id="notes-drawer">
    <div class="notes-header">
      <span>Speaker Notes</span>
      <button class="icon-btn" id="btn-close-notes" style="width:28px;height:28px;" aria-label="Close Notes">
        <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
    <div id="notes-body">No notes for this slide.</div>
  </div>

  <!-- Overview Modal -->
  <div id="overview-modal" role="dialog" aria-modal="true" aria-label="Slide Overview">
    <div class="overview-header">
      <h2>Slide Overview ({total_slides} Slides)</h2>
      <button class="icon-btn" id="btn-close-overview" style="color:#ffffff;" aria-label="Close Overview">
        <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
    <div class="overview-grid">
      {overview_cards_rendered}
    </div>
  </div>

  <!-- Help Modal -->
  <div id="help-modal" role="dialog" aria-modal="true" aria-label="Navigation Shortcuts">
    <div class="help-card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h3>Keyboard Navigation</h3>
        <button class="icon-btn" id="btn-close-help" aria-label="Close Help">
          <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      <div class="shortcut-row"><span>Next Slide</span><div><kbd>&rarr;</kbd> <kbd>Space</kbd> <kbd>PageDown</kbd></div></div>
      <div class="shortcut-row"><span>Previous Slide</span><div><kbd>&larr;</kbd> <kbd>Backspace</kbd> <kbd>PageUp</kbd></div></div>
      <div class="shortcut-row"><span>First / Last Slide</span><div><kbd>Home</kbd> / <kbd>End</kbd></div></div>
      <div class="shortcut-row"><span>Slide Overview Grid</span><div><kbd>O</kbd> or <kbd>Esc</kbd></div></div>
      <div class="shortcut-row"><span>Toggle Theme</span><div><kbd>T</kbd></div></div>
      <div class="shortcut-row"><span>Toggle Speaker Notes</span><div><kbd>S</kbd></div></div>
      <div class="shortcut-row"><span>Toggle Fullscreen</span><div><kbd>F</kbd></div></div>
      <div class="shortcut-row"><span>Show this Help</span><div><kbd>?</kbd></div></div>
      <div style="margin-top:16px; font-size:0.85rem; color:var(--text-muted); text-align:center;">
        Touch swipes on mobile and tablets are also supported.
      </div>
    </div>
  </div>

  <!-- SPA Runtime Script -->
  <script>
    (function() {{
      'use strict';

      const totalSlides = {total_slides};
      let currentIndex = 0;
      const slides = Array.from(document.querySelectorAll('.slide'));
      const progressBar = document.getElementById('progress-bar');
      const counterTop = document.getElementById('slide-counter-top');
      const counterPill = document.getElementById('slide-pill');
      const btnPrev = document.getElementById('btn-prev');
      const btnNext = document.getElementById('btn-next');
      const overviewModal = document.getElementById('overview-modal');
      const helpModal = document.getElementById('help-modal');
      const notesDrawer = document.getElementById('notes-drawer');
      const notesBody = document.getElementById('notes-body');
      const overviewCards = Array.from(document.querySelectorAll('.overview-card'));

      function padZero(n) {{
        return n < 10 ? '0' + n : '' + n;
      }}

      function updateSlide(newIndex, updateHash = true) {{
        if (newIndex < 0) newIndex = 0;
        if (newIndex >= totalSlides) newIndex = totalSlides - 1;

        currentIndex = newIndex;

        // Slide activation
        slides.forEach((slide, idx) => {{
          if (idx === currentIndex) {{
            slide.classList.add('active');
          }} else {{
            slide.classList.remove('active');
          }}
        }});

        // Overview highlight
        overviewCards.forEach((card, idx) => {{
          if (idx === currentIndex) {{
            card.classList.add('active-card');
          }} else {{
            card.classList.remove('active-card');
          }}
        }});

        // Progress bar & counters
        const progressPct = totalSlides > 1 ? (currentIndex / (totalSlides - 1)) * 100 : 100;
        progressBar.style.width = progressPct + '%';

        const counterText = padZero(currentIndex + 1) + ' / ' + padZero(totalSlides);
        counterTop.textContent = counterText;
        counterPill.textContent = counterText;

        // Nav button states
        btnPrev.disabled = (currentIndex === 0);
        btnNext.disabled = (currentIndex === totalSlides - 1);

        // Update speaker notes
        const currentSlide = slides[currentIndex];
        const notesElem = currentSlide ? currentSlide.querySelector('.slide-notes-content') : null;
        if (notesElem && notesElem.innerHTML.trim()) {{
          notesBody.innerHTML = notesElem.innerHTML;
        }} else {{
          notesBody.innerHTML = '<em>No speaker notes for this slide.</em>';
        }}

        // Update URL hash for SPA routing
        if (updateHash) {{
          history.replaceState(null, '', '#slide-' + (currentIndex + 1));
        }}
      }}

      function nextSlide() {{
        if (currentIndex < totalSlides - 1) {{
          updateSlide(currentIndex + 1);
        }}
      }}

      function prevSlide() {{
        if (currentIndex > 0) {{
          updateSlide(currentIndex - 1);
        }}
      }}

      function toggleOverview() {{
        const isOpen = overviewModal.classList.toggle('open');
        if (isOpen) {{
          overviewCards[currentIndex].scrollIntoView({{ block: 'nearest' }});
          overviewCards[currentIndex].focus();
        }}
      }}

      function toggleHelp() {{
        helpModal.classList.toggle('open');
      }}

      function toggleNotes() {{
        notesDrawer.classList.toggle('open');
      }}

      function toggleTheme() {{
        const htmlElem = document.documentElement;
        const currentTheme = htmlElem.getAttribute('data-theme') || 'light';
        const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
        htmlElem.setAttribute('data-theme', nextTheme);
        try {{
          localStorage.setItem('spa_deck_theme', nextTheme);
        }} catch (e) {{}}
      }}

      function toggleFullscreen() {{
        if (!document.fullscreenElement) {{
          document.documentElement.requestFullscreen().catch(() => {{}});
        }} else {{
          if (document.exitFullscreen) {{
            document.exitFullscreen();
          }}
        }}
      }}

      // Init Theme from LocalStorage if set
      try {{
        const savedTheme = localStorage.getItem('spa_deck_theme');
        if (savedTheme) {{
          document.documentElement.setAttribute('data-theme', savedTheme);
        }}
      }} catch (e) {{}}

      // Button listeners
      btnPrev.addEventListener('click', prevSlide);
      btnNext.addEventListener('click', nextSlide);
      document.getElementById('btn-overview').addEventListener('click', toggleOverview);
      document.getElementById('btn-close-overview').addEventListener('click', toggleOverview);
      document.getElementById('btn-help').addEventListener('click', toggleHelp);
      document.getElementById('btn-close-help').addEventListener('click', toggleHelp);
      document.getElementById('btn-notes').addEventListener('click', toggleNotes);
      document.getElementById('btn-close-notes').addEventListener('click', toggleNotes);
      document.getElementById('btn-theme').addEventListener('click', toggleTheme);
      document.getElementById('btn-fullscreen').addEventListener('click', toggleFullscreen);

      overviewCards.forEach(card => {{
        card.addEventListener('click', () => {{
          const target = parseInt(card.getAttribute('data-target-slide'), 10) - 1;
          updateSlide(target);
          overviewModal.classList.remove('open');
        }});
        card.addEventListener('keydown', (e) => {{
          if (e.key === 'Enter' || e.key === ' ') {{
            e.preventDefault();
            const target = parseInt(card.getAttribute('data-target-slide'), 10) - 1;
            updateSlide(target);
            overviewModal.classList.remove('open');
          }}
        }});
      }});

      // Close modals on backdrop click
      overviewModal.addEventListener('click', (e) => {{
        if (e.target === overviewModal) overviewModal.classList.remove('open');
      }});
      helpModal.addEventListener('click', (e) => {{
        if (e.target === helpModal) helpModal.classList.remove('open');
      }});

      // Keyboard navigation
      window.addEventListener('keydown', (e) => {{
        // Don't capture keys if typing in an input
        if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

        if (helpModal.classList.contains('open')) {{
          if (e.key === 'Escape' || e.key === '?') {{
            helpModal.classList.remove('open');
            e.preventDefault();
          }}
          return;
        }}

        if (overviewModal.classList.contains('open')) {{
          if (e.key === 'Escape' || e.key === 'o' || e.key === 'O') {{
            overviewModal.classList.remove('open');
            e.preventDefault();
          }}
          return;
        }}

        switch (e.key) {{
          case 'ArrowRight':
          case ' ':
          case 'PageDown':
          case 'l':
          case 'j':
            e.preventDefault();
            nextSlide();
            break;
          case 'ArrowLeft':
          case 'Backspace':
          case 'PageUp':
          case 'h':
          case 'k':
            e.preventDefault();
            prevSlide();
            break;
          case 'Home':
            e.preventDefault();
            updateSlide(0);
            break;
          case 'End':
            e.preventDefault();
            updateSlide(totalSlides - 1);
            break;
          case 'o':
          case 'O':
          case 'Escape':
            e.preventDefault();
            toggleOverview();
            break;
          case 't':
          case 'T':
            e.preventDefault();
            toggleTheme();
            break;
          case 's':
          case 'S':
            e.preventDefault();
            toggleNotes();
            break;
          case 'f':
          case 'F':
            e.preventDefault();
            toggleFullscreen();
            break;
          case '?':
          case '/':
            e.preventDefault();
            toggleHelp();
            break;
        }}
      }});

      // Touch Swipe Support
      let touchStartX = 0;
      let touchStartY = 0;

      window.addEventListener('touchstart', (e) => {{
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
      }}, {{ passive: true }});

      window.addEventListener('touchend', (e) => {{
        const deltaX = e.changedTouches[0].screenX - touchStartX;
        const deltaY = e.changedTouches[0].screenY - touchStartY;
        // Check horizontal swipe if deltaX > deltaY
        if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY)) {{
          if (deltaX < 0) {{
            nextSlide();
          }} else {{
            prevSlide();
          }}
        }}
      }}, {{ passive: true }});

      // Parse Initial Hash
      function getSlideFromHash() {{
        const match = window.location.hash.match(/#slide-(\\d+)/);
        if (match) {{
          const num = parseInt(match[1], 10);
          if (!isNaN(num) && num >= 1 && num <= totalSlides) {{
            return num - 1;
          }}
        }}
        return 0;
      }}

      window.addEventListener('hashchange', () => {{
        const target = getSlideFromHash();
        if (target !== currentIndex) {{
          updateSlide(target, false);
        }}
      }});

      // Initial Mount
      updateSlide(getSlideFromHash(), false);
    }})();
  </script>
</body>
</html>
"""


def main():
    base_dir = Path(__file__).resolve().parent
    slides_path = base_dir / "slides.md"
    out_presentation = base_dir / "presentation.html"
    out_index = base_dir / "index.html"

    if len(sys.argv) > 1:
        slides_path = Path(sys.argv[1]).resolve()

    if not slides_path.exists():
        print(f"Error: Markdown source file not found at {slides_path}")
        sys.exit(1)

    print(f"Reading slides from: {slides_path.name}")
    md_content = slides_path.read_text(encoding="utf-8")

    # Extract deck title from first H1 if present
    deck_title = "Presentation"
    title_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if title_match:
        deck_title = title_match.group(1).strip()

    slides = parse_slides(md_content, base_dir)
    if not slides:
        print("Error: No slides found in markdown file.")
        sys.exit(1)

    print(f"Parsed {len(slides)} slides successfully.")
    html_output = generate_spa_html(slides, deck_title=deck_title)

    # Write presentation.html (the standalone emailable file)
    out_presentation.write_text(html_output, encoding="utf-8")
    # Also write index.html for direct local preview
    out_index.write_text(html_output, encoding="utf-8")

    file_size_kb = out_presentation.stat().st_size / 1024
    print(f"Generated standalone SPA presentation: {out_presentation.name} ({file_size_kb:.1f} KB)")
    print(f"100% self-contained: all markup, styles, scripts, and assets are inlined.")
    print(f"Ready to send via email: {out_presentation}")


if __name__ == "__main__":
    main()
