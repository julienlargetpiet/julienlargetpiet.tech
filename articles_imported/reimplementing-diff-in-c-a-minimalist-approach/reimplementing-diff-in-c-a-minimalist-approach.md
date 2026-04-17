## Why Rebuild Something That Already Exists?

The `diff` command is one of the cornerstones of the GNU/Linux ecosystem. It’s simple in appearance, yet behind the scenes it powers version control, code reviews, and collaborative software development.

I wanted to reimplement `diff` myself — not because the world needs another diff tool, but because it’s a great exercise in understanding how file comparison works at a low level. Writing it from scratch in C++ forced me to think about edge cases, data handling, and performance, even for what seems like a “trivial” utility.

## Defining the Scope

The real `diff` command is sophisticated. It can produce unified diffs, context diffs, side-by-side comparisons, and even patch-friendly outputs. My goal wasn’t to replicate all of that. Instead, I set out to create a **minimalist version**:

- Input: two files (and optionally a separator).
- Output: a side-by-side comparison.
- Mark differences with `-` and `+`.
- Stop at the first divergence.

This narrow scope kept the project focused and educational.

## Implementation Decisions

The program accepts two mandatory filenames and an optional separator string. If no separator is given, it defaults to `" | "`.

From there, it opens both files and reads them line by line. The main loop compares each line from `file1` against `file2`.

- **If the lines match** → print them side by side.
- **If a line exists only in file1** → mark it with `-`.
- **If a line exists only in file2** → mark it with `+`.

```cpp

while (getline(file2, currow2)) {
    comp = 0;
    while (getline(file1, currow1)) {
        comp = (currow2 == currow1);
        if (!comp) {
            std::cout << currow1 << sep << "- " << "\n";
        } else {
            break;
        }
    };
    comp = (currow1 == currow2);
    if (comp) {
        std::cout << currow1 << sep << currow2 << "\n";
    } else {
        break;
    };
}

```

This nested loop is where the actual comparison happens. It might not be the most efficient solution, but it captures the essential logic: line-by-line matching until divergence.

## What Worked, What Didn’t

The program works for basic comparisons, but it’s very naive. As soon as files diverge significantly, the logic breaks down. For example:

- Reordered lines aren’t handled.
- Insertions and deletions at multiple positions confuse the loop.
- It doesn’t produce context around changes, like GNU `diff` does.

But that’s fine — my intention was never to compete with the mature tool. Instead, I gained:

- A better intuition for how diffing algorithms work.
- An appreciation for the complexity hidden inside “simple” commands.
- A foundation I could extend later if I want to explore LCS (Longest Common Subsequence) algorithms or patch generation.

## Next Steps

Possible improvements could include:

- Implementing the **LCS algorithm** to handle more complex differences.
- Adding **colorized output** for readability.
- Supporting **unified diff format** for compatibility with Git.

For now, though, I’m satisfied with this minimal diff clone. It’s a small project, but one that forced me to dive into text processing and algorithmic thinking in C++.

👉 [GitHub Repo](https://github.com/julienlargetpiet/semantic_tools/blob/main/semdiff.cpp)