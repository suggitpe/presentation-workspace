#!/usr/bin/env bash
set -euo pipefail

NAME="${1:-}"
THEME="${2:-black}"

if [[ -z "$NAME" ]]; then
  echo "Usage: ./scripts/new-presentation.sh <presentation-slug> [theme]"
  echo "Example: ./scripts/new-presentation.sh event-driven solarized"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${REPO_ROOT}/decks/${NAME}"

if [[ -d "$TARGET_DIR" ]]; then
  echo "Error: Directory ${TARGET_DIR} already exists." >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

cp "${REPO_ROOT}/.antigravity/skills/revealjs-presentation-builder/templates/index.html" "${TARGET_DIR}/index.html"
cp "${REPO_ROOT}/.antigravity/skills/revealjs-presentation-builder/templates/slides.md" "${TARGET_DIR}/slides.md"

cat << EOF > "${TARGET_DIR}/export.sh"
#!/usr/bin/env bash
../../.antigravity/skills/revealjs-presentation-builder/scripts/export-pdf.sh "${THEME}" "${NAME}.pdf"
EOF

chmod +x "${TARGET_DIR}/export.sh"

echo "Presentation scaffolded at: decks/${NAME}"
echo "1. Edit:    decks/${NAME}/slides.md"
echo "2. Preview: cd decks/${NAME} && python3 -m http.server 8000"
echo "3. Export:  cd decks/${NAME} && ./export.sh"
