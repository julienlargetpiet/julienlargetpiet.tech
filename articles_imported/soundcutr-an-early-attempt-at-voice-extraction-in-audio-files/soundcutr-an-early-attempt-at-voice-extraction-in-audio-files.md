## Introduction

Think of this article as a small time capsule of my programming journey — proof that everyone starts somewhere, and that projects don’t need to be perfect to be fun and functional.

## Project Overview

The goal of **SoundCutr** was to isolate the human voice from an audio track. This is useful for tasks like:

- Karaoke (removing or extracting vocals)
- Speech analysis
- Audio preprocessing for further machine learning tasks

The approach is based on two key principles:

1. **Frequency filtering** to focus on the human voice range (roughly 300 Hz – 3400 Hz).
2. **Block compartmentalization** (time segmentation) to distinguish between real continuous speech and short transient sounds.

## How It Works

The pipeline for processing audio files includes both spectral and temporal logic:

1. **Read the audio file** (typically a `.wav` format).
2. **Apply filters** to separate low, mid, and high frequencies.
3. **Focus on the mid-range band**, where the human voice dominates.
4. **Divide the signal into blocks** of 100 ms each.
5. **Classify each block** as either:

   - a short transient noise (“pop” or artifact), or
   - a real voice segment.
6. **Handle drop artifacts:** if a block is empty but the previous and next ones are identified as voice, then the middle block is considered a “drop” artifact — and is kept as part of the continuous voice.
7. **Rebuild the audio** emphasizing only the valid voice blocks.

### Example Code Snippet

```

// Pseudocode for block-based detection
signal = read("input.wav");
blocks = split_into_blocks(signal, 100ms);

for each block:
    if is_voice(block):
        mark_as_voice(block);
    else if prev_block_is_voice and next_block_is_voice:
        // Likely a drop artifact, keep it as voice
        mark_as_voice(block);
    else:
        mark_as_noise(block);

rebuild_audio(blocks, "voice_output.wav");

```

This combination of **frequency filtering** and **temporal block analysis** is what makes the algorithm more robust than a simple band-pass filter.

## Limitations (and a Smile)

Now, let’s be honest: this is an _old project_. My C++ skills (and general thinking practices, thanks Haskell) have evolved a lot since then..

That said, the fundamental concept — using block compartmentalization to detect real continuous voice — is solid. In fact, this logic of “fill in the gaps if neighbors are valid” is a common strategy in signal processing even today.

## Conclusion

**SoundCutr** was one of my first explorations into audio signal processing in C++. It may not reflect my current programming level, but it’s a fun reminder that experimenting and building things is the best way to learn.

If you want to check it out (nostalgia and all included), the code is available here:

👉 [GitHub Repository: SoundCutr](https://github.com/julienlargetpiet/sound_cutr)