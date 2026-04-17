## A Deep Semantic and Operational Mini-Book

This is not documentation.
This is not a tutorial.
This is a semantic excavation.


We will treat jq as:


- A stream calculus

- A purely functional reduction algebra

- A tree traversal and rewrite system

- A scoped evaluation engine with explicit rebinding


---

## Note

To run a `jq` file do that:



```bash
  Copy

$ jq -f test.jq file.json


```

And also some sections will implicitly reference these files

- [file1](/assets/common_files/file1.json)
- [file2](/assets/common_files/file2.json)

---

## 1\. The Execution Model: Streams, Not Values

Every jq filter is:


```
Filter : Value → Stream<Value>

```

Even if it emits one value, it is still a stream.
Even if it emits zero values, it is still a stream.


Composition:


```
a | b

```

means:


```
for each v in a(input):
emit b(v)

```

This is critical:
`|`
is not sequential mutation.
It is stream composition.


---

## 2\. Shape Discipline: Streams vs Arrays

Given posts.json:


```jq


.[] | .title


```

This emits a stream of titles.
NOT an array.


To collect:


```jq


[ .[] | .title ]


```

Collection operator:


```
[ stream ] : Stream<a> → [a]

```

This distinction is the root of most errors.


---

## 3\. Reduction Semantics: add “Waits” for Structure

Consider:


```jq


.[] | .title | length | add


```

At
`add`,
`.`
is a number.
But
`add`
expects an array.


Correct:


```jq


[ .[] | .title | length ] | add


```

Execution flow:


```
Step 1: .[] emits Post
Step 2: .title emits String
Step 3: length emits Number
Step 4: [ ... ] collects Numbers into Array
Step 5: add reduces Array to Number

```

Important:
`add`
cannot begin until the array is fully constructed.
This is structural waiting, not concurrency.


---

## 4\. group\_by vs reduce: Structural vs Algebraic Grouping

### Structural grouping

```jq


sort_by(.userId)
| group_by(.userId)
| map({ meanTitleLen: map(.title | length) | add / length })
| sort_by(.meanTitleLen) | reverse | .[:3]


```

Execution:


```
Array<Post> → sorted Array<Post> → Array<Array<Post>> → map over groups → produce Array<Summary> → sort_by mean → reverse → slice top 3

```

### reverse and slicing

```
reverse : [a] → [a] (reorders elements)
.[:n] : [a] → first n elements
.[m:n] : slice range

```

These are structural array transforms.
They do not operate on streams.


---

## 5\. reduce: Generator Scope vs Update Scope (Deep Explanation)

The previous explanation described the two scopes mechanically.
But this example is doing something deeper:

It is emulating `group_by` using a fold.

---

Consider:

```jq


reduce .[] as $p ({};
  .[$p.userId | tostring] |= (
    . // {lengths:[], maxn: 0}
    | {
        lengths: (.lengths + [($p.title | length)]),
        maxn: (
          if ($p.title | length) > .maxn
          then ($p.title | length)
          else .maxn
          end
        )
      }
  )
)


```

---

### What group\_by normally does

If we wrote:

```
sort_by(.userId)
| group_by(.userId)

```

We would obtain:

```
Array<Post>
→ Array<Array<Post>>

```

That is structural grouping.

It requires:

- Sorting first

- Holding the entire array in memory

- Building nested arrays

- Running a second aggregation pass with `map`

It constructs structure first.
Then aggregates.

---

### What reduce does instead

reduce performs incremental grouping.

```
reduce GEN as $x (INIT; UPDATE)

```

Is equivalent to:

```
foldl UPDATE INIT (GEN(input))

```

In this example:

```
GEN   = .[]
INIT  = {}
UPDATE = object accumulation

```

We iterate over posts one by one.

---

### What the accumulator represents

The accumulator starts as:

```
{}

```

After several iterations, it becomes:

```
{
  "1": { lengths: [...], maxn: ... },
  "2": { lengths: [...], maxn: ... },
  ...
}

```

This is a map keyed by `userId`.

