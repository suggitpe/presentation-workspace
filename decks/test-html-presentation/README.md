# Test HTML Presentation (Standalone SPA Deck)

A self-contained, single-file HTML presentation built for distributing over email or presenting offline.

## Key Features

- **100% Self-Contained**: Everything (HTML, CSS, JavaScript runtime, SVG icons, and local images) is inlined into a single file (`presentation.html`).
- **Email-Ready**: Safe to attach directly to emails. Recipients can double-click and open it in any browser with zero CORS errors, missing files, or external CDN blocks.
- **Single Page Application Experience**:
  - Smooth slide transitions
  - Top edge progress bar
  - Slide counter and deep linking (`#slide-1`, `#slide-2`)
  - Overview grid modal (`O` or `Esc`)
  - Speaker notes drawer (`S`)
  - Clean Minimalist Light default theme (Paper & Charcoal) with instant Dark mode toggle (`T`)
  - Fullscreen mode (`F`)
  - Touch and swipe gesture support for mobile/tablets
- **Markdown Workflow**: Keep all slide content in `slides.md` and rebuild with one command.

## Workflow

1. **Edit Slides**: Open and update `slides.md`. Slides are separated by `---` and speaker notes by `Note:`.
2. **Compile**:
   - In PowerShell: `.\decks\test-html-presentation\build.ps1`
   - Or Python: `python decks/test-html-presentation/build.py`
3. **Send**: Attach `decks/test-html-presentation/presentation.html` to an email!

## Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Right Arrow` / `Space` / `Page Down` / `L` | Next slide |
| `Left Arrow` / `Backspace` / `Page Up` / `H` | Previous slide |
| `Home` / `End` | Jump to first / last slide |
| `O` or `Esc` | Toggle slide overview grid |
| `T` | Toggle Clean Light / Dark Charcoal theme |
| `S` | Toggle speaker notes drawer |
| `F` | Toggle fullscreen mode |
| `?` | Show navigation shortcuts help modal |

## Including Local Images

Any local image placed in `images/` and referenced in Markdown:
```markdown
![Architecture Diagram](images/architecture.png)
```
will be automatically converted into a base64 data URI during build, ensuring the output HTML remains completely standalone and portable.
