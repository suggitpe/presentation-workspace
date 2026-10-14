# Test HTML Presentation
### Modern Standalone SPA Presentation Deck

Pete Suggitt &bull; Engineering Lead &bull; October 2026

<!-- badge: Email-Ready &bull; 100% Self-Contained -->

Note:
Welcome everyone. This presentation is fully self-contained inside a single HTML file—no external server, CDN, or build tools are required to view it. You can send it directly as an email attachment.

---

## Executive Summary

### Why a Standalone HTML Deck?

- **Zero Dependencies**: Everything (markup, styles, scripts, images) is bundled into one `.html` file.
- **Email Friendly**: Recipients can double-click and view immediately in any browser—even offline.
- **SPA Experience**: Seamless keyboard navigation, URL hash state, progress bar, and slide overview.
- **Markdown-Driven**: Maintain content in clean Markdown (`slides.md`) and compile with a single command.

> *"Simplicity is prerequisite for reliability."* &mdash; Edsger W. Dijkstra

Note:
Highlight that traditional HTML decks break when emailed because relative asset links and external CDNs fail under strict corporate email filters or offline access.

---

## The Workflow

```text
+---------------+         +---------------+         +---------------------+
|   slides.md   |  ====>  |   build.py    |  ====>  |  presentation.html  |
| (Edit Content)|         |  (Python CLI) |         | (Email Single File) |
+---------------+         +---------------+         +---------------------+
```

### 3 Simple Steps:
1. **Author**: Edit your slide material in `slides.md`.
2. **Compile**: Run `python build.py` to regenerate the standalone HTML.
3. **Distribute**: Attach `presentation.html` to an email or message.

Note:
The build script handles Markdown parsing, asset base64 inlining, and bundling in under one second.

---

## Feature Highlights

- **Instant Theme Switching**: Toggle between Clean Minimalist Light and Sleek Dark mode on the fly.
- **Overview Grid**: Press `O` or `Esc` to view a high-level thumbnail grid of all slides.
- **Keyboard Shortcuts**: Complete control via arrow keys, Space, Home, End, and Fullscreen (`F`).
- **Deep Linking**: Browser URL updates with `#slide-N` so you can link directly to specific slides.
- **Speaker Notes**: Press `S` to reveal private speaker notes.
- **Responsive Layout**: Designed for 16:9 projection as well as laptops, tablets, and phones.

Note:
Demonstrate the theme toggle and overview grid shortcuts to show the SPA capabilities.

---

## Key Performance Indicators

| Metric | Traditional Slides | Standalone SPA Deck | Advantage |
| :--- | :--- | :--- | :--- |
| **Asset Files** | 10+ files / assets | **1 single file** | Zero broken links |
| **Email Delivery** | Often blocked (ZIP) | **Standard `.html`** | Instant access |
| **Offline Support** | Partial (needs CDN) | **100% Offline** | Works anywhere |
| **Edit Speed** | Heavy GUI editor | **Plain Markdown** | Fast & versionable |

Note:
Compare the operational friction of sharing a folder of assets vs a single file.

---

## Sample Code Integration

Clean code blocks with syntax highlighting and easy reading:

```python
# build.py - Compile Markdown into self-contained HTML
from pathlib import Path
from parser import compile_presentation

def main():
    slides_md = Path("slides.md").read_text(encoding="utf-8")
    standalone_html = compile_presentation(slides_md)
    Path("presentation.html").write_text(standalone_html, encoding="utf-8")
    print("Deck compiled successfully into a single emailable HTML file!")

if __name__ == "__main__":
    main()
```

Note:
Code blocks are formatted with monospace typography, background contrast, and automatic scrolling if needed.

---

## Navigation & Controls Cheat Sheet

| Key / Action | Function |
| :--- | :--- |
| `Right Arrow` / `Space` / `Page Down` | Next slide |
| `Left Arrow` / `Backspace` / `Page Up` | Previous slide |
| `Home` / `End` | Jump to first / last slide |
| `O` or `Esc` | Toggle Slide Overview Grid |
| `T` | Toggle Dark / Light Theme |
| `S` | Toggle Speaker Notes Drawer |
| `F` | Toggle Fullscreen Mode |
| `?` | Show Navigation Help Modal |

Note:
Touch swipes on mobile or tablets are also natively supported.

---

## Next Steps & Action Items

- [x] Create seed `slides.md` content and documentation.
- [x] Build standalone zero-dependency Python compiler (`build.py`).
- [x] Implement SPA slide runner with theme switcher and overview modal.
- [ ] Add your custom presentation topics and slides to `slides.md`.
- [ ] Run `python build.py` and email `presentation.html` to your team!

> **Ready to deliver real impact!**

Note:
Wrap up the deck and open the floor for questions.
