There's a moment when using `sed` stops feeling like typing weird incantations… and starts feeling like you're programming a living stream of text.

At first, it looks like this:

```text


sed '1,2p' file


```

And you think:

> "ok… print lines 1 and 2… neat, but whatever"

But if you stay with it — if you push just a bit further — you discover something unexpected:

**sed is not a command. It is a language.**

A small one. A strange one. But a real one --> with control flow, memory, and a model of execution.

And that's how you end up writing things like:

`script.sed`

```bash


/./H
/^$/ {
    x
    /./ {
        s/\n/ /g
        s/^ //
        p
    }
}
$ {
    x
    s/\n/ /g
    s/^ //
    /./ { p }
}


```

```bash


sed -n -E -f script.sed ex3.log


```

…and suddenly, you're not filtering text anymore.

👉 You're processing a stream.

---

## The first principle: sed is a stream machine

At its core, sed does this:

```text


read line → transform → (maybe print) → repeat


```

One line at a time. No context. No memory.

That's why the simplest commands feel trivial:

### Basic streaming

```bash


sed '1,2p' file      # print lines 1 and 2
sed '/error/p' file  # print lines matching "error"
sed '5q' file        # stop at line 5
sed '/foo/d' file    # delete lines matching "foo"


```

### Core commands you must know



| Command | Meaning |
| --- | --- |
| <code>p</code> | print |
| <code>d</code> | delete and skip rest |
| <code>q</code> | quit immediately |
| <code>s///</code> | substitute |




### Example

```bash


sed -n '1,5p' file


```

👉 disable default output ( `-n`) and print explicitly

---

## Editing the stream

You can also modify lines:

```bash


sed 's/foo/bar/g' file   # replace text


```

### Insert / append / change

These are surprisingly expressive:

```bash


sed '/Alice/i BEFORE' file   # insert before
sed '/Alice/a AFTER' file    # append after
sed '/Alice/c REPLACED' file # replace line


```



| Command | Effect |
| --- | --- |
| <code>i</code> | insert before |
| <code>a</code> | append after |
| <code>c</code> | replace line |




You can combine streaming portions of the lines to processing them like doing:

```bash


sed -n '2,4 {/Alice/c REPLACED}; p' file


```

Note that we seprarate the commands with `;` and wrapped the change `c` command inside `{}`, so after we can print what happened.

Some commands like `c` stops direclty further commands that is why we wrapped them.

In fact `c` will stop further commands inside the block.

---

## The first illusion breaks

Up to now, sed is just: _"a tool that edits lines"_

But then you hit a problem:

### Problem: multi-line data

```text


Error: Something failed:
    at module A
    at module B


```

👉 This is not line-based anymore

### Enter: loops and multi-line thinking

```bash


sed -n -e ":loop N; s/\n[[:space:]]\+/ /g; t loop; p" ex.log


```

**Input:**

```text


Error: Something failed:
    at module A
    at module B

Next event



```

**Output:**

```text


Error: Something failed: at module A at module B
Next event


```

Important note, here there are trailing `\n`, but if the file was:

```text


Error: Something failed:
    at module A
    at module B

Next event


```

With no trailing `\n` at the very end of the file, then the output would be:

```text


Error: Something failed: at module A at module B


```

`Next event` is not printed...

because of N that only succeeds if it can take 2 rows.

So to solve this problem we do:

```text


sed -n -e ":loop; $!N; s/\n[[:space:]]\+/ /g; t loop; p; $p" error.log


```

It guarantees that no `N` is invoked at the last line, and that `p` is.

### What just happened?

You just wrote a loop:

```text


:loop
N
s/\n[[:space:]]\+/ /g
t loop


```

**Breakdown:**

- `N` → append next line
- `s` → try to merge lines
- `t loop` → repeat if substitution worked

💥 This is a real loop. Equivalent to:

```python


while can_merge:
    merge_lines()


```

👉 At this moment, sed stops being a filter — and becomes a program.

---

## The big shift: pattern space is not a line anymore

With `N`, pattern space becomes:

```text


line1\nline2\nline3


```

👉 You are now working on buffers.

---

## The second big shift: sliding windows

Now consider:

```bash


sed -n -E 'N; h; s/\n/->/g ;p; g; D' ex2.log


```

**Input:**

```text


A
B
C
D
E


```

**Output:**

```text


A->B
B->C
C->D
D->E


```

### What is happening?

This is where sed becomes… almost magical.

**Two worlds appear:**

1. **Pattern space** → computation


   ```text


   A\nB  →  transformed  →  A->B


   ```

2. **Hold space** → memory


   ```text


   A\nB


   ```


### The key operations

```text


h   # save structure
g   # restore structure
D   # slide window


```

### What you built

A sliding window:

```text


[A,B]
[B,C]
[C,D]
[D,E]


```

### The invariant

👉 `D` needs `\n` to exist

So you:

1. destroy structure ( `s/\n/->/`)
2. print
3. restore structure ( `g`)
4. slide ( `D`)

### Final model

```text


structure = truth
display   = transformation


```

👉 You compute on a view, but preserve the truth.

---

## When it starts being surprinsingly good

Up until now, you've been transforming lines.

Then suddenly, you see this:

```bash


sed -n -E 'N; h; s/\n/->/g; p; G; D' ex2.log


```

```text


A->B
A->B->C
A->B->C->D
A->B->C->D->E


```

And something feels… different.

This is no longer line editing.

👉 This is **stateful stream computation**.

---

### The key: two memory regions

To understand this, you must accept one fundamental truth:

**sed operates on two distinct spaces**

### 1\. Pattern space (the present)

👉 This is:

- the current working buffer
- what commands modify
- what `p` prints

