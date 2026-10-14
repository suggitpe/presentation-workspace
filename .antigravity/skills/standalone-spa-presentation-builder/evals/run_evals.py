#!/usr/bin/env python3
"""
Pre-Flight Assertion Suite for Standalone SPA Presentations
Validates that generated HTML is 100% self-contained, email-safe, and functionally complete.
"""

import sys
import re
from pathlib import Path

def evaluate_deck(html_path: Path):
    print(f"\n--- Running Pre-Flight Evals for: {html_path.name} ---")
    failures = []
    passes = []

    if not html_path.exists():
        print(f"[FAIL] Target presentation file does not exist: {html_path}")
        return False

    content = html_path.read_text(encoding="utf-8")
    size_bytes = html_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    # Check 1: File size under 5 MB for email safety
    if size_mb <= 5.0:
        passes.append(f"Email file size check: {size_mb:.2f} MB <= 5.0 MB limit")
    else:
        failures.append(f"Email file size warning: {size_mb:.2f} MB exceeds 5.0 MB recommended email limit")

    # Check 2: 100% self-contained (No external HTTP/HTTPS scripts or stylesheets)
    ext_scripts = re.findall(r'<script[^>]+src=["\'](https?://[^"\']+)["\']', content, re.IGNORECASE)
    ext_styles = re.findall(r'<link[^>]+href=["\'](https?://[^"\']+)["\']', content, re.IGNORECASE)

    if not ext_scripts and not ext_styles:
        passes.append("100% self-contained check: Zero external CDN scripts or remote stylesheets found")
    else:
        for s in ext_scripts:
            failures.append(f"External script detected: {s}")
        for l in ext_styles:
            failures.append(f"External stylesheet detected: {l}")

    # Check 3: Slide count & presence
    slides = re.findall(r'<section\s+class=["\'][^"\']*slide[^"\']*["\']', content, re.IGNORECASE)
    if len(slides) > 0:
        passes.append(f"Slide count check: {len(slides)} slides rendered")
    else:
        failures.append("No slide sections (<section class=\"slide\">) found in presentation")

    # Check 4: SPA components
    spa_elements = [
        ("Progress bar", 'id="progress-bar"'),
        ("Slide counter", 'id="slide-counter-top"'),
        ("Overview modal", 'id="overview-modal"'),
        ("Speaker notes drawer", 'id="notes-drawer"'),
        ("Theme switcher", 'id="btn-theme"'),
        ("SPA runtime script", 'addEventListener(\'keydown\'')
    ]

    for label, signature in spa_elements:
        if signature in content:
            passes.append(f"SPA component check: {label} present")
        else:
            failures.append(f"Missing SPA component: {label} ({signature})")

    # Report results
    print("\nPassed Assertions:")
    for p in passes:
        print(f"  \033[32m[PASS]\033[0m {p}")

    if failures:
        print("\nFailed Assertions:")
        for f in failures:
            print(f"  \033[31m[FAIL]\033[0m {f}")
        print(f"\nResult: FAILED ({len(failures)} failures)\n")
        return False

    print(f"\nResult: ALL {len(passes)} CHECKS PASSED. Presentation is 100% self-contained and ready for email delivery!\n")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_evals.py <path/to/presentation.html>")
        sys.exit(1)

    target_path = Path(sys.argv[1]).resolve()
    success = evaluate_deck(target_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
