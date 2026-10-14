#!/usr/bin/env python3
"""
CLI Scaffolder for Standalone SPA Presentations
Creates a new deck directory in decks/<slug>/ with template slides.md, build scripts, and runs initial build.
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python new-deck.py <slug> [Title] [Presenter]")
        print("Example: python new-deck.py quarterly-review \"Q3 Engineering Review\" \"Alex Smith\"")
        sys.exit(1)

    slug = sys.argv[1].strip().lower().replace(" ", "-")
    title = sys.argv[2] if len(sys.argv) > 2 else slug.replace("-", " ").title()
    presenter = sys.argv[3] if len(sys.argv) > 3 else "Presenter"
    today_str = datetime.now().strftime("%B %Y")

    skill_dir = Path(__file__).resolve().parent.parent
    templates_dir = skill_dir / "templates"
    repo_root = skill_dir.parents[2]
    deck_dir = repo_root / "decks" / slug

    if deck_dir.exists():
        print(f"Error: Deck directory already exists at {deck_dir}")
        sys.exit(1)

    deck_dir.mkdir(parents=True)
    images_dir = deck_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Populate slides.md from template
    template_slides = (templates_dir / "slides.md").read_text(encoding="utf-8")
    custom_slides = template_slides.replace("{{PRESENTATION_TITLE}}", title)
    custom_slides = custom_slides.replace("{{PRESENTATION_SUBTITLE}}", "Executive Briefing & Update")
    custom_slides = custom_slides.replace("{{PRESENTER_NAME}}", presenter)
    custom_slides = custom_slides.replace("{{DATE}}", today_str)
    (deck_dir / "slides.md").write_text(custom_slides, encoding="utf-8")

    # 2. Copy build.py
    shutil.copy(templates_dir / "build.py", deck_dir / "build.py")

    # 3. Create build.ps1
    (deck_dir / "build.ps1").write_text(
        "$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path\npython \"$scriptDir\\build.py\"\n",
        encoding="utf-8"
    )

    # 4. Create build.sh
    (deck_dir / "build.sh").write_text(
        "#!/usr/bin/env bash\nSCRIPT_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"\npython3 \"$SCRIPT_DIR/build.py\"\n",
        encoding="utf-8"
    )

    # 5. Create README.md
    readme_content = f"""# {title}

Standalone SPA presentation deck.

## Workflow
1. Edit `slides.md`
2. Run `python build.py` (or `.\\build.ps1`)
3. Send `presentation.html` via email!
"""
    (deck_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 6. Run initial build
    sys.path.insert(0, str(deck_dir))
    import subprocess
    print(f"Scaffolding new deck at: decks/{slug}")
    subprocess.run([sys.executable, str(deck_dir / "build.py")], check=True)

    print(f"\nDeck successfully scaffolded and compiled!")
    print(f"- Slides: {deck_dir / 'slides.md'}")
    print(f"- Output: {deck_dir / 'presentation.html'}")

if __name__ == "__main__":
    main()