Each key holds aggregated statistics for that group.

That is exactly what `group_by` \+ `map` would compute —
but without ever building nested arrays.

---

### Why the two scopes matter

During execution:

```
GEN scope:
"." = each post
$p = that post

UPDATE scope:
"." = accumulator object
$p = current post

```

Two separate "." worlds.

Inside UPDATE:

```
.[$p.userId | tostring]

```

Means:

"Access the accumulator bucket corresponding to this post's userId."

If it does not exist yet:

```
. // {lengths:[], maxn: 0}

```

Initializes it.

Then it updates:

- Appending the title length

- Updating the maximum title length


---

### Why this emulates group\_by

Conceptually:

```
group_by(.userId)
| map(aggregate)

```

Does:

```
1. Partition into groups
2. Aggregate each group

```

reduce does:

```
For each element:
  Find its group bucket
  Update that bucket

```

Instead of building:

```
Array<Array<Post>>

```

It builds:

```
Object<UserId → Aggregates>

```

It performs grouping and aggregation simultaneously.

---

### Structural vs Algebraic Grouping

**group\_by** is structural:

- Rearranges the data

- Creates nested arrays

- Requires sorting


**reduce** is algebraic:

- Keeps original order irrelevant

- Updates buckets in constant time

- Never constructs intermediate nested arrays


It is a streaming group-by.

---

### The deeper insight

group\_by builds structure, then folds.

reduce folds while grouping.

One is two-phase.

The other is single-pass.

That is why this pattern emulates group\_by —
but in a more algebraic and memory-efficient way.

---

## 6\. Recursion: Evaluation Order and Waiting

### Example

```jq


def flatten_tree: if type == "array" then map(flatten_tree) | add else . end; flatten_tree


```

Input:


```
[1,[2,[3,4]],5]

```

Flow:


```
flatten_tree([1,[2,[3,4]],5])
→ map(flatten_tree)
→ flatten_tree(1) = 1
→ flatten_tree([2,[3,4]])
→ map(flatten_tree)
→ flatten_tree(2) = 2
→ flatten_tree([3,4])
→ map(flatten_tree)
→ flatten_tree(3) = 3
→ flatten_tree(4) = 4
→ add([3,4]) = 7
→ add([2,7]) = 9
→ flatten_tree(5) = 5
→ add([1,9,5]) = 15

```

Important:


- `map` waits for each recursive call to return.

- `add` waits for full array from map.

- Evaluation is depth-first.


---

## 7\. type and walk

`type`
inspects structure:


```
"string"
"number"
"array"
"object"
"boolean"
"null"

```

`walk(f)`
recursively applies f bottom-up.


### Uppercase all strings (nested.json)

```jq


walk( if type == "string" then ascii_upcase else . end )


```

walk semantics:


```
descend to leaves
apply f to leaves
reconstruct upward

```

Bottom-up traversal.


---

## 8\. paths, getpath, setpath: Tree Calculus

### Enumerate scalar leaves

```jq


paths(scalars) as $p | { path_location: $p, value: getpath($p) }


```

Here:


- `paths`
   emits path arrays

- `.`
   becomes a path

- Original root must be captured if needed


### Why capture root?

```jq


. as $root | paths as $p | select($root | getpath($p) == "rust") | ($p[0:-1]) as $parent | $root | getpath($parent)


```

After
`paths`,
"."
is a path array.
Not the document.


So:


```
. as $root

```

preserves original context.


---

## 9\. Ancestor Slicing: Upward Traversal

A path:


```
["departments",0,"teams",1,"members",0,"skills",0]

```

Parent:


```
$p[0:-1]

```

Grandparent:


```
$p[0:-2]

```

General:


```
$p[0:-n]

```

This is structural upward movement.


---

## 10\. Structural Rewrite with reduce + setpath

### Add remote:true to members with skill "rust"

```jq


. as $root
| reduce ( paths as $p | select(getpath($root | $p) == "rust")
| ($p[0:-2]) ) as $member ($root; setpath($member + ["remote"]; true) )


```

