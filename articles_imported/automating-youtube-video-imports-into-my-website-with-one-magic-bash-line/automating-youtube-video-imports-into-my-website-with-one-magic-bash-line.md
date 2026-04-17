## Introduction

Over the past months I’ve been downloading my own YouTube videos with
[yt-dlp](https://github.com/yt-dlp/yt-dlp). It’s a fantastic tool for archiving,
and I’ve built up a folder full of `.mp4`, `.webm`, and `.mkv` files.


But here’s the boring part: every time I wanted to put those videos on my personal website,
I had to manually write `<a>` tags for each one. Copying file names, escaping spaces,
renaming stuff… too much grunt work.


So I decided to automate it.

And the result is this single, magic line of Bash:

```bash

$ find . -type f \( -name "*.webm" -o -name "*.mp4" -o -name "*.mkv" \) -printf "%P\0" | xargs -0 -n1 bash -c 'X="$1"; clean=$(echo "$X" | sed "s/ /_/g"); echo "<a href="/assets/common_files/$clean">$X</a><br>"' X1

```

## Breaking Down the Magic

- **find . -type f \\( -name "\*.webm" -o -name "\*.mp4" -o -name "\*.mkv" \\)**


   This searches the current directory (and subdirectories) for my video files.
   I only want mp4, mkv, or webm.

- **-printf "%P\\0"**


   Normally `find` outputs paths starting with `./`. With `%P`, that’s stripped away.
   The `\0` means each result is separated by a _null byte_ instead of a newline — very handy if filenames have spaces or weird characters.

- **xargs -0 -n1**


   This reads the null-terminated list and passes each filename **one by one** into the next command ( `-n1` = one argument at a time).
   The `-0` matches the `\0` from `find`.

- **bash -c '…' X1**


   This runs a little subshell script for each file.
   `X="$1"` grabs the filename argument passed in (the `X1` at the end is just a dummy placeholder).

- **clean=$(echo "$X" \| sed "s/ /\_/g")**


   Replace spaces in the filename with underscores, so links don’t break.

- **echo "<a href="/assets/common\_files/$clean">$X</a>"**


   Finally, output an `<a>` tag where the `href` points to the cleaned filename, but the link text stays the original filename.


## The End Result

Run that command in my videos folder, and out comes a neat list of HTML links, like this:

```

<a href="../../static/My_Video_Title.mp4">My Video Title.mp4</a>
<a href="../../static/Another_Episode.webm">Another Episode.webm</a>
<a href="../../static/Archive_Talk.mkv">Archive Talk.mkv</a>

```

Now I just copy-paste the output straight into my site’s HTML. No hand-editing, no mistakes, no wasted time.

## Why I Love This

- **Fully automated.** Every new video I download is just one command away from being “web-ready.”
- **Robust against weird filenames.** Thanks to null separation and `xargs -0`, it handles spaces, quotes, even oddball characters.
- **Hackable.** Want Markdown links instead of HTML? Just tweak the `echo`. Want a custom URL path? Change the prefix.

This is the beauty of the UNIX philosophy: small tools, combined cleverly, save you hours of repetitive work.

🔥 Now my YouTube video archive basically imports itself onto my website with a single line.

## Worth mentioning

Because i need to not have any whitespace on my files, i could also just do:

```bash

$ find . -type f \( -name "*.webm" -o -name "*.mp4" -o -name "*.mkv" \) -printf "%P\0"   | xargs -0 -n1 bash -c 'X="$1"; clean=$(echo "$X" | sed "s/ /_/g"); mv "$X" $clean' X1

```

to rename all my files without any whitespace, then just an `ls > markup.html`