# Modern Delivery Architecture
### Distributed Systems & Clean Boundaries

Peter Suggitt
Engineering Fellow

Note:
Welcome everyone. Today we are walking through modular design and automated presentation pipelines.

---

## Architectural Objectives

- **Decoupled Workflows:** Independent lifecycle between content and presentation shells.
- **Dynamic Theming:** Switch presentation styles on the fly without touching markup.
- **Low Friction:** Plain Markdown authoring with zero compiler lock-in.
- **Fail-Fast Validation:** Pre-flight evaluation tests run against the deck.

Note:
Highlight why keeping slides.md discrete allows non-technical contributors to collaborate via Git.

---

## Dynamic Theme Selection

Pass the theme directly in the browser URL:

- `http://localhost:8000/?theme=black` (Default Dark)
- `http://localhost:8000/?theme=white` (Clean Light)
- `http://localhost:8000/?theme=dracula` (High Contrast)
- `http://localhost:8000/?theme=solarized` (Classic Muted)

--

### Exporting Themed PDFs

Append both `theme` and `print-pdf`:

```bash [1|2-4|5]
chromium --headless --disable-gpu \
  --print-to-pdf=presentation-white.pdf \
  --print-to-pdf-no-header \
  --enable-background-graphics \
  "http://localhost:8000/?theme=white&print-pdf"
```

Note:
Show how both flags compose cleanly together.
