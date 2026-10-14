---
name: standalone-spa-presentation-builder
description: Author, build, and maintain self-contained, single-file HTML SPA presentation decks from Markdown for email distribution and offline presenting in this repository.
---

# Standalone SPA Presentation Builder

Use this skill when asked to create, update, or compile single-file, email-ready HTML slide decks in this repository.

## Core Principles

1. **100% Self-Contained:** The compiled `presentation.html` MUST have zero external runtime dependencies. No external CDNs (JS/CSS), no external fonts, no external icons, and zero CORS `fetch()` calls. All styling, SVG icons, scripts, and local images (via base64 data URIs) must be inlined into the single `.html` output file so it can be emailed and opened directly via `file:///` in any browser.
2. **Markdown-Driven Content:** Slide content belongs exclusively in `slides.md`. Presenters edit plain Markdown; they never need to manually edit HTML wrappers.
3. **SPA User Experience:** Decks must behave like a polished Single Page Application:
   - Smooth slide transitions
   - Real-time progress bar along the top edge
   - Reactive URL hash routing (`#slide-1`, `#slide-2`)
   - Overview thumbnail grid (`O` or `Esc`)
   - Slide counter pill (`01 / 08`)
   - Speaker notes drawer (`S`)
   - Built-in theme switching (`T`): Clean Minimalist Light (Paper & Charcoal default) and Sleek Dark (Charcoal & Electric Sky)
   - Fullscreen mode (`F`)
   - Full keyboard navigation and touch/swipe support
4. **Email & File Safety:** Keep final HTML file sizes optimized (< 5 MB recommended for email attachments). Compress or resize local images before inlining.

---

## Directory Structure for Decks

Each standalone presentation deck lives under `decks/<slug>/`:

```text
decks/<slug>/
├── slides.md               # Primary slide copy & speaker notes in Markdown
├── build.py                # Standalone compiler (standard library Python 3)
├── build.ps1               # PowerShell build shortcut
├── build.sh                # Bash build shortcut
├── README.md               # Deck overview and shortcut cheatsheet
├── images/                 # Local assets (automatically inlined as base64)
├── presentation.html       # Single-file HTML output (for emailing & distribution)
└── index.html              # Copy of presentation.html (for local web server/preview)
```

---

## Slide Authoring Guidelines (`slides.md`)

- **Slide Separators:** Use `---` on its own line to create horizontal slides.
- **Titles & Headings:** Use `#` for presentation title, `##` for slide titles, `###` for section/subheadings.
- **Badges:** Use `<!-- badge: Text -->` to render a pill badge at the top of a slide.
- **Speaker Notes:** End slide content with `Note:` followed by speaker notes. These will be hidden from the presentation canvas and displayed in the collapsible notes drawer (`S`).
- **Images:** Use standard markdown `![Alt text](images/diagram.png)`. During build, `build.py` automatically detects local image files and converts them into inline `data:image/...;base64` URIs.
- **Tables:** Use standard markdown table syntax `| Col 1 | Col 2 |`.
- **Code Blocks:** Use triple backticks with optional language identifier (```` ```python ... ``` ````).
- **Checklists:** Use `- [x]` for completed tasks and `- [ ]` for pending tasks.

---

## Deck Creation Workflow

When instructed to create a new standalone deck named `<slug>`:

1. **Scaffold the Deck:**
   Create `decks/<slug>/` and populate:
   - `decks/<slug>/slides.md` using `.antigravity/skills/standalone-spa-presentation-builder/templates/slides.md`
   - `decks/<slug>/build.py` copied from `.antigravity/skills/standalone-spa-presentation-builder/templates/build.py`
   - `decks/<slug>/build.ps1` and `decks/<slug>/build.sh`
   - `decks/<slug>/README.md`
   - `decks/<slug>/images/` directory
2. **Draft Slide Content:**
   Write the presentation copy into `decks/<slug>/slides.md`.
3. **Compile:**
   Execute:
   ```powershell
   python "decks/<slug>/build.py"
   ```
4. **Validate:**
   Run pre-flight evaluations to ensure the generated file is valid, self-contained, and within email size limits:
   ```powershell
   python ".antigravity/skills/standalone-spa-presentation-builder/evals/run_evals.py" "decks/<slug>/presentation.html"
   ```
5. **Update Repository Hub:**
   Add a presentation card for `<slug>` into the root `index.html`.
