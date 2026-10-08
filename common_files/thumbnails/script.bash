#!/usr/bin/bash

for i in *.jpg; do
  ffmpeg -y -i $i -c:v libwebp -q:v 75 "${i%.jpg}.webp"
done
