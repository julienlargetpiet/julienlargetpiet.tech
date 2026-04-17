In Go (since **Go 1.20**), `errors.Join` lets you **combine multiple errors into a single error** while still preserving each individual error inside it.

This is especially useful when:

- multiple operations can fail independently
- you want to return _all_ errors, not just the first one

---

## 🧠 Basic idea

```go


err := errors.Join(err1, err2, err3)


```

- Returns `nil` if all inputs are `nil`
- Automatically ignores `nil` errors
- The resulting error **wraps all the non-nil ones**

---

## ✅ Simple example

```go


package main

import (
	"errors"
	"fmt"
)

func main() {
	err1 := errors.New("file not found")
	err2 := errors.New("permission denied")

	joined := errors.Join(err1, err2)

	fmt.Println(joined)
}


```

### Output:

```text


file not found
permission denied


```

---

## 🔍 Checking errors with `errors.Is`

This is where `errors.Join` becomes powerful:

```go


package main

import (
	"errors"
	"fmt"
)

var ErrNotFound = errors.New("not found")

func main() {
	err1 := ErrNotFound
	err2 := errors.New("something else")

	joined := errors.Join(err1, err2)

	fmt.Println(errors.Is(joined, ErrNotFound)) // true
}


```

👉 `errors.Is` works across all joined errors.

---

## 🔎 Extracting errors kind with `errors.As`

```go


package main

import (
	"errors"
	"fmt"
)

type MyError struct {
	msg string
}

func (e MyError) Error() string {
	return e.msg
}

func main() {
	err1 := MyError{"custom error"}
	err2 := errors.New("other error")

	joined := errors.Join(err1, err2)

	var target MyError
	if errors.As(joined, &target) {
		fmt.Println("Found MyError:", target.msg)
	}
}


```

---

## 🧪 Real-world pattern: collecting multiple errors

```go


func validate() error {
	var errs []error

	if err := checkName(); err != nil {
		errs = append(errs, err)
	}
	if err := checkEmail(); err != nil {
		errs = append(errs, err)
	}
	if err := checkAge(); err != nil {
		errs = append(errs, err)
	}

	return errors.Join(errs...)
}


```

👉 Instead of failing fast, you return _everything wrong at once_.

---

## ⚠️ Important behaviors

### 1\. `nil` handling

```go


errors.Join(nil, nil) // => nil


```

### 2\. Single error

```go


errors.Join(err) // still works, returns wrapped err


```

### 3\. Formatting

By default:

```go


fmt.Println(joined)


```

prints each error on a new line.

---

## 🧬 Under the hood (important insight)

The value returned by `errors.Join` is not a simple wrapper — it implements a **multi-error unwrapping interface**:

```go


interface {
    Unwrap() []error
}


```

This is different from the usual wrapping pattern:

```go


interface {
    Unwrap() error
}


```

👉 Classic wrapping ( `fmt.Errorf("%w", err)`) creates a **chain** (linked list of errors)

👉 `errors.Join` creates a **tree (or graph)** of errors

---

### 🔗 Chain vs 🌳 Tree

#### Standard wrapping (chain)

```go


err3 := fmt.Errorf("level 3: %w", err2)
err2 := fmt.Errorf("level 2: %w", err1)
err1 := errors.New("root error")


```

Structure:

```text


err3 → err2 → err1


```

Each error unwraps to **one** child.

---

#### `errors.Join` (tree)

```go


err := errors.Join(err1, err2, err3)


```

Structure:

```text


        err
      /  |  \
   err1 err2 err3


```

Each error unwraps to **multiple children**.

---

### 🔍 How `errors.Is` works internally

When you call:

```go


errors.Is(err, target)


```

Go does roughly:

1. Check `err == target`
2. If not, call `Unwrap()`
3. If:
   - `Unwrap() error` → continue down the chain
   - `Unwrap() []error` → recursively explore **all branches**

