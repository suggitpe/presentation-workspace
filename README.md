# Presentations Repository (Antigravity-Enabled)

A centralized presentation hub designed for creating and managing multiple Reveal.js slide decks using `agy`.

The presentation skill is defined locally at `.antigravity/skills/revealjs-presentation-builder/` so `agy` will automatically detect and trigger it within this repository workspace.

## Repository Layout

```text
.
├── .gitignore
├── README.md
├── .antigravity/
│   └── skills/
│       ├── revealjs-presentation-builder/       # Reveal.js presentation workflow
│       │   ├── SKILL.md
│       │   ├── evals/
│       │   ├── scripts/
│       │   └── templates/
│       └── standalone-spa-presentation-builder/ # Single-file emailable SPA presentation workflow
│           ├── SKILL.md                         # Skill definition & guidelines
│           ├── evals/
│           │   └── run_evals.py                 # Self-contained & size pre-flight assertions
│           ├── scripts/
│           │   └── new-deck.py                  # CLI deck scaffold script
│           └── templates/
│               ├── build.py                     # Standalone Python compiler engine
│               └── slides.md                    # Starter slide template
├── scripts/
│   └── new-presentation.sh                      # Reveal.js CLI scaffold script
├── decks/
│   ├── test-html-presentation/                  # Standalone SPA deck (emailable)
│   │   ├── slides.md                            # Pure Markdown slide content
│   │   ├── build.py                             # Compiler script
│   │   ├── build.ps1 / build.sh                 # Build shortcuts
│   │   ├── presentation.html                    # 100% self-contained output (email-ready)
│   │   └── README.md
│   ├── get-stuff-done/                          # "Get Stuff Done" by Pete Suggitt (Reveal.js)
│   └── modern-delivery/                         # Example Reveal.js deck
```

## Adding Presentations

### Using `agy`
Prompt `agy` directly within this repository:
> *"Create a new presentation in `decks/event-driven-architecture/` using the solarized theme."*

`agy` reads the local skill, sets up the deck structure in `decks/`, populates `slides.md`, and runs pre-flight density checks.

### Using the Scaffold Script
```bash
./scripts/new-presentation.sh event-driven-architecture solarized
```

## Running & Exporting a Deck

1. Navigate to the deck:
   ```bash
   cd decks/modern-delivery
   ```

2. Start the preview server:
   ```bash
   python3 -m http.server 8000
   ```
   Open `http://localhost:8000` (or `http://localhost:8000/?theme=dracula`).

3. Run assertions:
   ```bash
   python3 ../../.antigravity/skills/revealjs-presentation-builder/evals/run_evals.py slides.md
   ```

4. Export to PDF:
   ```bash
   ./export.sh
   ```

---

## Standalone SPA Presentations (Email-Ready)

For decks that need to be emailed as a single file with zero external dependencies and an SPA feel:

### 1. Scaffold a New Standalone Deck
```bash
python .antigravity/skills/standalone-spa-presentation-builder/scripts/new-deck.py my-new-deck "My New Presentation" "Presenter Name"
```

### 2. Edit & Compile
1. Edit slides in `decks/<slug>/slides.md`.
2. Compile to single-file HTML:
   ```bash
   python decks/<slug>/build.py
   # Or using PowerShell:
   .\decks\<slug>\build.ps1
   ```

### 3. Verify Self-Contained Evals
```bash
python .antigravity/skills/standalone-spa-presentation-builder/evals/run_evals.py decks/<slug>/presentation.html
```

### 4. Send via Email
Attach `decks/<slug>/presentation.html` directly to any email. Recipients can double-click and open it immediately with zero CORS warnings, external network requests, or missing files.

