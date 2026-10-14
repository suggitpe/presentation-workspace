---
name: revealjs-presentation-builder
description: Author, maintain, and evaluate modular reveal.js presentations with discrete Markdown content, dynamic themes, pre-flight evals, and reliable PDF exports in this repository.
---

# Reveal.js Presentation Builder

Use this skill when asked to create, update, or evaluate presentation decks in this repository.

## Principles

1. **Content Isolation:** Slide copy belongs exclusively in `slides.md`. Do not place raw Reveal container wrappers (`<div class="reveal">`) or scripts in `slides.md`.
2. **Untouched Runner:** `index.html` is the presentation harness and should remain decoupled from presentation copy.
3. **No Overflow:** Keep each slide under 6 bullet points and 160 words to avoid vertical clipping when rendered or exported to PDF.

## Presentation Creation Workflow

When instructed to create a new deck named `<slug>`:
1. Create `decks/<slug>/`.
2. Copy `templates/index.html` into `decks/<slug>/index.html`.
3. Draft slide content into `decks/<slug>/slides.md` using `---` (horizontal slides), `--` (vertical sub-slides), and `Note:` (speaker notes).
4. Create `decks/<slug>/export.sh` pointing to `.antigravity/skills/revealjs-presentation-builder/scripts/export-pdf.sh`.
5. Execute `evals/run_evals.py decks/<slug>/slides.md` to ensure layout density and slide boundaries are compliant.