Semantics:


```
Generator finds paths to "rust"
Moves up two levels
Reduce accumulates updated root
Each iteration returns new root

```

Purely functional.
Each setpath returns new structure.


---

## 11\. getpath and setpath — Deep Semantics (Expanded)

**Core idea:**
A path in jq is not traversal.
It is data describing traversal.
`getpath` interprets that data.
`setpath` constructs a new structure using that data.

---

### 1\. What Is a Path?

A path is an array of segments.
Each segment is either:

- **String** → object key
- **Number** → array index

Example JSON:

```
{
  "departments": [
    {
      "teams": [
        { "name": "compiler", "members": 5 },
        { "name": "runtime",  "members": 3 }
      ]
    }
  ]
}

```

Path to "runtime":

```
["departments", 0, "teams", 1, "name"]

```

The path is plain data.
It contains no execution.

---

### 2\. Formal Semantics of getpath

```
getpath : (JSON, Path) → JSON

```

Given a current context ".", and a path array:

```
getpath(["a", 0, "b"])

```

jq evaluates:

```
(((.["a"])[0])["b"])

```

Conceptually:

```
function getpath(root, path):
  current = root
  for segment in path:
    current = current[segment]
  return current

```

Important:
`getpath` does not modify structure.
It is pure navigation.

---

### 3\. setpath — Structural Reconstruction

```
setpath(PathArray; Value)

```

```
setpath : (JSON, Path, JSON) → JSON

```

**Key insight:**
jq structures are immutable.
`setpath` does not mutate.
It reconstructs the tree.

If we do:

```
setpath(["a",0,"b"]; 42)

```

jq conceptually performs:

```
function setpath(root, path, value):
  if path is empty:
    return value

  head = path[0]
  tail = path[1:]

  copy = shallow_copy(root)

  copy[head] = setpath(root[head], tail, value)

  return copy

```

So only the nodes along the path are rebuilt.
The rest of the tree is structurally shared.

---

### 4\. getpath vs Direct Access

These are equivalent:

```
.["a"][0]["b"]
getpath(["a",0,"b"])

```

Difference:

- Direct access hardcodes traversal.
- `getpath` makes traversal data-driven.

That enables meta-programming.

---

### 5\. Data ↔ Structure Duality

`paths` turns structure into data:

```
paths

```

produces:

```
Stream<Path>

```

Then:

```
getpath($p)

```

turns data back into structure traversal.

This is a reversible bridge:

```
Structure → Data → Structure

```

---

### 6\. Scoping Is Critical

Both `getpath` and `setpath`
operate relative to the current ".".

Example:

```
. as $root
| paths as $p
| select(getpath($p) == "runtime")

```

After `paths`, "." becomes a path array.
If you do:

```
getpath($p)

```

it will try to interpret the path relative to the path itself —
not the original document.

Correct version:

```
$root | getpath($p)

```

Always remember:

```
getpath and setpath are relative to "."

```

---

### 7\. Structural Rewrite Pattern

Canonical rewrite:

```
. as $root
| reduce (paths as $p | select(...)) as $target
    ($root; setpath($target; NEW_VALUE))

```

Interpretation:

- Find structural coordinates
- Use them to reconstruct a new tree

No mutation.
Only pure structural rebuilding.

---

### 8\. Algebraic View

Think of JSON as a tree.

A path is a coordinate.

`getpath` is coordinate evaluation.

`setpath` is coordinate rewrite.

Together they form a minimal tree algebra.

---

### 9\. Mental Model

```
"." = current root
Path = list of instructions
getpath = interpret instructions
setpath = rebuild tree along instructions

```

Once internalized,
jq stops being a query language.
It becomes programmable tree transformation.

## 12\. Two-Scope Problem

```jq


.value | . as $u | . + { anyAboveMean: ($u.lengths | any(. > $u.meanTitleLen)) }


```

Inside
`any`,
"."
is each element.
Outer "."
would be lost.
So:


```
. as $u

```

