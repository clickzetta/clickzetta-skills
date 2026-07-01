#!/usr/bin/env bash
# Rewrite https://www.singdata.com/documents/<slug>[.txt] URLs to references/<file> paths.
# Reads llms.txt on stdin, writes transformed content to stdout.
# For slugs whose <slug>.md doesn't exist under references/, use explicit overrides.
set -euo pipefail

REFS_DIR="${1:?usage: rewrite-llms-urls.sh <references-dir>}"

if [[ ! -d "$REFS_DIR" ]]; then
  echo "references dir not found: $REFS_DIR" >&2
  exit 1
fi

# Map URL slugs whose filename differs from <slug>.md.
override_for() {
  case "$1" in
    java-sdk-refer)              echo "java_reference/java-sdk-summary.md" ;;
    python-sdk-refer)            echo "python_reference/python-sdk-summary.md" ;;
    LakehousePythonZettapark)    echo "LakehousePython-zettapark.md" ;;
    OptimizingComputingResources) echo "optimizing-computing-resources.md" ;;
    Server_data_for_AI)          echo "server-data-for-ai.md" ;;
    tools)                       echo "tools_BI.md" ;;
    *)                           echo "" ;;
  esac
}

content=$(cat)

content=$(printf '%s' "$content" \
  | sed -E '/^> Each section below is a focused sub-index; fetch only what you need\.$/d; /^## (Quick Start|User Guide|AI Guide|SQL Manual|Development Manual|Practice Tutorials|Release Notes|Other) → https:\/\/(www\.)?singdata\.com\/documents\/llms-[A-Za-z0-9_-]+\.txt$/d')

urls=$(printf '%s' "$content" \
  | grep -oE 'https://(www\.)?singdata\.com/documents/[A-Za-z0-9_-]+(\.txt)?' \
  | sort -u)

while IFS= read -r url; do
  [[ -z "$url" ]] && continue
  name="${url##*/}"
  slug="${name%.txt}"
  override=$(override_for "$slug")
  if [[ -n "$override" ]]; then
    target="references/$override"
  elif [[ "$name" == *.txt && -f "$REFS_DIR/$name" ]]; then
    target="references/$name"
  elif [[ -f "$REFS_DIR/$slug.md" ]]; then
    target="references/$slug.md"
  else
    found=$(find "$REFS_DIR" -maxdepth 1 -type f -iname "${slug}.md" -print -quit 2>/dev/null || true)
    if [[ -n "$found" ]]; then
      target="references/$(basename "$found")"
    else
      target="references/$slug.md"
      echo "⚠️  No file found for slug: $slug (falling back to $target)" >&2
    fi
  fi
  esc_target=${target//\//\\/}
  escaped_url=$(printf '%s' "$url" | sed 's/[.[\*^$()+?{}|]/\\&/g')
  content=$(printf '%s' "$content" | sed -E "s|${escaped_url}|${esc_target}|g")
done <<< "$urls"

printf '%s' "$content"
