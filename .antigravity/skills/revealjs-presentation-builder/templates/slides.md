# Presentation Title
### Subtitle or Architectural Focus

Author Name
Role / Team

Note:
Introductory speaker notes and opening context.

---

## Agenda

- **Decoupled Architecture:** Content separate from presentation engines.
- **Dynamic Theming:** Seamless style swapping at runtime.
- **Automated Validation:** Pre-flight evaluation tests.
- **Reproducible Exports:** Deterministic 16:9 PDF rendering.

Note:
Session overview.

---

## Implementation Sample

```kotlin [1-2|4-6]
val deck = Deck(title = "Core Architecture")
deck.loadTheme("solarized")

// Run verification assertions
deck.runEvals()
```

Note:
Code walkthrough and explanation of highlighted lines.
