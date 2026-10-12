#!/usr/bin/env bash

CONTENT='
<a href="https://liberapay.com/julienlargetpiet/donate"
   class="support-button"
   target="_blank"
   rel="noopener noreferrer">
    ♥ Support
</a>
'

export CONTENT

find . -type f -name '*.md' \
    -exec sh -c 'printf "%s\n" "$CONTENT" >> "$0"' {} \;
