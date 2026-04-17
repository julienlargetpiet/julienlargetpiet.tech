## Prerequisites

This article will reference SED syntax that is described here:

[sed](https://julienlargetpiet.tech/articles/sed-a-powerfull-mini-language-from-the-70s.html)

This was also vastly ispired by this comment (user: piekvorst) on HackerNews (a lot of credits go to this user and ressources share in the comment):

[hn](https://news.ycombinator.com/item?id=47491117)

## SAM - Installation

Because SAM is part of [Plan 9](https://en.wikipedia.org/wiki/Plan_9_from_Bell_Labs), we have to install `plan9port`:

```text


$ git clone https://github.com/9fans/plan9port.git
$ cd plan9port
plan9port$ ./INSTALL


```

then:

```text


$ export PLAN9=$HOME/plan9port
$ export PATH=$PATH:$PLAN9/bin
$ source ~/.bashrc


```

To make it permanent, write the export down to your `~/.bashrc` then `source ~/.bashrc`

## Where does it come from

SAM was written by Rob Pike at Bell Labs in the late 80s.
It comes from the same place as UNIX, but from a later phase where people were already trying to rethink some of its limitations.

SED is a stream editor. It reads line by line, mutates a state (pattern space + hold space), and moves forward.

SAM comes with a different idea:

- the file is not a stream
- it is a buffer
- you select regions
- then you apply transformations to those regions

SAM later became part of Plan 9, which pushed this idea further: everything is a file, everything is text, and tools should compose through simple primitives.

## Paradigm

Difference between sed and sam.

**SED:**

- stream line by line (default)
- state machine
- pattern space + hold space
- commands like `N`, `D`, `h`, `g` control flow

**SAM:**

- selection1 → selection2 → ... → transformation
- loop is: repeat until it doesn't longer match
- no hidden state between iterations
- everything is explicit

A SAM script is basically:

- select a region
- refine that selection
- optionally branch ( `g`, `v`)
- apply a transformation ( `c`, `a`, `d`, …)

Contrary to SED, do not think as processing lines but instead in term of rewriting the file buffer where your selectors matched.

Also, we are iterating over the buffer while it is being mutated by our own actions.

This means we are not walking a fixed structure: the data changes as we move through it.

And importantly, the buffer is modified in place, and each new selection is applied on the modified data.

```text


selection1 → modification → selection2


```

See more subtelty in following examples...

That is the mental shift.

## Syntax

I won't describe everything here. You understand SAM by using it.

## A basic SAM translation from a first SED command

`error.log`:

```text


Error: Something failed:
    at module A
    at module B

Next event


```

`script.sed`:

```sed


:loop N; s/\n[[:space:]]\+/ /g; t loop; p


```

This accumulates lines until no more "newline + spaces" can be reduced, then prints.

Output:

```text


Error: Something failed: at module A at module B
Next event


```

### In SAM

`script.sam`:

```text


, x/\n +/ c/ /


```

Run:

```sh


sam -d error.log < script.sam


```

Output:

```text


Error: Something failed: at module A at module B
Next event


```

### Explanation

- `,` means: the whole buffer. It is shorthand for `1,$`.
- In SAM, addressing is always `start,end`. `$` is the last line. You can do arithmetic like `$-1`, `$-2`, etc.
- `x/PATTERN/` means: for each match of `PATTERN` in the current selection.
- Here: `x/\n +/` selects every "newline followed by spaces".
- `c/ /` replaces the entire matched region with a single space.

So this is not a loop. It is: find all occurrences of "newline + spaces" and replace them.

No state, no iteration, no labels.

### About `c`

`c/PATTERN/` replaces the current selection.

There is also:

- `a/PATTERN/` → append after selection
- `i/PATTERN/` → insert before selection
- `d` → delete selection

Compared to SED:

- `/pattern/a` in sed appends after a line match
- in SAM, `a/…/` works on the current selection, not on lines

## Second example

Sed command:

```sed


N; h; s/\n/->/g ;p; g; D


```

`file.txt`:

```text


A
B
C
D
E


```

Output:

```text


A->B
B->C
C->D
D->E


```

This is a sliding window:

- read next line ( `N`)
- keep a copy ( `h`)
- transform ( `s`)
- print
- restore ( `g`)
- drop first line and continue ( `D`)

### SAM

```text


1,$-2 x/./ {
    a/->/
    /./ t .
}
1,$-2 {
    p
}
q


```

Run:

```text


sam -d file.txt < script.sam


```

Output:

```text


A->B
B->C
C->D
D->E


```

### Explanation

- `1,$-2` means: you are able to start from first line to the second-to-last line

`x/./` is the actual loop

```text


matches = all matches of '.' (regex term) in selection
for each match in matches:
    run block


```

This is important: the loop is not `/./ t .`, it is `x/./.`

Inside the block:

```text


a/->/


```

Append "->" after the current position.

```text


/./ t .


```

If there is still a character, jump ( `t`) to . (the current position), which moves the cursor forward.

What actually happens
`x/./` iterates over each character
for each iteration:
we append "->"
we move forward, here to next character ("B", "C", "D", "E")
The buffer is always modified,
but `x/./` and `/./ t .` don’t chase what it just inserted.

So we are:

walking the buffer while mutating it in place

The range ( `1,$-2`) only controls where we start the loop, not where it stops.

The loop itself ( `x/./`) keeps going as long as it can find another match forward in the buffer.

If we start from `$-2` (= 6), the last starting point is D:

```text


A
B
C
D  <- last start
E


```

From D, the loop walks forward through the buffer and stops at the end.

This produces the correct final structure:

```text


A->B
B->C
C->D
D->E


```

in fact this code produces same output:

```text


1,4 x/./ {
    a/->/
    /./ t .
}
1,$-2 {
    p
}
q


```

### Variant 1.1

What happens with `$-1`

If we use:

```text


1,$-1 x/./ {
    a/->/
    /./ t .
}


```

then the last starting point becomes E.

From E, the loop walks forward:

E → (continues on modified buffer)

Observed result with `$-1`:

```text


A->B
B->C
C->D
D->E
E->A


```

### Variant 1.2

```text


1,$-3 x/./ {
    a/->/
    /./ t .
}
1,$-2 {
    p
}
q


```

Output:

```text


A->B
B->C
C->D
D


```

### Variant 2

Just to show that even if we append and move forward, the loop does not chase what was just appended. It continues with the next character in the traversal (B, C, ...).

```text


1,$-2 x/./ {
    a/->/
}
1,$-2 {
    p
}
q


```

output:

```text


A->
B->
C->
D->


```

## Third SED translation

`script.sed`:

```sed


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

This groups paragraphs:

- accumulate non-empty lines ( `H`)
- on blank line: collapse them into one line
- print
- skip blank lines

`file.txt`:

```text


line1
line2

line3
line4
line5

line6
line7


```

Output:

```text


line1 line2
line3 line4 line5
line6 line7


```

### SAM

```text


, x/(.+\n)+|\n+/ {
    g/./ x/\n/ c/ /
    v/./ c/\n/
}
$ a/\n/
, x/\n+$/ c/\n/
w file_out.txt
q


```

Run:

```sh


sam -d file.txt < script.sam


```

### Explanation

First line:

```text


, x/(.+\n)+|\n+/


```

Select blocks of either:

- paragraphs: `(.+\n)+`
- or blank lines: `\n+`

So we process structure, not lines.

Inside the block:

```text


g/./ x/\n/ c/ /


```

If the selection contains a character (so: a paragraph):

- iterate over newlines
- replace each newline with a space

Result: `line1\nline2` → `line1 line2`

```text


v/./ c/\n/


```

If the selection does NOT contain characters (so: blank lines):

- replace the whole block with a single newline

So multiple blank lines collapse into one.

### About normalization

After the transformation, the end of the buffer is not guaranteed to be correct:

- there may be no trailing newline
- or multiple ones

So we fix it:

```text


$ a/\n/


```

Ensure at least one newline exists. Then:

```text


, x/\n+$/ c/\n/


```

Normalize trailing newlines to exactly one.

### About `w`

```text


w file_out.txt


```

Writes the buffer to a file ( `file_out.txt`).

`file_out.txt`:

```text


line1 line2
line3 line4 line5
line6 line7


```

### Variant 1.1

piekvorst also proposed this alternative version:

```text


, x/(.+\n)+/ {
    .,+#0-#1  {
        x/\n/ c/ /
    }
}
, x/\n+/ c/\n/
, p


```

Here we:

- iterate over the file.
- select paragraph with regex `(.+\n)+`
- then we apply a subrange loop between start and end of the match minus the last character ( `\n`), we just exclude last `\n`
- in this subrange, we just replace all previous `\n` by a space
- after that logic, we just removes all contiguous `\n` by only one `\n`
- and we print the entire buffer `, p`

## Closing note

SED and SAM solve similar problems. But:

- SED is about **how to process** (state, loop, flow)
- SAM is about **what to transform** (selection, structure)

Trying to translate one directly into the other is often the wrong approach. You usually need to rethink the problem.

## Further ressources

piekvorst mentioned these ressources on HN:

[sam\_tut.pdf](https://ratfactor.com/papers/sam_tut.pdf) [struct-regex.pdf](https://9p.io/sources/contrib/steve/other-docs/struct-regex.pdf)