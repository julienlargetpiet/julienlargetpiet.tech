Most people edit their YouTube videos with slick GUIs: Premiere, DaVinci Resolve, Final Cut Pro, even OBS + Shotcut for the open-source crowd. Me? I’m allergic to timelines and mouse-dragging. I prefer to edit in the most brutalist way possible: directly from the terminal, using nothing but ffmpeg.

Yes, I’m basically editing like a robot with a text editor and command lines. It’s unusual, it’s nerdy, but it works. Let me walk you through my strange ritual.

## Step 1 — Recording the Chaos

I start by summoning `ffmpeg` to record my microphone and my screen at the same time. One incantation later:

```bash

$ ffmpeg \
  -f pulse -i alsa_input.usb-JMDZ_MICROPHONE_WOODBRASS_UM1_20211207-00.mono-fallback \
  -f x11grab -s 1920x1080 -i :0.0

```

- `-f pulse` tells `ffmpeg` to grab audio through `PulseAudio`, my sound system on Linux.
- Then I point it at my mic input.
- `-f x11grab` says: “grab the X11 display,” my desktop.
- `-s 1920x1080` means standard Full HD.
- `:0.0` is my main screen.

Boom. Both my screen and my voice are recorded straight into a video file, no OBS required.

## Step 2 — Slicing the Recording

Now I have a few raw takes: `out1.mp4, out2.mp4`, etc. They’re messy. Instead of dragging clips into a timeline, I slice them like a surgeon:

```bash

$ ffmpeg -i out2.mp4 -ss 00:00:05 -to 00:02:30 out2b.mp4

```

Here I chop off the boring parts and keep only what I want. Each cut produces a cleaner clip: `out2b.mp4, out3b.mp4`, and so on.

## Step 3 — The Magic Playlist File

When I’ve gathered my chosen clips, I don’t drop them into an editor. Instead, I write them into a plain text file—like I’m drafting a mixtape playlist from the ’90s:

 `vids.txt`

```

file 'out2b.mp4'
file 'out3b.mp4'
file 'out4b.mp4'
file 'out5b.mp4'
...

```

It’s so simple it’s almost funny.

## Step 4 — Concatenating the Franken-Video

Now the playlist becomes a full video. One command glues everything together:

```bash

$ ffmpeg -f concat -i vids.txt outF.mp4

```

That’s it. No “export” button, no “render queue.” Just a stitched-up Frankenstein video.

## Step 5 — Making It Louder (Because YouTube Audio Is Always Too Quiet)

My mic always records a bit too softly. Instead of fiddling with audio settings, I just **crank the gain afterward**:

```bash

$ ffmpeg -i outF.mp4 -filter:a "volume=3.0" outF2.mp4

```

Voilà (allow it, i'm french). The final file, `outF2.mp4`, is YouTube-ready.

## Why Do It This Way?

- It’s fast once you memorize the commands.
- It’s **scriptable**, I can automate my whole editing pipeline.
- It feels like `cyberpunk` wizardry.

Sure, it’s not “normal.” But if you enjoy the command line and want a lightweight, minimalist approach to editing, `ffmpeg` can handle it all: recording, cutting, concatenating, and even audio fixes.

And that’s how I edit my YouTube videos in the weirdest, nerdiest way possible —> no timeline, no GUI, just pure `ffmpeg` kung-fu.