captures outer binding.
Lexical closure simulation.


---

## 13\. flatten vs flatten(1)

From your structural wrapper example:


```jq


[[[[ pipeline ]]]] | flatten(1)


```

flatten removes nested arrays.
flatten(1) removes one level only.


Important distinction:


```
flatten is structural
.[0] is positional unwrap

```

---

## 14\. Full Aggregation Pipeline with Scope Isolation

```jq


def mean: add / length;
[[
    del(.[] | .body)
    | map(select(.userId >= 4))
    | reduce .[] as $p ({}; .[$p.userId | tostring]
      |= ( . // {lengths:[], maxn: 0}
    | { lengths: (.lengths + [($p.title | length)]),
        maxn: (if ($p.title | length) > .maxn then ($p.title | length)
               else .maxn end) } ) )
    | map_values( . + { meanTitleLen: (.lengths | mean),
                        anyLongTitle: (.lengths | any(. > 50)),
                        allLongTitles: (.lengths | all(. > 20)) } )
]]
| flatten
| .[0]
| to_entries
| map( .value + { userId: (.key | tonumber) }
        | . as $u
        | . + { anyAboveMean: ($u.lengths | any(. > $u.meanTitleLen)) } )
| sort_by(.maxn)
| reverse
| (max_by(.maxn).maxn) as $gmax
| map(. + { globalMax: $gmax })
| .[:3]


```

Observe:


- Wrapper arrays force delayed evaluation.

- flatten resolves structural staging.

- .\[0\] unwraps single layer.

- reverse + .\[:3\] implements top-N.

- Global aggregate captured with
   `as`.


---

## 15\. Mental Model Summary

```
"." = current context
map(f) = rebind "." to element
any/all = rebind "." to element
reduce = two separate scopes
paths = "." becomes path array
as $x = lexical capture
reverse = array reorder
.[:n] = structural slice
[0:-n] = ancestor slicing
walk = bottom-up recursive transform
add = fold over array (waits for structure)

```

---

## Closing

jq is:


- A streaming calculus

- A fold algebra

- A tree rewriting system

- A scoped evaluation machine


Once you internalize:


```
Rebinding of "."
Structural vs Stream
Generator vs Update scope
Upward vs downward traversal

```

You no longer “write jq”.
You derive jq.


---

# Part II — Formal Semantics, Category Theory, and Execution Visualization

## 17\. A Formal Evaluation Model

Let’s define jq more formally.


A jq filter is a function:


```
F : JSON → Stream(JSON)

```

A stream is an ordered (possibly empty) sequence of values.


Composition:


```
(a | b)(x) = flatten( map(b, a(x)) )

```

This is Kleisli composition for the list monad.


jq is literally programming in the Kleisli category of lists.


---

## 18\. Evaluation Diagram for Pipe Composition

Consider:


```jq


.[] | .title | length


```

Formal evaluation:


```
Input: [Post]
Step 1: .[] : [Post] → Stream<Post>
Step 2: .title : Stream<Post> → Stream<String>
Step 3: length : Stream<String> → Stream<Number>

```

Graphically:


```
Input Array
│ .[]
│ Stream<Post>
│ .title
│ Stream<String>
│ length
│ Stream<Number>

```

Important:
Each stage consumes a stream and produces a stream.


---

## 19\. Reduce as a Fold (Catamorphism)

reduce is a fold.


```
reduce GEN as $x (init; update)

```

Equivalent to:


```
foldl update init (GEN(input))

```

Where:


- GEN : JSON → Stream<a>

- update : accumulator × a → accumulator


This is a left fold.


---

## 20\. Monoids in jq

Many jq operations are monoidal.


- `add`
   over numbers → (+, 0)

- `add`
   over arrays → (concat, \[\])

- `add`
   over objects → (merge, {})

- `any`
   → (OR, false)

- `all`
   → (AND, true)


Monoid structure:


```
(identity, associative combine)

```

Example:


```jq


[true, false, true] | any


```

Equivalent to:


```
false OR true OR false OR true

```

