Bash arrays aren't just containers, they're a way to control how data flows through the shell.

This guide builds from zero to production-grade patterns, using real examples like file processing and reverse lookups.

---

## 1\. The Basics (Quick but Solid)

**Creating arrays**

```bash


arr=(apple banana "cherry pie")


```

**Access**

```bash


echo "${arr[0]}"
echo "${arr[@]}"
echo "${#arr[@]}"


```

> 👉 Always use `"${arr[@]}"` — this preserves elements.

---

## 2\. The Rule That Changes Everything

`"${arr[@]}"` vs `${arr[@]}`

```bash


arr=("a b" "c d")

for x in ${arr[@]}; do echo "$x"; done   # broken

a
b
c
d

for x in "${arr[@]}"; do echo "$x"; done # correct

a b
c d



```

> 👉 Without quotes, Bash:
>
> - splits on spaces
> - expands wildcards

---

## 3\. Real Data: Reading Files Safely

Let's start doing something real.

**❌ Wrong way**

```bash


arr=($(ls))


```

Breaks on:

- spaces
- special characters

**✅ Correct way**

```bash


mapfile -t arr3 < <(ls)


```

- `-t` flag means strip all `\n` for every newline, so no elements have a trailing `\n`

Now:

```bash


for i in "${!arr3[@]}"; do
  echo "$i -> ${arr3[$i]}"
done


```

**Example output:**

```text


0 -> 2026-02-14 16-36-43.mkv
1 -> 2026-02-14 16-39-36.mkv
...


```

---

## 4\. Real Pattern: Build a Reverse Lookup Map

**Goal:** 👉 Given a filename → find its index

**❌ Naive (broken)**

```bash


declare -A map
for i in "${!arr3[@]}"; do
  map[${arr3[$i]}]=$i   # ❌ WRONG
done


```

- `-A` is for an associative array -> hashmap
- `-a` is for an index array

**Why it fails:**

- filenames contain spaces
- Bash splits them into multiple words

**Correct version**

```bash


declare -A map

for i in "${!arr3[@]}"; do
  map["${arr3[$i]}"]=$i
done


```

**Use it**

```bash


file="2026-02-14 16-40-28.mkv"
echo "${map["$file"]}"


```

> 👉 O(1) lookup instead of scanning the array.

---

## 5\. Debugging Gotcha

If you write:

```bash


echo "$k -> map[$k]"


```

You'll get:

```text


file -> map[file]


```

> 👉 That's just a string.

**Correct**

```bash


echo "$k -> ${map["$k"]}"


```

> 👉 `${...}` triggers evaluation.

---

## 6\. Iteration Patterns (Real Usage)

**Process files safely**

```bash


for file in "${arr3[@]}"; do
  echo "Processing: $file"
done


```

**With index (important for mapping)**

```bash


for i in "${!arr3[@]}"; do
  file=${arr3[$i]}
  echo "$i -> $file"
done


```

---

## 7\. Real Use Case: Filtering Files

**Example: keep only `.mkv`**

```bash


filtered=()

for f in "${arr3[@]}"; do
  [[ $f == *.mkv ]] && filtered+=("$f")
done


```

---

## 8\. Transformations

**Rename preview**

```bash


for f in "${arr3[@]}"; do
  echo "${f/.mkv/.mp4}"
done


```

**Apply to array**

```bash


new=("${arr3[@]/.mkv/.mp4}")


```

---

## 9\. Associative Arrays = Power Tool

**Real use: deduplicate files**

```bash


declare -A seen
unique=()

for f in "${arr3[@]}"; do
  if [[ -z ${seen["$f"]} ]]; then
    unique+=("$f")
    seen["$f"]=1
  fi
done


```

---

## 10\. Subshell Trap (VERY Important)

**Broken**

```bash


cat file.txt | while read -r line; do
  arr+=("$line")
done


```

> 👉 `arr` is empty after loop.

**Correct**

```bash


while read -r line; do
  arr+=("$line")
done < file.txt


```

---

## 11\. Arrays as Safe Command Builders

**Real-world safe command**

```bash


args=(-l -h --color=auto)
ls "${args[@]}"


```

**Dynamic command**

```bash


cmd=(grep -i "error" logfile.txt)
"${cmd[@]}"


```

> 👉 No `eval`, no injection risk.

---

## 12\. Subtle Tricks

**Reverse array**

```bash


rev=()
for ((i=${#arr3[@]}-1; i>=0; i--)); do
  rev+=("${arr3[i]}")
done


```

**Stack behavior**

```bash


stack=()

stack+=("a")              # push
last="${stack[-1]}"       # peek
unset 'stack[-1]'         # pop


```

**Join safely**

```bash


join_by() {
  local IFS="$1"
  shift
  echo "$*"
}

join_by "," "${arr3[@]}"


```

Here there is a lot going on. In fact, a simpler version could be:

```text


$ arr=("a b" "c" d)
$ IFS=","
$ echo "${arr[*]}"
a b,c,d


```

This works because `"${arr[*]}"` joins all elements into a single string using the first character of IFS.

But the function is more general, because it is intended to be used as:

```text


$ join_by "," "${arr[@]}"


```

Here, the separator is given as the first argument, which is why we do:

`local IFS="$1"`

Then we `shift`, to remove the first argument (the separator), so that the remaining arguments are only the elements to join.

And because inside a function the arguments are not in an array but in positional parameters:

```text


$1, $2, … → individual arguments
$@ → all arguments (as separate elements)
$* → all arguments as a single string


```

Using:

```bash


echo "$*"


```

joins all remaining arguments into one string using IFS.

So effectively:

```bash


"$*"


```

inside the function behaves like:

```bash


"${arr[*]}"


```

but applied to the function arguments instead of a specific array.

---

## 13\. Performance Reality (Important)

Arrays in Bash are:

- slow compared to real languages
- memory-heavy (strings everywhere)

**Use arrays when:**

- handling argument lists
- small/medium datasets
- mapping (like the reverse lookup example)

**Avoid arrays when:**

- processing huge files
- streaming is possible

---

## 14\. Mental Model Upgrade

**The key insight:**

> Bash arrays are not "data structures" — they are **word control mechanisms**

They exist to:

- preserve boundaries between values
- prevent splitting/globbing bugs
- safely build commands

---

## Final Real Example (Everything Together)

```bash


mapfile -t arr3 < <(ls)

declare -A map

# Build reverse lookup
for i in "${!arr3[@]}"; do
  map["${arr3[$i]}"]=$i
done

# Use it
target="${arr3[3]}"
echo "Index of '$target' is ${map["$target"]}"

# Process safely
for file in "${arr3[@]}"; do
  echo "Processing: $file"
done


```

---

## Final Thought

You're already touching the hard parts:

- quoting
- expansion
- associative arrays with real data

That's where most Bash scripts break — and where good ones are made.