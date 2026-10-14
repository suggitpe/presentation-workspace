#!/usr/bin/env python3
"""Presentation Pre-flight Evaluation Suite."""

import sys
import re
from pathlib import Path

def run():
    target_path = sys.argv[1] if len(sys.argv) > 1 else "slides.md"
    slides = Path(target_path)
    failures = []
    passes = []

    if not slides.exists():
        print(f"FAIL: {target_path} not found.")
        sys.exit(1)

    content = slides.read_text(encoding="utf-8")

    # 1. Content isolation
    if re.search(r'''<div\s+class=["']reveal["']>''', content):
        failures.append(f"{target_path} contains reveal container tags. Keep content pure markdown.")
    else:
        passes.append("Markdown is decoupled from presentation HTML shells.")

    # 2. Slide delimiter checks
    sections = re.split(r'^\r?\n---\r?\n$', content, flags=re.MULTILINE)
    if len(sections) < 2:
        failures.append("Found fewer than 2 horizontal slides separated by '---'.")
    else:
        passes.append(f"Delimiters valid: {len(sections)} horizontal slides detected.")

    # 3. Density and overflow guards
    for i, sec in enumerate(sections, 1):
        sub_slides = re.split(r'^\r?\n--\r?\n$', sec, flags=re.MULTILINE)
        for j, sub in enumerate(sub_slides, 1):
            ref = f"Slide {i}.{j}" if len(sub_slides) > 1 else f"Slide {i}"
            body = re.split(r'^Note:', sub, flags=re.MULTILINE)[0]
            bullets = re.findall(r'^\s*[-*+]\s+', body, flags=re.MULTILINE)
            words = body.split()
            if len(bullets) > 6:
                failures.append(f"{ref} has {len(bullets)} bullets (limit: 6).")
            if len(words) > 160:
                failures.append(f"{ref} has {len(words)} words (limit: 160).")

    if not any("bullets" in f or "words" in f for f in failures):
        passes.append("All slides respect density limits (prevents PDF cut-off).")

    print(f"\n=== Evals for {target_path} ===")
    for p in passes:
        print(f"  [PASS] {p}")
    for f in failures:
        print(f"  [FAIL] {f}")

    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    run()