Monoidal reduction.


---

## 21\. map as Functor

map(f) obeys functor laws:


```
map(id) = id
map(f ∘ g) = map(f) ∘ map(g)

```

Because:


```
map(f) = collect(.[] | f)

```

It preserves structure.


Contrast:


```
.[] destroys structure (becomes stream)
map preserves structure (returns array)

```

So arrays form a functor.


---

## 22\. walk as a Recursive Algebra

walk(f) is a bottom-up traversal.


Category-theoretically, this is a catamorphism over the JSON tree.


Example:


```jq


walk( if type == "string" then ascii_upcase else . end )


```

Evaluation:


```
Traverse children
Apply f to children results
Reconstruct parent

```

This is a structural fold.


---

## 23\. Tree Algebra Model

JSON is an algebraic data type:


```
JSON = Null | Boolean | Number | String | Array [JSON] | Object {String: JSON}

```

paths transforms structure into data:


```
Tree → Stream < Path >

```

getpath interprets data as structure traversal:


```
(Path, Tree) → Value

```

setpath constructs new structure:


```
(Path, Value, Tree) → Tree

```

Thus jq allows:


```
Structure ↔ Data

```

This is meta-programming over trees.


---

## 24\. Generator vs Update Scope Diagram

Consider:


```jq


reduce .[] as $x (0; . + $x)


```

Execution model:


```
GEN context: "." = each element of input array
UPDATE context: "." = accumulator
$x = element

```

Diagram:


```
Input Array
│ GEN (.[])
│ Stream<Element>
│ reduce loop:
│ accumulator₀ = 0
│ accumulator₁ = accumulator₀ + element₁
│ accumulator₂ = accumulator₁ + element₂
...

```

Two separate scopes.
Always remember this.


---

## 25\. Execution Visualizer Mental Model

Imagine jq as a machine with:


- A current value register "."

- A stream buffer

- A scope stack for variables

- A structural stack for recursion


When you write:


```
. as $root | paths as $p | ...

```

Machine does:


```
Register "." = input
Push $root
Run paths:
For each path:
Register "." = path
Push $p
Evaluate body

```

Variables are lexical captures.
Not dynamic global references.


---

## 26\. Visualizing Recursion Internally

flatten\_tree recursion:


```
Call stack:
flatten_tree([1,[2,[3,4]],5])
flatten_tree(1)
flatten_tree([2,[3,4]])
flatten_tree(2)
flatten_tree([3,4])
flatten_tree(3)
flatten_tree(4)

```

Return stack:


```
3 + 4 = 7
2 + 7 = 9
1 + 9 + 5 = 15

```

map builds array before add.
add reduces array.


So:


```
Recursion builds structure.
Reduction collapses structure.

```

---

## 27\. Slices and Ordering as Algebra

reverse:


```
reverse : [a] → [a]

```

Pure permutation.


Slicing:


```
.[:n]
.[m:n]
.[-n:]

```

These are structural projections.
Not stream operators.


Ancestor slicing in paths:


```
$p[0:-1]
$p[0:-2]

```

Is path projection.


---

## 28\. jq as Kleisli Category Programming

Because every filter returns a stream,
jq operates in:


```
Kleisli(List)

```

Composition:


```
f >=> g

```

Which is:


```
x ↦ flatten(map(g, f(x)))

```

That is literally jq's pipe.


---

## 29\. Final Unified Model

jq combines:


- Functor (map)

- Fold (reduce, add, any, all)

- Monoid (aggregation)

- Catamorphism (walk)

- Kleisli composition (\|)

- Tree algebra (paths, getpath, setpath)

- Lexical scoping (as)


It is not a scripting language.
It is a small algebra over streams and trees.


---

## Closing Reflection

When something breaks in jq:


- You misunderstood what "." is.

- You confused stream with array.

- You crossed generator scope with update scope.

- You forgot to capture context with as.

- You attempted structural operation on a stream.


Once those invariants are internalized,
jq becomes derivable, not memorized.


It stops being syntax.
It becomes algebra.