Think:

```text


pattern = what I am computing right now


```

### 2\. Hold space (the memory)

👉 This is:

- persistent across commands
- invisible unless accessed
- controlled manually

Think:

```text


hold = what I choose to remember


```

---

## The commands that matter here



| Command | Meaning |
| --- | --- |
| <code>N</code> | append next line to pattern (<code>\n</code>) |
| <code>h</code> | save pattern → hold |
| <code>G</code> | append hold → pattern |
| <code>D</code> | remove first line of pattern, continue |




---

## Let's walk through execution

\\*\\* Input:\*\*

```text


A
B
C
D
E


```

### Iteration 1

**Step 1 — `N`**

```text


pattern = A\nB
hold    = (empty)


```

**Step 2 — `h`**

```text


pattern = A\nB
hold    = A\nB


```

👉 snapshot of structure

**Step 3 — `s/\n/->/`**

```text


pattern = A->B
hold    = A\nB


```

👉 ⚠️ structure is destroyed in pattern

**Step 4 — `p`**

```text


OUTPUT: A->B


```

**Step 5 — `G`**

```text


pattern = A->B\nA\nB
hold    = A\nB


```

👉 re-inject original structure

**Step 6 — `D`**

```text


pattern = A\nB
hold    = A\nB


```

👉 remove display part, keep structure

---

### Iteration 2

**Step 1 — `N`**

```text


pattern = A\nB\nC


```

**Step 2 — `h`**

```text


hold = A\nB\nC


```

👉 overwrite previous snapshot

**Step 3 — `s`**

```text


pattern = A->B->C


```

**Step 4 — `p`**

```text


OUTPUT: A->B->C


```

**Step 5 — `G`**

```text


pattern = A->B->C\nA\nB\nC


```

**Step 6 — `D`**

```text


pattern = A\nB\nC


```

---

## What is really happening

At every iteration, the structure grows:

```text


A\nB
A\nB\nC
A\nB\nC\nD


```

But you **never build from transformed data**.

### The key insight

👉 You are maintaining **two representations**:



| Role | Content |
| --- | --- |
| structure (truth) | <code>A\nB\nC</code> |
| display (view) | <code>A-&gt;B-&gt;C</code> |




### The trick

```text


h   # save structure
s   # destroy structure (for display)
p   # show display
G   # restore structure
D   # continue sliding


```

### The invariant

`D` only works if `\n` exists. So:

- you temporarily break the structure
- then restore it before `D`

---

## This is the algorithm

```text


grow structure   (N)
save structure   (h)

display = transform(structure)
print(display)

restore structure (G + D)
repeat


```

---

## This is NOT obvious

At first glance, you might think:

> "it builds A->B, then B->C…"

**Wrong.**

👉 It always builds from:

```text


A\nB\nC\nD...


```

### Think like this

```text


pattern = working buffer
hold    = checkpoint of truth


```

---

## Why this matters

This pattern unlocks:

- cumulative computations
- prefix building
- streaming aggregation
- rolling transformations

---

## Minimal mental model

👉 sed =

```text


(pattern space) + (hold space) + (control flow)


```

## sed is now a state machine

You now have:

- memory ( `h`, `g`)
- loops ( `:`, `t`)
- buffers ( `N`, `D`)

👉 This is no longer "text processing"

👉 This is **stream programming**

---

## Final evolution: grouping blocks

Now consider real-world logs:

```text


line1
line2

line3
line4
line5

line6
line7


```

\\*\\* Goal:\*\*

```text


line1 line2
line3 line4 line5
line6 line7


```

### Script

```bash


/./H
/^$/ {
    x
    /./ {
        s/\n/ /g
        s/^ //
        p
    }
}
$ {
    x
    s/\n/ /g
    s/^ //
    /./ { p }
}


```

**▶️ Run it:**

```bash


sed -n -E -f script.sed ex3.log


```

### What is happening?



| Expression | Effect |
| --- | --- |
| <code>/./H</code> | accumulate non-empty lines |
| <code>/^$/</code> | block separator |
| <code>x</code> | bring accumulated block into pattern space |
| <code>s/\n/ /g</code> | flatten block |
| <code>$</code> | handle last block (EOF) |




🔥 You just:

- grouped variable-length blocks
- transformed them
- handled edge cases
- wrote reusable logic

👉 This is not a one-liner anymore.

👉 This is **a program**.

But we could also avoids nesting block deleting each blank lines that comes after a paragraph:

```text


/./H
/^$/ {
     x
     s/\n/ /g
     s/^ //
     /^$/d
     p
}
$ {
     x
     s/\n/ /g
     s/^ //
     /./ { p }
}



```

with this pattern:

```text


/^$/d


```

---

## The final mental model

sed is:

```text


a streaming engine
+ a working buffer (pattern space)
+ a memory buffer (hold space)
+ control flow (loops, branches)


```

### The secret to mastering sed

It's not about memorizing commands. It's about understanding:

**1\. The execution loop**

```text


read → process → print → repeat


```

**2\. The invariant**

- pattern space = computation
- hold space = state

**3\. The transformations**



| Command | Action |
| --- | --- |
| <code>N</code> | grow |
| <code>D</code> | slide |
| <code>H</code> | accumulate |
| <code>h</code> / <code>g</code> | checkpoint / restore |




---

## Why it feels "shamanic"

Because you're not writing steps.

You're maintaining **invariants**:

- "newline must exist"
- "structure must be preserved"
- "state must be restored"

> _The master of sed doesn't edit text._
>
> _They shape streams._

In fact `sed` is what `jq` is for `JSon` but for text.

Note:

To modify the file in-place, use the `-i` flag followed by the name of the file.