👉 This means `errors.Is` performs a **depth-first traversal** of the error tree.

---

### 🧪 Example: traversal in action

```go


package main

import (
	"errors"
	"fmt"
)

var ErrA = errors.New("A")
var ErrB = errors.New("B")
var ErrC = errors.New("C")

func main() {
	joined := errors.Join(
		ErrA,
		errors.Join(ErrB, ErrC),
	)

	fmt.Println(errors.Is(joined, ErrC)) // true
}


```

Structure:

```text


        joined
       /      \
    ErrA     (join)
             /   \
          ErrB  ErrC


```

👉 `errors.Is` finds `ErrC` even though it's nested.

## 🔍 Traversal with `fmt.Errorf` (chain example)

To understand the difference clearly, let’s look at how traversal works with **classic wrapping**:

```go


package main

import (
	"errors"
	"fmt"
)

var ErrRoot = errors.New("root")

func main() {
	err := fmt.Errorf("level 3: %w",
		fmt.Errorf("level 2: %w",
			fmt.Errorf("level 1: %w", ErrRoot),
		),
	)

	fmt.Println(errors.Is(err, ErrRoot)) // true
}


```

Structure:

```text


err
 ↓
level 2
 ↓
level 1
 ↓
ErrRoot


```

👉 Here, `errors.Is` walks **linearly down the chain**:

- check level 3
- unwrap → level 2
- unwrap → level 1
- unwrap → ErrRoot ✅

---

### ⚖️ Key difference in traversal



| Feature | fmt.Errorf("%w") | errors.Join |
| --- | --- | --- |
| Structure | Chain (linked list) | Tree / graph |
| Unwrap signature | <code>Unwrap() error</code> | <code>Unwrap() []error</code> |
| Traversal | Linear | Depth-first search |
| Use case | Causality | Aggregation |




---

### 🔎 `errors.As` works the same way

```go


var target *MyError
errors.As(err, &target)


```

👉 It also traverses the entire tree until it finds a matching type.

---

### ⚠️ Important implications

#### 1\. Order does NOT matter

```go


errors.Join(err1, err2)
errors.Join(err2, err1)


```

👉 Both behave the same for `Is` / `As`

---

#### 2\. No short-circuit guarantees

Even if the first error matches, Go may still explore others internally.

👉 Don’t rely on evaluation order.

---

#### 3\. Can create deep trees

```go


err := errors.Join(
	errors.Join(err1, err2),
	errors.Join(err3, err4),
)


```

👉 This builds a **tree of trees**, and Go will traverse all of it.

---

### 🧠 Mental model

Think of `errors.Join` as:

> “This operation failed for **multiple independent reasons**”

Not:

> “This error happened because of another error”

That distinction is key:

- `fmt.Errorf("%w")` → **causality**
- `errors.Join(...)` → **aggregation**

---

### 🚀 Why this design is powerful

Because Go extended the error model from:

- **linear chains** → to → **general trees**

Without breaking compatibility.

👉 Old code still works

👉 New code can express richer failure states

---

### 💡 Bonus: inspect manually

You can type-assert and inspect the tree:

```go


if u, ok := err.(interface{ Unwrap() []error }); ok {
	for _, e := range u.Unwrap() {
		fmt.Println("child:", e)
	}
}


```

---

👉 This is the core reason `errors.Join` feels “magical”:

it upgrades Go’s error model from a **linked list → to a traversable graph**

---

## 💡 When to use `errors.Join`

Use it when:

- validating input (multiple fields)
- batch processing (multiple failures)
- cleanup operations (multiple resources failing to close)

Avoid it when:

- only one error matters (simpler code is better)

---

## 🚀 Pro tip

If you want structured error handling, combine it with sentinel errors:

```go


var ErrInvalidEmail = errors.New("invalid email")
var ErrInvalidName  = errors.New("invalid name")


```

Then you can still do:

```go


if errors.Is(err, ErrInvalidEmail) {
    // handle specifically
}


```