#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-articles_imported}"

mkdir -p "$ROOT_DIR"

slugify() {
  local input="$1"
  local slug

  # Lowercase
  slug=$(printf '%s' "$input" | tr '[:upper:]' '[:lower:]')

  # Remove emojis / non-ascii if iconv exists
  if command -v iconv >/dev/null 2>&1; then
    slug=$(printf '%s' "$slug" | iconv -f UTF-8 -t ASCII//TRANSLIT 2>/dev/null || printf '%s' "$slug")
  fi

  # Replace apostrophes with nothing
  slug=$(printf '%s' "$slug" | sed "s/'//g")

  # Replace anything not alnum with hyphens
  slug=$(printf '%s' "$slug" | sed -E 's/[^a-z0-9]+/-/g')

  # Remove leading/trailing hyphens
  slug=$(printf '%s' "$slug" | sed -E 's/^-+//; s/-+$//')

  # Fallback if empty
  if [[ -z "$slug" ]]; then
    slug="article"
  fi

  printf '%s' "$slug"
}

stx articles | while IFS= read -r line; do
  [[ -z "$line" ]] && continue

  # here we apply a regex match, creating 2 subgroups if successfull 
  # INTEGER TITLE --> exactly what we want, because fits the output format of
  # stx articles

  if [[ "$line" =~ ^([0-9]+)[[:space:]]+(.*)$ ]]; then
    id="${BASH_REMATCH[1]}"
    title="${BASH_REMATCH[2]}"
  else
    echo "Skipping unparsable line: $line" >&2
    continue
  fi

  slug=$(slugify "$title")
  name="${slug}"
  dir="$ROOT_DIR/$name"

  mkdir -p "$dir"

  cat > "$dir/metadata.txt" <<EOF
id: $id
title: $title
nickname: $name
directory: $dir
EOF
 
  echo "Processing article $id -> $name"

  # Create nickname locally
  stx nickname import "$id" "$name"

  # Import markdown content
  (
    cd "$dir"
    stx nickname import-content --markdown "$id" "$name"
  )

done


